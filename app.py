from ollama import chat

user_input = input("You: ")

response = chat(
    model="llama3.2:1b",
    messages=[
        {
            "role": "user",
            "content": user_input
        }
    ]
)

print("AI:", response["message"]["content"])