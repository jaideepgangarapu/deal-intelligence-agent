# Elephant: Never Forgets What the CFO Said

An AI-powered sales assistant that uses Hindsight memory and Groq to remember customer interactions, recall important deal context, and turn scattered conversation history into actionable deal intelligence.

## Overview

This project was originally a Python CLI tool and is now a polished hackathon-ready web application. The app helps sales teams keep track of customer concerns, stakeholders, changes in the deal, risk signals, and next actions without relying on memory alone.

## Problem Statement

Sales teams often lose valuable context because customer information is spread across calls, emails, and meetings. Important details like pricing objections, integration blockers, security requirements, stakeholder concerns, and deadline changes are easy to forget.

Without that historical context, sales conversations become inconsistent and opportunities move slower than they should.

## Our Solution

The Deal Intelligence Agent stores each interaction in a deal-specific memory bank, retrieves the most relevant recall from previous conversations, and uses Groq to generate grounded analysis. The system surfaces:

- Deal risk radar
- Stakeholder relationship map
- Timeline of deal changes
- Recommended next action
- Memory-backed AI answers

The existing Python logic remains the real engine. The new frontend simply makes it easier to interact with that functionality in a clean product experience.

## Key Features

- Deal-specific Hindsight memory banks
- AI-generated deal summaries grounded in prior context
- Risk radar for pricing, security, technical, procurement, and approval issues
- Stakeholder tracking for roles, concerns, and decision-makers
- Timeline of changes and unresolved blockers
- Next-best-action recommendations and planning support
- Web dashboard with a polished UI for demos

## Why It Matters

This project turns fragmented deal history into usable, trusted intelligence. Instead of forcing a salesperson to manually review old notes, the app memory-remembers what matters and brings it back when it is most useful.

## How It Works

1. A deal is selected or created in the web dashboard.
2. The user adds an interaction for that deal.
3. Hindsight stores the memory with the interaction metadata.
4. Groq and the existing deal-analysis logic recall the relevant context.
5. The system validates evidence against the stored memories.
6. The dashboard shows risks, stakeholders, changes, and recommendations.

## Architecture

```text
User
  |
  v
Web dashboard (Flask)
  |
  v
Python deal engine (core.py)
  |
  +--> Hindsight memory for each deal
  |
  +--> Groq analysis for grounded AI output
  |
  +--> Evidence validation against remembered facts
  |
  v
UI output (risk, stakeholders, timeline, next best action)
```

## Groq Integration

Groq is used where it adds real value: generating grounded analysis based on recalled customer memories. The app keeps the API key in `.env` and never hardcodes secrets. The project uses the official Groq Python client and a temperature of 0 for more deterministic results.

## Hindsight Integration

Hindsight is the memory layer that enables the system to remember earlier customer interactions and retrieve relevant context later. Each deal has isolated memory storage, which prevents cross-deal contamination and makes the experience much more realistic for sales workflows.

## Technology Stack

- Python 3.14
- Flask
- Hindsight Memory / Hindsight Cloud
- Groq API
- HTML, CSS, and Jinja templates
- Python-dotenv
- pytest

## Project Structure

```text
deal-intelligence-agent/
├── app.py                 # Flask web app and dashboard routes
├── core.py                # Existing deal-memory + analysis engine
├── prompts.py             # AI prompt definitions for the analysis modes
├── agent.py               # Original CLI entry point preserved
├── test_hindsight.py      # Original Hindsight test example
├── tests/
│   └── test_app.py        # App smoke test
├── templates/
│   ├── index.html         # Landing page
│   └── dashboard.html     # Deal dashboard and analysis panels
├── static/
│   └── styles.css         # Professional hackathon UI styling
├── deals.json             # Created automatically for deal metadata
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── .env                   # Local environment file (not committed)
├── screenshots...
└── .venv/
```

## Prerequisites

- Python 3.12+
- Git
- A Hindsight API key
- A Groq API key

## Installation

```bash
git clone <your-repo-url>
cd deal-intelligence-agent
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
HINDSIGHT_BASE_URL=https://api.hindsight.vectorize.io
HINDSIGHT_API_KEY=your_hindsight_key
GROQ_API_KEY=your_groq_key
SECRET_KEY=choose_a_secure_value
```

## Running Locally

```bash
python app.py
```

Then open:

```text
http://localhost:5000
```

The landing page shows the product overview, and the dashboard is available at:

```text
http://localhost:5000/dashboard
```

## Testing

```bash
python -m pytest -q
```

## Deployment

The repository includes a Render Blueprint in `render.yaml`. To deploy:

1. Push the project to the `main` branch on GitHub.
2. In Render, choose **New > Blueprint** and connect `jaideepgangarapu/deal-intelligence-agent`.
3. During the initial Blueprint setup, enter `HINDSIGHT_BASE_URL`, `HINDSIGHT_API_KEY`, and `GROQ_API_KEY`. Render generates `SECRET_KEY`.
4. Create the Blueprint and wait for the `/health` check to pass.
5. Open the `onrender.com` URL shown for the service.

The service uses Render's free web plan. Local `.env` and `deals.json` files are intentionally excluded from Git; the deployed app will not contain the local deal list. Create the deal again in the hosted dashboard to access its Hindsight bank. The Blueprint does not provision paid persistent storage, so local deal metadata may reset when the service restarts or redeploys. Hindsight remains the persistent memory store.

Never commit `.env` or enter API keys in GitHub. Add secret values only through Render's protected environment-variable setup.

## GitHub Repository

This project is already versioned in Git. For a standard workflow:

```bash
git status
git add .
git commit -m "Build hackathon web application"
git push
```

## Live Demo

Live app: https://deal-intelligence-agent-ao7t.onrender.com

Dashboard: https://deal-intelligence-agent-ao7t.onrender.com/dashboard

## Hackathon Demo Flow

1. Open the dashboard.
2. Create or select a deal.
3. Add a customer interaction.
4. Ask the AI for a summary or run Deal Risk Radar.
5. Review the Hindsight-backed insights.
6. Use the stakeholder and timeline views to explain the deal story.
7. Show how the app can carry context between customer conversations.

## Team

Built for a hackathon as a memory-powered sales intelligence application.

## License

This project is currently distributed without a formal license file. Add one if you plan to open-source it publicly.

## Original CLI Behavior

The project still preserves the original Python functionality from the earlier version. The CLI file remains available as `agent.py`, while the web app becomes the polished product demo layer.

## Beginner-Friendly Local Setup

### Step 1: Clone the repository

```bash
git clone <your-repo-url>
cd deal-intelligence-agent
```

### Step 2: Open the project in VS Code

Open the folder in VS Code and make sure the terminal is pointed at the project root.

### Step 3: Create a virtual environment

```bash
python -m venv .venv
```

### Step 4: Activate it on Windows

```bash
.venv\Scripts\activate
```

### Step 5: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 6: Create `.env`

```bash
copy .env.example .env
```

### Step 7: Add Groq credentials

Add your Groq key to `.env`.

### Step 8: Add Hindsight credentials

Add your Hindsight API key and base URL to `.env`.

### Step 9: Run the app

```bash
python app.py
```

### Step 10: Open the local website

```text
http://localhost:5000
```

The app will show the landing page and the dashboard for interacting with the deal memory system.

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