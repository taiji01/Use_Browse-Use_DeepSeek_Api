from langchain_ollama import ChatOllama
from browser_use import Agent
from pydantic import SecretStr


# Initialize the model
llm=ChatOllama(model="qwen2:0.5b", num_ctx=32000)

# Create agent with the model
agent = Agent(
    task="你是什么？",
    llm=llm
)
