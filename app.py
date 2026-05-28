from ollama import chat

# Conversation memory
messages = []


# Calculator tool
def calculator(expression):
    return eval(expression)


while True:

    user_input = input("You: ")

    # Exit condition
    if user_input.lower() in ["exit", "end"]:
        print("Goodbye!")
        break

    # TOOL ROUTING
    # Very primitive agent logic
    if any(op in user_input for op in ["+", "-", "*", "/"]):

        try:
            result = calculator(user_input)

            print("Tool Result:", result)

            continue

        except Exception:
            print("Invalid math expression")
            continue

    # Store user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Normal LLM chat
    response = chat(
        model="llama3.2:1b",
        messages=messages
    )

    assistant_message = response["message"]

    print("AI:", assistant_message["content"])

    messages.append(assistant_message)