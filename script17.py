import anthropic
import json

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=300,
    messages=[{
        "role": "user",
        "content": """Classify this prospect's fit for an AI-powered analytics tool.
Return ONLY valid JSON in this exact format, no other text:
{"fit_score": <1-5>, "reasoning": "<one sentence>"}

Prospect: Jordan Kim, Nova Energy, a renewable energy company exploring data infrastructure upgrades."""
    }]
)

raw_text = response.content[0].text
print("Raw response:", raw_text)

parsed = json.loads(raw_text)
print("Fit score:", parsed["fit_score"])
print("Reasoning:", parsed["reasoning"])