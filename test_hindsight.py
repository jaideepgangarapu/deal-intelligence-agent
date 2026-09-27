import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

load_dotenv()

# Hindsight
hindsight = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

# Groq
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 1. Ask Hindsight for relevant memories
results = hindsight.recall(
    bank_id="deal-intelligence-agent",
    query="What should I know before my next call with Acme Corp?"
)

# 2. Convert memories into text
memories = "\n".join(result.text for result in results.results)

# 3. Give those memories to the LLM
prompt = f"""
You are a Deal Intelligence Agent.

Use the following information remembered from previous interactions:

{memories}

Answer this salesperson's question:

What should I know before my next call with Acme Corp?

Give a concise summary of:
- Customer concerns
- Competitors
- Timeline
- Stakeholder concerns
"""

response = groq.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": prompt}
    ]
)

print("\nDeal Intelligence Summary:\n")
print(response.choices[0].message.content)