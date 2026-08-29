"""wrapper-openai.py - the smallest possible OpenAI API call.

Read a line from the user, send it to the model, print what comes back.
No agent, no framework, no tools. This is the layer everything else sits on.

Note the shape of `messages`: the persona is just another entry in the list,
tagged with the "system" role. That list IS the request.

Run:  python wrapper-openai.py
"""
import os

from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI

MODEL = "gpt-5"

INSTRUCTIONS = (
    "You are a concise assistant for a beginner learning to call LLM APIs. "
    "Answer in at most two sentences."
)

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def ask(prompt: str) -> str:
    """Send one system message plus one user message, return the reply text."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    prompt = input("You: ")
    print("AI :", ask(prompt))
