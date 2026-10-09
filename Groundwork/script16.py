import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=200,
    messages=[{"role": "user", "content": "Summarize what a Founding AE role typically involves, in 2 sentences."}]
)

print(response.content[0].text)