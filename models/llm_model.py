from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GROQ_API_KEY")

if not key:
    raise ValueError("GROQ_API_KEY is not set in the environment.")


def llm_for_agent():
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.4,
        api_key=key,
        max_tokens=800,
        reasoning_effort="none",
    )
    return llm
