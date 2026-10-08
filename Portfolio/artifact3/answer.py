"""
answer.py
Answers an agent's question from the corpus, or says "Ask a lead".

Pipeline (requirements doc, section 7):
  1. Filtered search (search.py): only chunks the role may see.
  2. Similarity floor: nothing relevant -> Ask a lead, no Claude call.
  3. Claude reports what each retrieved source says, with exact quotes.
  4. Code checks every quote appears word for word in its chunk.
  5. Code applies the conflict rule (section 5). Claude never decides
     which source is more authoritative.

Run:
    python answer.py agent "cust bought sofa on sale 5 wks ago wants return, ok?"
"""

import json
import re
import sys
from datetime import date
from pathlib import Path

import anthropic

from search import search

MODEL = "claude-sonnet-5-5"   # use the same model string as call_scorer.py
TOP_K = 6
SIM_FLOOR = 0.45              # set from dev questions D1-D4; see write-up
FLAG_LOG = Path("flags_log.jsonl")

ASK_LEAD = "ASK_LEAD"
ANSWER = "ANSWER"
ANSWER_WITH_FLAG = "ANSWER_WITH_FLAG"

PROMPT = """You help the customer support team at Kestrel Home, a home-goods retailer.
A support {role} asked this question while on a call with a customer:

<question>{question}</question>

Below are passages retrieved from internal policy sources. Each has an id.

{passages}

Your job is to report what the passages say. You do not decide which source is
more authoritative or more current; other code does that.

Rules:
- Use only the passages. Never use outside knowledge.
- For every passage that directly answers the question, add one entry to
  "positions": its id, one sentence copied EXACTLY from that passage that
  supports the answer, the answer that passage gives (one or two sentences,
  written for the person asking), and a "group" letter.
- Positions that give the same or compatible answers share a group letter
  ("A"). A position that contradicts them gets a different letter ("B").
- A passage that covers only a narrower case (for example one item type) does
  not contradict a general rule. If the question does not say whether the
  narrower case applies, mention the condition in its answer and keep it in
  the same group.
- Ignore passages that are on the topic but do not answer the question.
- "answer" is your overall answer for the person asking, addressed to them
  as a {role}, using only group A positions
  if there is no contradiction. Leave it empty if positions contradict.
- If no passage answers the question, set "status" to "not_answerable" and
  leave "positions" empty.

Return only JSON, with no other text:
{{"status": "answerable" or "not_answerable",
  "answer": "...",
  "positions": [{{"chunk_id": "...", "quote": "...", "answer": "...", "group": "A"}}]}}"""


# ---------- helpers ----------

def normalize(text):
    """Remove markdown bold and collapse whitespace, for quote matching."""
    text = text.replace("**", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def strip_fences(text):
    """Claude sometimes wraps JSON in ```json fences even when told not to."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text


def format_passages(results):
    blocks = []
    for _, c in results:
        body = c["text"].split("\n\n", 1)[-1]
        blocks.append(f'<passage id="{c["chunk_id"]}" source="{c["source_name"]}">\n'
                      f"{body}\n</passage>")
    return "\n\n".join(blocks)


def citation(chunk):
    eff = chunk.get("effective_date")
    when = f"effective {eff}" if eff else "effective date not stated"
    return f'{chunk["source_name"]} ({chunk["source_type"]}, {when})'


def ask_lead(reason, results=None):
    return {"outcome": ASK_LEAD, "answer": None, "citation": None,
            "source_id": None,
            "flags": [], "reason": reason,
            "retrieved": [c["chunk_id"] for _, c in (results or [])]}


def call_claude(question, results, role):
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4000,  # room for the model's thinking plus the JSON
        messages=[{"role": "user", "content": PROMPT.format(
            question=question, role=role,
            passages=format_passages(results))}],
    )
    # The response can start with a thinking block. Keep only the text blocks.
    return "".join(b.text for b in msg.content if b.type == "text")


# ---------- conflict rule (requirements section 5) ----------

def pick_winner(positions):
    """
    positions: list of (position dict, chunk dict), all with verified quotes.
    Returns (winner, None) or (None, reason to ask a lead).
    """
    top_tier = min(c["authority_tier"] for _, c in positions)
    top = [(p, c) for p, c in positions if c["authority_tier"] == top_tier]

    # One source at the top tier, or several that agree with each other.
    if len({p.get("group", "A") for p, _ in top}) == 1:
        return top[0], None

    # Several sources at the top tier.
    all_announcements = all(c["source_type"] == "announcement" for _, c in top)
    owners = {c["owner"] for _, c in top}
    dates = [c.get("effective_date") for _, c in top]
    if all_announcements and len(owners) == 1 and all(dates):
        # Same owner, all dated: the latest effective date wins.
        return max(top, key=lambda pc: pc[1]["effective_date"]), None

    return None, "Sources at the same authority level disagree."


# ---------- main pipeline ----------

def answer(question, role, as_of=None, claude=call_claude):
    as_of = as_of or date.today()
    results = search(question, role, top_k=TOP_K, as_of=as_of)
    retrieved = {c["chunk_id"]: c for _, c in results}

    # Step 2: similarity floor.
    if not results or results[0][0] < SIM_FLOOR:
        return ask_lead("No sufficiently relevant source found.", results)

    # Step 3: Claude reports what each source says.
    raw = claude(question, results, role)
    try:
        data = json.loads(strip_fences(raw))
        positions = data.get("positions", [])
    except (json.JSONDecodeError, AttributeError):
        return ask_lead("Model output could not be read.", results)

    if data.get("status") != "answerable" or not positions:
        return ask_lead("The sources do not answer this question.", results)

    # Step 4: every quote must appear word for word in a retrieved chunk.
    verified = []
    for p in positions:
        chunk = retrieved.get(p.get("chunk_id"))
        if chunk is None:
            return ask_lead(f"Model cited a passage it was not given: "
                            f"{p.get('chunk_id')}", results)
        if normalize(p.get("quote", "")) not in normalize(chunk["text"]):
            return ask_lead(f"Quote could not be verified in "
                            f"{chunk['chunk_id']}.", results)
        verified.append((p, chunk))

    # Step 5: conflict rule, in code.
    groups = {p.get("group", "A") for p, _ in verified}

    if len(groups) == 1:
        # All sources agree. Use the overall answer, cite the most
        # authoritative source.
        best = min(verified, key=lambda pc: pc[1]["authority_tier"])
        text = data.get("answer") or best[0]["answer"]
        return {"outcome": ANSWER, "answer": text, "citation": citation(best[1]),
                "source_id": best[1]["source_id"], "flags": [], "reason": None, "quote": best[0]["quote"],
                "retrieved": list(retrieved)}

    winner, reason = pick_winner(verified)
    if winner is None:
        return ask_lead(reason, results)

    p, c = winner
    win_group = p.get("group", "A")
    # Flag only sources whose answer disagrees with the winner.
    flags = [{"source": citation(oc), "source_id": oc["source_id"],
              "says": op["answer"], "quote": op["quote"]}
             for op, oc in verified if op.get("group", "A") != win_group]
    log_flags(question, c, flags)
    return {"outcome": ANSWER_WITH_FLAG, "answer": p["answer"],
            "citation": citation(c), "source_id": c["source_id"],
            "flags": flags, "reason": None,
            "quote": p["quote"], "retrieved": list(retrieved)}


def log_flags(question, winner, flags):
    """Record outdated sources so leads know which pages to fix."""
    if not flags:
        return
    with FLAG_LOG.open("a", encoding="utf-8") as f:
        for fl in flags:
            f.write(json.dumps({"question": question,
                                "current_source": winner["source_name"],
                                "outdated_source": fl["source"]}) + "\n")


def show(result):
    if result["outcome"] == ASK_LEAD:
        print("ASK A LEAD")
        print(f"  Why: {result['reason']}")
        return
    print(result["answer"])
    print(f"  Source: {result['citation']}")
    print(f'  Quote:  "{result["quote"]}"')
    for fl in result["flags"]:
        # Show the outdated source's own words, not a competing answer.
        print(f"  OUTDATED FOR THIS QUESTION: {fl['source']} still says: "
              f'"{fl["quote"]}" Reported for review.')


def main():
    if len(sys.argv) != 3:
        print('Usage: python answer.py agent "your question"')
        sys.exit(1)
    show(answer(sys.argv[2], sys.argv[1]))


if __name__ == "__main__":
    main()
