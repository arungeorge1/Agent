from ollama import chat

messages = []


# Calculator tool
def calculator(expression):
    return eval(expression)


while True:

    user_input = input("You: ")

    if user_input.lower() in ["exit", "end"]:
        print("Goodbye!")
        break

    # Store user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # SYSTEM PROMPT
    system_message = {
        "role": "system",
        "content": """
You are an AI assistant.

If the user asks a math question,
respond ONLY in this format:

CALCULATE: expression

Example:
CALCULATE: 5 * 8

Do not explain.
Do not add extra text.
"""
    }

    # Send conversation + system prompt
    response = chat(
        model="llama3.2:1b",
        messages=[system_message] + messages
    )

    assistant_message = response["message"]

    assistant_content = assistant_message["content"]

    # TOOL EXECUTION
    if assistant_content.startswith("CALCULATE:"):

        expression = assistant_content.replace("CALCULATE:", "").strip()

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

        except Exception:
            print("AI: Failed to calculate.")

    else:

        print("AI:", assistant_content)

        messages.append(assistant_message)