from groq import Groq
import os
from dotenv import load_dotenv
from tools.calculator import calculator
from tools.search import search_tool

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODEL = "llama-3.1-8b-instant"

messages = []

# -------------------------
# Tool Registry
# -------------------------
tools = {
    "CALCULATE": calculator,
    "SEARCH": search_tool
}


def run_agent(user_input):

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
CALCULATE= 55 * 6

Wrong:
User: What is 55 * 6?
CALCULATE= 330


2. Search

Use Search whenever:
- current information is needed
- current date or time is needed
- the answer may have changed over time
- the question contains a year
- the question asks about current leaders
- the question asks about latest updates
- the answer requires internet knowledge
- if llm doesn't know the answer but it seems like something that can be searched

Examples:

User: Who is the Chief Minister of Kerala in 2026?
SEARCH= Chief Minister of Kerala 2026

User: Latest AI news
SEARCH= latest AI news

User: Current Prime Minister of India
SEARCH= current Prime Minister of India

If you decide to use a tool,
respond ONLY with the tool call.

Do not explain.
Do not add extra text.
Do not add data which llm had returned if a tool needs to be used.

Correct:
SEARCH= latest AI news

Wrong:
Here is some information...SEARCH= latest AI news

Do not try to use the same tool multiple times in a single user input.

Correct: SEARCH= kochi vs thodupuzha tourism

Wrong:
SEARCH= kochi vs thodupuzha tourism\nSEARCH= kochi vs thodupuzha economy\nSEARCH= population of kochi and thodupuzha

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
    
    response = client.chat.completions.create(
    model=MODEL,
    messages=[system_message] + messages
    )
    assistant_content = response.choices[0].message.content
    assistant_message = {"role": "assistant", "content": assistant_content}

    # -------------------------
    # Generic Tool Parser
    # -------------------------
    if "=" in assistant_content:

        tool_name = assistant_content.split("=", 1)[0].strip()
        tool_input = assistant_content.split("=", 1)[1].strip()

        print("\nMODEL DECISION:")
        print(repr(assistant_content))

        if tool_name in tools:

            # ==================================
            # CALCULATOR
            # ==================================
            if tool_name == "CALCULATE":

                try:

                    result = tools[tool_name](tool_input)

                    tool_response = f"The answer is {result}"

                    messages.append(
                        {
                            "role": "assistant",
                            "content": tool_response
                        }
                    )
                    return tool_response

                except Exception as e:

                    error_message = (
                        f"Failed to calculate: {e}"
                    )

                    messages.append(
                        {
                            "role": "assistant",
                            "content": error_message
                        }
                    )

                    return error_message

            # ==================================
            # SEARCH
            # ==================================
            elif tool_name == "SEARCH":

                try:

                    results = tools[tool_name](tool_input)

                    search_context = ""

                    for result in results:

                        search_context += f"""
                        Title: {result['title']}
                        Body: {result['body']}
                        URL: {result['href']}

                        """

                    final_response = client.chat.completions.create(
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

                    final_answer = final_response.choices[0].message.content
                    messages.append(
                        {
                            "role": "assistant",
                            "content": final_answer
                        }
                    )

                    return final_answer

                except Exception as e:

                    error_message = (
                        f"Search failed: {e}"
                    )

                    messages.append(
                        {
                            "role": "assistant",
                            "content": error_message
                        }
                    )

                    return error_message

    else:

        messages.append(assistant_message)

        return assistant_content