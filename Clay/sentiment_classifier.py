import anthropic
import os
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# The fixed tag set. Keep this list tight, every reply must map to exactly one.
VALID_TAGS = ["interested", "not_interested", "needs_follow_up", "not_relevant"]

SYSTEM_PROMPT = """You are classifying replies to cold sales outreach emails.
Read the reply and assign exactly one tag from this list:

- interested: wants to move forward, asks for more info, requests a call/demo
- not_interested: explicit no, unsubscribe request, or clear rejection
- needs_follow_up: ambiguous, deferred, or conditional (e.g. "maybe later", "check back next quarter")
- not_relevant: auto-reply, wrong person, out of office, spam-adjacent, or unrelated to the outreach

Return ONLY valid JSON in this exact format, nothing else, no markdown fences:
{"tag": "one_of_the_four_tags", "reasoning": "one short sentence"}
"""


def classify_reply(reply_text):
    """Takes a reply's raw text, returns a dict with 'tag' and 'reasoning'."""
    # Guard clause: the API rejects empty content outright, so an empty or
    # whitespace-only reply is handled before it ever reaches the API call.
    if not reply_text or not reply_text.strip():
        return {"tag": "not_relevant", "reasoning": "Empty reply body, handled before API call."}

    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=200,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": reply_text}
        ]
    )

    raw_text = message.content[0].text.strip()

    # Defensive fence-stripping. Claude wraps JSON in markdown code fences
    # even when told not to, this bit us in Week 2, expect it here too.
    if raw_text.startswith("```"):
        raw_text = raw_text.strip("`")
        if raw_text.startswith("json"):
            raw_text = raw_text[4:]
        raw_text = raw_text.strip()

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        # If parsing fails outright, that's itself a data point for the eval,
        # not something to silently swallow.
        return {"tag": "PARSE_ERROR", "reasoning": f"Could not parse: {raw_text}"}

    if parsed.get("tag") not in VALID_TAGS:
        parsed["reasoning"] = f"[INVALID TAG '{parsed.get('tag')}'] " + parsed.get("reasoning", "")
        parsed["tag"] = "INVALID_TAG"

    return parsed


if __name__ == "__main__":
    # Quick manual smoke test before running the full eval set.
    test_reply = "Hey, this looks interesting, can we grab 15 minutes next week?"
    result = classify_reply(test_reply)
    print("Test reply:", test_reply)
    print("Result:", result)