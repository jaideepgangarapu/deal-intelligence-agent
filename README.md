# Deal Intelligence Agent

An AI-powered sales assistant that uses Hindsight memory and Groq to remember customer interactions, recall important deal information, and provide sales intelligence over time.

## Problem

Sales teams often handle many customer conversations across different stages of a deal.

Important information can be spread across meetings, calls, emails, and discussions with different stakeholders. This makes it difficult for a salesperson to quickly remember:

- Customer objections
- Pricing concerns
- Competitor considerations
- Stakeholder requirements
- Implementation expectations
- Security or approval requirements

A salesperson may need to review previous conversations manually before deciding how to approach the next interaction.

The Deal Intelligence Agent solves this problem by giving the salesperson a memory-powered assistant that can retain customer interactions, recall relevant information later, and use that context to answer questions about the deal.

## Solution

The Deal Intelligence Agent acts as a memory-powered assistant for sales teams.

The salesperson can record customer interactions as they happen. These interactions are stored in Hindsight memory.

Later, the salesperson can ask a question about the deal. Hindsight recalls relevant information from previous interactions, and the recalled memories are provided to Groq.

Groq uses this context to generate a clear answer for the salesperson.

The key idea is that the agent does not depend only on the current conversation. It can use information retained from earlier customer interactions to provide deal-specific context.

## Features
- Store customer interactions in Hindsight memory
- Recall relevant information from previous deal interactions
- Generate deal-specific answers using Groq
- Combine information from multiple customer stakeholders
- Support questions about pricing, integration, implementation, and security concerns
- Keep customer context available across separate interactions
- Provide a simple command-line interface for sales teams
## How It Works

The application follows a simple memory-based workflow:

1. The salesperson enters a customer interaction.
2. The interaction is stored in Hindsight.
3. The salesperson asks a question about the deal.
4. Hindsight recalls relevant memories.
5. The recalled memories are sent to Groq.
6. Groq generates a useful answer for the salesperson.

This allows the agent to use information from earlier interactions instead of relying only on the latest question.

## Technologies Used
- Python 3.14
- Hindsight Memory
- Hindsight Cloud
- Groq API
- hindsight-client
- groq
- python-dotenv

## Project Structure

```text
deal-intelligence-agent/
|-- agent.py
|-- test_hindsight.py
|-- requirements.txt
|-- README.md
|-- screenshot-menu.png
|-- screenshot-memory1.png
|-- screenshot-memory1.1.png
|-- screenshot-answer.png
|-- .gitignore
|-- .env
`-- .venv/


## Hindsight Memory

Hindsight is the core memory component of the application.

The agent uses Hindsight in two important ways:

### Retain

When the salesperson enters a customer interaction, the interaction is stored in the Hindsight memory bank.

### Recall

When the salesperson asks a question, Hindsight searches the stored customer memories and returns information relevant to that question.

The recalled memories are then provided to Groq so the language model can generate an answer using the customer's previous context.

This makes memory a central part of the agent rather than simply using an LLM for a single question-and-answer interaction.

## Architecture

The system has three main components:

1. **Salesperson Interface**
   - Accepts customer interactions.
   - Accepts questions about a deal.

2. **Hindsight Memory**
   - Stores customer interactions.
   - Recalls relevant memories when a question is asked.

3. **Groq LLM**
   - Receives the recalled memories.
   - Generates a useful answer for the salesperson.

### Flow

```text
Salesperson
     |
     v
Customer Interaction
     |
     v
Hindsight Memory
     |
     |  Recall relevant memories
     v
Groq LLM
     |
     v
Deal Intelligence Answer

## Data Flow

The application follows this data flow:

1. Customer interaction is entered by the salesperson.
2. The interaction is sent to Hindsight using the Hindsight client.
3. Hindsight stores the interaction in the Deal Intelligence Agent memory bank.
4. The salesperson later asks a question about the customer or deal.
5. The application sends the question to Hindsight for recall.
6. Hindsight returns relevant memories.
7. The application combines the recalled memories with the salesperson's question.
8. The combined context is sent to Groq.
9. Groq generates the final deal intelligence answer.
10. The answer is displayed to the salesperson.

## Example Memory-Based Learning

## Example Memory-Based Learning

Suppose a salesperson records these interactions with TechNova Inc.:

1. The CTO is concerned about integration with the existing system.
2. The CFO considers the pricing too high and requests a 10% discount.
3. Procurement wants the solution deployed within four weeks.
4. Legal requires a security review before approving the deal.

Later, the salesperson asks:

```text
What are the main concerns from the CTO, CFO, Procurement, and Legal teams?```text

## Running the Application

## Running the Application

### 1. Clone the repository

```bash
git clone https://github.com/jaideepgangarapu/deal-intelligence-agent.git
cd deal-intelligence-agent```bash

## Security

API keys are stored in the local `.env` file and are not committed to GitHub.

The `.gitignore` file excludes:

```text
.env
.venv/
__pycache__/
```text

## Future Improvements

- Add a web-based dashboard for sales teams
- Support multiple deals and customers
- Add deal-stage tracking
- Add automatic interaction summaries
- Add follow-up recommendations based on previous deal history
- Add authentication and user-specific memory
- Add analytics to show how deal context changes over time

## Project Goal

The goal of this project is to build a practical sales assistant that uses persistent memory to help salespeople understand customer deals more effectively.

Instead of treating every question as a new conversation, the agent can use relevant information from previous customer interactions to provide context-aware answers.


