import anthropic
import os

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# --- Step 1: Define the actual Python function the tool will call ---
def lookup_company_tier(company_name, headcount):
    """Same logic as your Clay tier-scoring formula from Day 11, just in Python."""
    if headcount > 200:
        return f"{company_name} is Enterprise tier."
    elif headcount > 20:
        return f"{company_name} is Mid-Market tier."
    else:
        return f"{company_name} is SMB tier."


# --- Step 2: Describe that tool to Claude, so it knows it exists and when to use it ---
tools = [
    {
        "name": "lookup_company_tier",
        "description": "Determine a company's sales tier (Enterprise, Mid-Market, or SMB) based on its employee headcount.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "The name of the company"
                },
                "headcount": {
                    "type": "integer",
                    "description": "Number of employees at the company"
                }
            },
            "required": ["company_name", "headcount"]
        }
    }
]

# --- Step 3: Send a message that should naturally prompt Claude to use the tool ---
message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "What tier is Acme Freight Co, they have 45 employees?"}
    ]
)

print("Claude's response:")
print(message.content)

# --- Step 4: If Claude decided to call the tool, actually run it and show the result ---
for block in message.content:
    if block.type == "tool_use":
        print("\nClaude decided to call the tool with these inputs:")
        print(block.input)

        result = lookup_company_tier(
            block.input["company_name"],
            block.input["headcount"]
        )
        print("\nActual function result:")
        print(result)