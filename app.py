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

Use only for arithmetic calculations.

Respond EXACTLY in this format:

CALCULATE: expression

Example:
CALCULATE: 5 * 8


2. Search

Use Search whenever:
- current information is needed
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

    # =====================================================
    # CALCULATOR TOOL
    # =====================================================
    if assistant_content.startswith("CALCULATE:"):

        expression = assistant_content.replace(
            "CALCULATE:",
            ""
        ).strip()

        try:

            result = calculator(expression)

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

    # =====================================================
    # SEARCH TOOL
    # =====================================================
    elif assistant_content.startswith("SEARCH:"):

        query = assistant_content.replace(
            "SEARCH:",
            ""
        ).strip()

        print("Searching:", query)

        try:

            results = search_tool(query)

            search_context = ""

            for result in results:

                search_context += f"""
Title: {result['title']}
Body: {result['body']}
URL: {result['href']}

"""

            # -----------------------------------
            # Second LLM Call
            # -----------------------------------
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

    # =====================================================
    # NORMAL CHAT
    # =====================================================
    else:

        print("AI:", assistant_content)

        messages.append(assistant_message)