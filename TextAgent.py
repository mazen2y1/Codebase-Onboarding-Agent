from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import streamlit as st
import os
import json

load_dotenv()

GOOGLE_API_KEY= st.secrets["GOOGLE_API_KEY"]

model = ChatGoogleGenerativeAI(
    model="gemini-3.1-flash-lite",
    temperature=0,
    google_api_key=GOOGLE_API_KEY
)

agent = create_agent(
    model=model,
    system_prompt="""
You are a repository analysis explainer.

Explain the repository analysis clearly and accurately.
Do not invent information that is not present in the analysis.
"""
)


def explain_repository(output_file):

    with open(output_file, "r", encoding="utf-8") as file:
        repo_data = json.load(file)

    result = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": repo_data["analysis"]
            }
        ]
    })

    content = result["messages"][-1].content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        return "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
        )

    return str(content)