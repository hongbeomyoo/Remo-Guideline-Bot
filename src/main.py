import os
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

llm = OpenAI(api_key=api_key)

question = "hello"
answer = llm.predict(question)

print(f"Q: {question}")
print(f"A: {answer}")
