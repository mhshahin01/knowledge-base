"""web.py — serve the agent as a web chat playground.

Run:   uvicorn web:app --reload
Open:  http://127.0.0.1:8000
"""
from agent import agent

# This ONE line turns your agent into a web app with a chat UI:
app = agent.to_web()
