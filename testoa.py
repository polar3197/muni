from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI()

response = client.chat.completions.create(
    model="gpt-5-nano",
    messages=[
        {"role": "system", "content": "You are a SFMTA MUNI assistant. You respond casually and concisely."},
        {"role": "user", "content": "Hi there partner"}
    ],
    max_completion_tokens=500
)

print(response.choices[0].message.content)
