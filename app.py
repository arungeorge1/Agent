from ollama import chat
from ddgs import DDGS

MODEL = "qwen2.5:3b"

messages = []


# -------------------------
# Calculator Tool
# -------------------------
def calculator(expression):
    return eval(expression)


# -------------------------
# Search Tool
# -------------------------
def search_tool(query):

    results = list(
        DDGS().text(
            query,
            max_results=5
        )
    )

    return results


# -------------------------
# Tool Registry
# -------------------------
tools = {
    "CALCULATE": calculator,
    "SEARCH": search_tool
}


while True:

    user_input = input("You: ")

    if user_input.lower() in ["exit", "end"]:
        print("Goodbye!")
        break

    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # -------------------------
    # System Prompt
    # -------------------------
    system_message = {
        "role": "system",
        "content": """
You are an AI assistant.

Available tools:

1. Calculator

Use ONLY for arithmetic calculations.

IMPORTANT:
Do NOT solve the calculation yourself.
Pass the ORIGINAL expression to the calculator.

Correct:
User: What is 55 * 6?
CALCULATE: 55 * 6

Wrong:
User: What is 55 * 6?
CALCULATE: 330


2. Search

Use Search whenever:
- current information is needed
- current date or time is needed
- the answer may have changed over time
- the question contains a year
- the question asks about current leaders
- the question asks about latest updates
- the answer requires internet knowledge

Examples:

User: Who is the Chief Minister of Kerala in 2026?
SEARCH: Chief Minister of Kerala 2026

User: Latest AI news
SEARCH: latest AI news

User: Current Prime Minister of India
SEARCH: current Prime Minister of India


If no tool is required,
answer normally.

Only use these tool names:
CALCULATE
SEARCH

Never invent tool names.
"""
    }

    # -------------------------
    # First LLM Call
    # -------------------------
    response = chat(
        model=MODEL,
        messages=[system_message] + messages
    )

    assistant_message = response["message"]
    assistant_content = assistant_message["content"]

    print("\n[MODEL DECISION]")
    print(assistant_content)
    print()

    # -------------------------
    # Generic Tool Parser
    # -------------------------
    if ":" in assistant_content:

        tool_name = assistant_content.split(":", 1)[0].strip()
        tool_input = assistant_content.split(":", 1)[1].strip()

        if tool_name in tools:

            # ==================================
            # CALCULATOR
            # ==================================
            if tool_name == "CALCULATE":

                try:

                    result = tools[tool_name](tool_input)

                    tool_response = f"The answer is {result}"

                    print("AI:", tool_response)

                    messages.append(
                        {
                            "role": "assistant",
                            "content": tool_response
                        }
                    )

                except Exception as e:

                    print("AI: Failed to calculate.")
                    print("ERROR:", e)

            # ==================================
            # SEARCH
            # ==================================
            elif tool_name == "SEARCH":

                print("Searching:", tool_input)

                try:

                    results = tools[tool_name](tool_input)

                    search_context = ""

                    for result in results:

                        search_context += f"""
Title: {result['title']}
Body: {result['body']}
URL: {result['href']}

"""

                    final_response = chat(
                        model=MODEL,
                        messages=[
                            {
                                "role": "system",
                                "content": f"""
Use the search results below
to answer the user's question.

Search Results:

{search_context}
"""
                            },
                            {
                                "role": "user",
                                "content": user_input
                            }
                        ]
                    )

                    final_answer = final_response["message"]["content"]

                    print("AI:", final_answer)

                    messages.append(
                        {
                            "role": "assistant",
                            "content": final_answer
                        }
                    )

                except Exception as e:

                    print("AI: Search failed.")
                    print("ERROR:", e)

        else:

            print(f"AI: Unknown tool '{tool_name}' requested.")

    else:

        print("AI:", assistant_content)

        messages.append(assistant_message)