import anthropic
import os
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Six-dimension call-scoring rubric, generalized from real post-call assessment
# structure (not copied from any specific company's proprietary rubric or data).
# Each dimension checks WHEN/HOW something happened, not just WHETHER it happened,
# that distinction is what makes this a judgment-scoring problem instead of a
# keyword-matching problem.

DIMENSIONS = [
    "pitch_intensity_fit",
    "trust_framing_placement",
    "pain_reflected_back",
    "time_discipline",
    "claim_discipline",
    "decision_maker_path",
]

SYSTEM_PROMPT = """You are scoring a B2B sales call transcript against six dimensions.
For each dimension, assign a rating of "strong", "needs_work", or "poor", plus one
sentence of evidence quoted or closely paraphrased from the transcript. Do not just
check whether something was mentioned, judge WHEN and HOW it happened.

Dimensions:

1. pitch_intensity_fit: Did the rep's pitch level (how much they offered/proposed)
   match the qualification actually confirmed on the call, or did they pitch a
   bigger commitment than the evidence supported? A rep who confirms budget and
   authority before proposing a large next step scores strong. A rep who proposes
   a large commitment to someone with no confirmed authority to approve it scores
   poor, even if the pitch itself was well-delivered.

2. trust_framing_placement: Was any risk, security, compliance, or trust-relevant
   framing delivered proactively early in the call, or only reactively after the
   prospect raised a concern? Proactive and early scores strong. Reactive but
   substantive scores needs_work. Never addressed scores poor.

3. pain_reflected_back: When the prospect stated a real pain point, did the rep
   explicitly reflect it back in their own words at some point in the call
   (showing they heard and will use it), or did it just pass by unaddressed?

4. time_discipline: Did the call move toward a close at a reasonable pace, or did
   it drift past its natural point of resolution with no active close attempt,
   leaving the prospect to end the call themselves?

5. claim_discipline: Did the rep make any claims about capabilities, pricing, or
   availability that go beyond what's confirmed as true, without clearly flagging
   uncertainty? Overpromising or vague hedging without disclosure scores poor.

6. decision_maker_path: If the real decision-maker or approver was not on the
   call, is there a concrete, owned next step to reach them (a specific date, a
   named action, someone responsible), or is the gap just acknowledged and left
   unresolved?

Return ONLY valid JSON in this exact format, nothing else, no markdown fences:
{
  "pitch_intensity_fit": {"rating": "strong|needs_work|poor", "evidence": "one sentence"},
  "trust_framing_placement": {"rating": "strong|needs_work|poor", "evidence": "one sentence"},
  "pain_reflected_back": {"rating": "strong|needs_work|poor", "evidence": "one sentence"},
  "time_discipline": {"rating": "strong|needs_work|poor", "evidence": "one sentence"},
  "claim_discipline": {"rating": "strong|needs_work|poor", "evidence": "one sentence"},
  "decision_maker_path": {"rating": "strong|needs_work|poor", "evidence": "one sentence"},
  "overall_call_outcome": "advancing|disqualified|stalled",
  "outcome_reasoning": "one sentence explaining the overall_call_outcome choice"
}
"""


def score_call(transcript_text):
    """Takes a full transcript's raw text, returns a dict of dimension scores."""
    if not transcript_text or not transcript_text.strip():
        return {"error": "Empty transcript, cannot score."}

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": transcript_text}
        ]
    )

    raw_text = message.content[0].text.strip()

    # Same defensive fence-stripping as the Week 5 sentiment classifier.
    # Claude wraps JSON in markdown fences even when told not to, expect this.
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return {"error": f"PARSE_ERROR: could not parse response: {raw_text}"}

    return parsed


def print_scorecard(name, result):
    print("=" * 70)
    print(f"CALL: {name}")
    print("=" * 70)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        return

    for dim in DIMENSIONS:
        if dim in result:
            rating = result[dim].get("rating", "MISSING")
            evidence = result[dim].get("evidence", "")
            print(f"\n{dim.replace('_', ' ').title()}: {rating.upper()}")
            print(f"  Evidence: {evidence}")

    print(f"\nOVERALL OUTCOME: {result.get('overall_call_outcome', 'MISSING').upper()}")
    print(f"  Reasoning: {result.get('outcome_reasoning', '')}")
    print()


if __name__ == "__main__":
    transcripts = {
        "Meridian Sensing (clean close)": "transcript_1_clean_close.txt",
        "Harrow Analytics (clean loss)": "transcript_2_clean_loss.txt",
        "Fenwick Trials (ambiguous stall)": "transcript_3_ambiguous_stall.txt",
        "Solstice Underwriting (adversarial)": "transcript_4_adversarial_CLEAN.txt",
        "Cartwell Logistics (adversarial round 2)": "transcript_5_adversarial2_CLEAN.txt",
    }

    all_results = {}

    for name, filename in transcripts.items():
        with open(filename, "r") as f:
            text = f.read()

        result = score_call(text)
        print_scorecard(name, result)
        all_results[name] = result

    with open("scoring_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nFull results saved to scoring_results.json")