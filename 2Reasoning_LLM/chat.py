import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["AZURE_ENDPOINT"].rstrip("/") + "/",
    api_key=os.environ["AZURE_KEY"],
)

response = client.chat.completions.create(
    model=os.getenv("AZURE_MODEL", "gpt-4.1-mini"),  # nombre del despliegue
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is deeplearning?"},
    ],
)

print("Response:", response.choices[0].message.content)
