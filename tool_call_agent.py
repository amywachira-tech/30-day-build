import anthropic
import os
import json

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# --- Step 1: Define the actual Python functions the tools will call ---
def lookup_company_tier(company_name, headcount):
    """Same logic as the Clay tier-scoring formula, in Python."""
    if headcount > 200:
        return f"{company_name} is Enterprise tier."
    elif headcount > 20:
        return f"{company_name} is Mid-Market tier."
    else:
        return f"{company_name} is SMB tier."


def check_recent_signal(company_name):
    """Stub: pretend this checks Clay-style enrichment for a recent signal."""
    return f"{company_name} had a recent funding round announced 2 months ago."


# A lookup table so the loop can call the right Python function by name,
# instead of writing a new if/elif chain every time you add a tool.
available_functions = {
    "lookup_company_tier": lookup_company_tier,
    "check_recent_signal": check_recent_signal,
}

# --- Step 2: Describe both tools to Claude ---
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
    },
    {
        "name": "check_recent_signal",
        "description": "Check whether a company has a recent notable signal, such as funding or a leadership hire, that would affect prioritization.",
        "input_schema": {
            "type": "object",
            "properties": {
                "company_name": {
                    "type": "string",
                    "description": "The name of the company"
                }
            },
            "required": ["company_name"]
        }
    }
]

# --- Step 3: Start the conversation ---
# This now lives in a list, because the loop appends to it as messages go back and forth.
messages = [
    {"role": "user", "content": "Is Acme Freight Co worth a deeper look? They have 8 employees."}
]
# --- Step 4: The agent loop ---
# Keep calling Claude until it responds with no more tool_use blocks, only text.
while True:
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=tools,
        messages=messages
    )

    # Add Claude's response to the conversation history before doing anything else.
    messages.append({"role": "assistant", "content": response.content})

    # Check if Claude wants to call any tools.
    tool_calls = [block for block in response.content if block.type == "tool_use"]

    if not tool_calls:
        # No more tool calls. Claude gave a final answer. Print it and stop.
        final_text = "".join(
            block.text for block in response.content if block.type == "text"
        )
        print("\nFinal answer:")
        print(final_text)
        break

    # Otherwise, run every requested tool call and collect the results.
    tool_results = []
    for call in tool_calls:
        print(f"\nClaude called {call.name} with inputs: {call.input}")
        function_to_run = available_functions[call.name]
        result = function_to_run(**call.input)
        print(f"Result: {result}")

        tool_results.append({
            "type": "tool_result",
            "tool_use_id": call.id,
            "content": result
        })

    # Send the results back as a new user message, then loop again.
    messages.append({"role": "user", "content": tool_results})