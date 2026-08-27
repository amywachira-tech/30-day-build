import anthropic
import json

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=300,
    messages=[{
        "role": "user",
        "content": """Tell me something about Jordan Kim.

Prospect: Jordan Kim, Nova Energy, a renewable energy company exploring data infrastructure upgrades."""
    }]
)

raw_text = response.content[0].text
print("Raw response:", raw_text)

try:
    parsed = json.loads(raw_text)
    print("Fit score:", parsed["fit_score"])
    print("Reasoning:", parsed["reasoning"])
except json.JSONDecodeError:
    print("Model didn't return valid JSON. Raw response was:")
    print(raw_text)