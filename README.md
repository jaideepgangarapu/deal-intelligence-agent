# Elephant: Never Forgets What the CFO Said

An AI-powered sales assistant that uses **Hindsight memory** and **Groq** to remember customer interactions, recall important deal information, and turn it into sales intelligence: risks, stakeholders, deal changes, and next actions.

## Problem

Sales teams handle many customer conversations across different stages of a deal. Important information is spread across meetings, calls, emails, and discussions with different stakeholders, which makes it hard to quickly remember:

- Customer objections
- Pricing concerns
- Competitor considerations
- Stakeholder requirements
- Implementation expectations
- Security or approval requirements

A salesperson may need to review previous conversations manually before deciding how to approach the next interaction.

## Solution

The Deal Intelligence Agent is a memory-powered assistant for sales teams.

The salesperson records customer interactions as they happen, and they are stored in Hindsight memory. Later, the salesperson asks a question or runs an analysis. Hindsight recalls the relevant memories, and Groq uses that context to produce a clear, grounded result.

The agent does not depend only on the current conversation. It uses information retained from earlier customer interactions to give deal-specific context.

```text
Remember -> Recall -> Analyze -> Detect Risks -> Understand Stakeholders -> Track Deal Changes -> Recommend Action
```

## Features

### Core features
- Store customer interactions in Hindsight memory
- Recall relevant information from previous deal interactions
- Generate deal-specific answers using Groq
- Combine information from multiple customer stakeholders
- Support questions about pricing, integration, implementation, and security concerns
- Keep customer context available across separate interactions
- Simple command-line interface for sales teams

### New intelligence features

1. **Deal Risk Radar**
   Finds risks and blockers in recalled memories: pricing objections, technical/integration concerns, security or legal approvals, procurement problems, deadlines, missing approvals, and other unresolved blockers. Each risk gets a **High / Medium / Low** level, a short reason, a status (Open / Addressed), and evidence quoted from memory. Risks without supporting memory are never shown.

2. **Stakeholder Relationship Map**
   Builds a structured map of everyone involved in the deal: name, role/department, concerns, requirements, objections, requests, approval responsibility, and whether they are blocking the deal. Missing details show `Not stated`. Supports questions such as "Who has pricing concerns?" or "Who is blocking the deal?"

3. **Deal Timeline & Change Detector**
   Builds a chronological timeline showing new objections, new requirements, pricing changes, new stakeholders, deadline changes, resolved concerns, and newly unresolved concerns. It uses recorded interaction order and timestamps and never invents dates. Supports questions such as "What changed since the first interaction?"

4. **Next Best Action**
   Reads the risks, stakeholders, and changes, then recommends what the salesperson should do next and drafts a follow-up message. The draft only mentions facts found in memory and does not promise terms that were never agreed.

5. **Multi-Deal Memory Isolation**
   Each customer gets its own Hindsight memory bank (for example `deal-technova`, `deal-infosys`). Analyzing one deal never uses another deal's memories.

## How It Works

1. The salesperson selects or creates a deal.
2. The salesperson enters a customer interaction, which is tagged with its order and time and stored in that deal's Hindsight bank.
3. The salesperson asks a question or runs Risk Radar, Stakeholder Map, Timeline, or Next Best Action.
4. Several targeted recall queries run against the deal's memory bank and the results are merged.
5. The recalled memories are sent to Groq with a task-specific prompt that requires JSON output with quoted evidence.
6. The application checks every item's evidence against the recalled memories and removes unsupported items.
7. The result is displayed to the salesperson.

## Grounding and Safety Against Invented Information

- Groq runs at temperature 0 and must answer with JSON.
- Every risk, stakeholder, event, and action must include evidence quoted from memory.
- Evidence is verified in code. Items whose quotes are not found in the recalled memories are dropped, and the number removed is shown.
- Anything not stated in memory is shown as `Not stated`.
- A concern is only marked "Addressed" if a later interaction explicitly says so.
- If no memories exist for a deal, the agent says so instead of guessing.

## Technologies Used

- Python 3.14
- Hindsight Memory / Hindsight Cloud
- Groq API
- hindsight-client
- groq
- python-dotenv

## Project Structure

```text
deal-intelligence-agent/
|-- agent.py              # CLI menu (original options + new options)
|-- core.py               # per-deal memory banks, recall, analysis engine, evidence validation
|-- prompts.py            # prompts and JSON formats for the four analysis modes
|-- test_hindsight.py
|-- requirements.txt
|-- README.md
|-- deals.json            # created automatically: deal names and interaction counters
|-- screenshot-menu.png
|-- screenshot-memory1.png
|-- screenshot-memory1.1.png
|-- screenshot-answer.png
|-- .gitignore
|-- .env
`-- .venv/
```

## Hindsight Memory

Hindsight is the core memory component of the application.

- **Retain:** when the salesperson enters a customer interaction, it is stored in the deal's Hindsight memory bank, tagged with an interaction number and recorded time.
- **Recall:** when a question is asked or an analysis is run, Hindsight searches the stored memories and returns what is relevant. The Risk Radar, Stakeholder Map, Timeline, and Next Best Action each run several recall queries (pricing, security, integration, deadlines, approvals, and so on) and merge the results so fewer details are missed.

The recalled memories are then provided to Groq so it can respond using the customer's previous context.

## Architecture

```text
Salesperson (CLI)
       |
       v
Select deal -> Customer interaction
       |
       v
Hindsight Memory (one bank per deal)
       |
       |  Multi-query recall, merged
       v
Groq LLM (mode-specific prompt, JSON output)
       |
       v
Evidence validation (unsupported items removed)
       |
       v
Risk Radar | Stakeholder Map | Timeline | Next Best Action
```

## Data Flow

1. The salesperson selects a deal (option 4).
2. A customer interaction is entered (option 9).
3. The interaction is tagged, for example `[Interaction #3 | recorded 2026-09-28 14:30]`, and sent to that deal's Hindsight bank.
4. The salesperson later runs an analysis or asks a question.
5. The application sends several recall queries to Hindsight.
6. Hindsight returns relevant memories, which are merged and de-duplicated.
7. The memories and the salesperson's question are sent to Groq with the mode-specific prompt.
8. Groq returns JSON with evidence for each item.
9. The application removes any item whose evidence is not found in the memories.
10. The result is displayed.

## Menu

```text
1. Add customer interaction          (original)
2. Ask about a deal                  (original)
3. Exit                              (original)
4. Select / create deal
5. Deal Risk Radar
6. Stakeholder Map
7. Deal Timeline & Changes
8. Next Best Action
9. Add interaction to selected deal
```

Options 1 and 2 use the original shared memory bank. Options 4 to 9 use a separate bank per deal.

## Example: Memory-Based Learning

Suppose a salesperson records these interactions with TechNova Inc. (option 9):

1. The CTO is concerned about integration with the existing system.
2. The CFO considers the pricing too high and requests a 10% discount.
3. Procurement wants the solution deployed within four weeks.
4. Legal requires a security review before approving the deal.

Later, the salesperson asks (option 2 or 6):

```text
What are the main concerns from the CTO, CFO, Procurement, and Legal teams?
```

## Example Output Formats

The examples below show the layout of each result. Actual wording depends on the stored memories.

### Deal Risk Radar (option 5)

```text
=========== DEAL RISK RADAR ===========

[HIGH] Security/Legal: Security review pending
    Why: Legal will not approve until the review is complete.
    Status: Open
    Evidence: "Legal requires a security review before approving the deal"

[MEDIUM] Pricing: Discount request
    Why: CFO objection with no resolution recorded.
    Status: Open
    Evidence: "The CFO considers the pricing too high and requests a 10% discount"
```

### Stakeholder Map (option 6)

```text
[1] Not stated | CFO
    ----------------------------------------------------------------------
    Concerns                | Pricing is too high
    Requests                | 10% discount
    Approval responsibility | Not stated
    Blocking the deal?      | Not stated
```

### Deal Timeline (option 7)

```text
Interaction #1  [Technical concern]
    The CTO is concerned about integration with the existing system.

Interaction #4  [Security/Legal]
    Legal requires a security review before approving the deal.
```

### Next Best Action (option 8)

```text
1. Address the pricing objection with the CFO
    Who: CFO
    Why: The discount request has no recorded resolution.

--- Draft follow-up message ---
To: CFO
Subject: Follow-up on pricing
...
```

## Running the Application

### 1. Clone the repository

```bash
git clone https://github.com/jaideepgangarapu/deal-intelligence-agent.git
cd deal-intelligence-agent
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your API keys

Create a `.env` file in the project folder:

```text
HINDSIGHT_BASE_URL=your_hindsight_url
HINDSIGHT_API_KEY=your_hindsight_key
GROQ_API_KEY=your_groq_key
```

### 5. Run the agent

```bash
python agent.py
```

## Demo: Memory Changes the Outcome

1. Option 4: create `TechNova Inc.`
2. Option 9: add the four interactions above.
3. Option 5 and option 8: the CFO pricing risk is shown as open, and the recommended action addresses it.
4. Option 9: add "CFO approved a 7% discount."
5. Option 5 and option 8 again: the pricing risk is shown as addressed and the recommendation changes.
6. Option 4: create `Infosys` and run option 5. No TechNova information appears.
7. Close and reopen the app, then run option 5 again to show that the memories persist.

## Security

API keys are stored in the local `.env` file and are not committed to GitHub.

The `.gitignore` file excludes:

```text
.env
.venv/
__pycache__/
```

`deals.json` only contains deal names and interaction counts. Add it to `.gitignore` if you prefer not to publish customer names.

## Limitations

- The timeline is only as precise as the recorded order and timestamps. If Hindsight rewrites stored text and drops the interaction tags, the timeline shows "Order not recorded" instead of guessing.
- Memories entered with the original option 1 live in the shared bank and are not visible to options 5 to 8. Re-enter them with option 9.
- Evidence checking confirms that quoted text exists in the recalled memories. It does not guarantee that the interpretation of that text is always correct, so the salesperson should review the results.

## Future Improvements

- Web-based dashboard for sales teams (for example with Streamlit)
- Deal-stage tracking
- Automatic interaction summaries
- Draft messages in regional languages
- Authentication and user-specific memory
- Analytics to show how deal context changes over time

## Project Goal

The goal of this project is to build a practical sales assistant that uses persistent memory to help salespeople understand customer deals more effectively.

Instead of treating every question as a new conversation, the agent uses relevant information from previous customer interactions to provide context-aware answers, spot risks, understand stakeholders, track how the deal is changing, and recommend the next step.