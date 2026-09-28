import os
from dotenv import load_dotenv
from hindsight_client import Hindsight
from groq import Groq

import core  # NEW: multi-deal banks + analysis features

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


# ---------------------------------------------------------------
# NEW: helpers for multi-deal selection and the analysis features
# ---------------------------------------------------------------
current = {"slug": None}  # the deal selected with option 4


def choose_deal():
    deals = core.load_deals()

    if deals:
        print("\nExisting deals:")
        for d in deals.values():
            print(f"- {d['name']} ({d['count']} interactions)")

    name = input(
        "\nEnter deal/customer name (new names create a new deal): "
    ).strip()

    if not name:
        print("Deal name cannot be empty.")
        return None

    current["slug"] = core.select_deal(name)

    print(
        f"Selected deal: {core.deal_name(current['slug'])}"
    )

    return current["slug"]


def ensure_deal():
    return current["slug"] or choose_deal()


# Main application
while True:

    print("\n================================")
    print("   DEAL INTELLIGENCE AGENT")
    print("================================")
    print("1. Add customer interaction")
    print("2. Ask about a deal")
    print("3. Exit")
    print("4. Select / create deal")
    print("5. Deal Risk Radar")
    print("6. Stakeholder Map")
    print("7. Deal Timeline & Changes")
    print("8. Next Best Action")
    print("9. Add interaction to selected deal")

    if current["slug"]:
        print(
            f"\n[Selected deal: "
            f"{core.deal_name(current['slug'])}]"
        )

    choice = input("\nChoose an option: ")

    # Option 1: Add memory
    if choice == "1":

        customer = input(
            "\nEnter customer/company name: "
        )

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

    # Option 4: Select / create a deal
    elif choice == "4":
        choose_deal()

    # Options 5-8: analysis features
    elif choice in ("5", "6", "7", "8"):

        slug = ensure_deal()

        if slug:

            mode = {
                "5": "risk",
                "6": "stakeholder",
                "7": "timeline",
                "8": "next"
            }[choice]

            question = None

            if mode in ("stakeholder", "timeline"):
                question = input(
                    "\nOptional question "
                    "(press Enter for the full view): "
                ).strip() or None

            try:
                print("\nAnalyzing deal memories...")

                data = core.analyze(
                    mode,
                    slug,
                    question
                )

                core.show(
                    mode,
                    data
                )

            except Exception as e:
                print(
                    f"\nCould not complete the analysis: {e}"
                )

    # Option 9: add a tagged interaction
    # to the selected deal's bank
    elif choice == "9":

        slug = ensure_deal()

        if slug:

            interaction = input(
                "\nEnter the customer interaction: "
            ).strip()

            if interaction:

                try:
                    n = core.retain_interaction(
                        slug,
                        interaction
                    )

                    print(
                        f"Interaction #{n} remembered for "
                        f"{core.deal_name(slug)}."
                    )

                except Exception as e:

                    print(
                        f"Could not store the interaction: {e}"
                    )

    # Invalid option
    else:
        print(
            "Invalid choice. Please select 1-9."
        )


# Close Hindsight connection
hindsight.close()
core.close()

print("\nDeal Intelligence Agent closed.")