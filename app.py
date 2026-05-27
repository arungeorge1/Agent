from ollama import chat

messages = []

while True:

    # Get user input
    user_input = input("You: ")

    # Exit condition
    if (user_input.lower() == "exit") or (user_input.lower() == "end"):
        print("Goodbye!")
        break

    # Store user message
    messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Send full conversation to model
    response = chat(
        model="llama3.2:1b",
        messages=messages
    )

    # Extract assistant reply
    assistant_message = response["message"]

    # Print assistant response
    print("AI:", assistant_message["content"])

    # Store assistant reply in memory
    messages.append(assistant_message)