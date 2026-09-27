import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

# Load environment variables
load_dotenv()

# Connect to Hindsight
hindsight = Hindsight(
    base_url=os.getenv("HINDSIGHT_BASE_URL"),
    api_key=os.getenv("HINDSIGHT_API_KEY")
)

# Connect to Groq
groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# Hindsight memory bank
BANK_ID = "deal-intelligence-agent"

print("Deal Intelligence Agent initialized!")


# Store customer interaction
def remember(interaction):
    hindsight.retain(
        bank_id=BANK_ID,
        content=interaction
    )
    print("Interaction remembered.")


# Recall memories
def recall(question):
    results = hindsight.recall(
        bank_id=BANK_ID,
        query=question
    )

    print("\nRecalled memories:")
    for result in results:
        print("-", result.text)


# Generate AI answer using recalled memories
def generate_answer(question):
    results = hindsight.recall(
        bank_id=BANK_ID,
        query=question
    )

    memories = "\n".join(result.text for result in results)
    print("\nHindsight recalled:")
    for result in results:
     print("-", result.text)

    response = groq.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a sales deal intelligence assistant. "
                    "Use the provided customer memories to answer "
                    "the salesperson's question clearly. "
                    "Focus only on information supported by the memories."
                )
            },
            {
                "role": "user",
                "content": f"""
Customer memories:
{memories}

Salesperson's question:
{question}
"""
            }
        ]
    )

    print("\nAgent answer:")
    print(response.choices[0].message.content)


# Main application
while True:

    print("\n================================")
    print("   DEAL INTELLIGENCE AGENT")
    print("================================")
    print("1. Add customer interaction")
    print("2. Ask about a deal")
    print("3. Exit")

    choice = input("\nChoose an option: ")

    # Option 1: Add memory
    if choice == "1":

        customer = input("\nEnter customer/company name: ")

        interaction = input(
            "Enter the customer interaction: "
        )

        memory = f"""
Customer: {customer}
Interaction: {interaction}
"""

        remember(memory)

    # Option 2: Ask question
    elif choice == "2":

        customer = input(
            "\nEnter customer/company name: "
        )

        question = input(
            "Ask about the deal: "
        )

        full_question = f"""
Customer: {customer}

Question: {question}
"""

        generate_answer(full_question)

    # Option 3: Exit
    elif choice == "3":
        break

    # Invalid option
    else:
        print(
            "Invalid choice. Please select 1, 2, or 3."
        )


# Close Hindsight connection
hindsight.close()

print("\nDeal Intelligence Agent closed.")