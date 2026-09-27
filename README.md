# Deal Intelligence Agent

An AI-powered sales assistant that uses Hindsight memory and Groq to remember customer interactions, recall important deal information, and provide sales intelligence over time.

## Problem

Sales teams often interact with the same customer many times during a deal.

Important information can be spread across different conversations, such as:

- Customer objections
- Pricing concerns
- Competitors
- Stakeholder concerns
- Implementation requirements
- Deal timelines

The Deal Intelligence Agent stores these interactions in Hindsight and recalls relevant information when a salesperson asks a question.

## Solution

The agent combines:

- Hindsight - persistent memory for customer and deal information
- Groq - generates useful answers from the recalled memories
- Python - connects the memory and AI components into an interactive application

## Features

- Store customer interactions in Hindsight memory
- Recall relevant information from previous interactions
- Maintain stakeholder-specific deal information
- Ask natural-language questions about a customer or deal
- Generate AI-powered answers using Groq
- Combine information from multiple past interactions
- Interactive command-line menu
- Cleanly close the Hindsight connection

## How It Works

1. The salesperson enters a customer interaction.
2. The interaction is stored in Hindsight.
3. The salesperson asks a question about the deal.
4. Hindsight recalls relevant memories.
5. The recalled memories are sent to Groq.
6. Groq generates a useful answer for the salesperson.

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
  agent.py
  test_hindsight.py
  requirements.txt
  README.md
  .env
  .gitignore
  .venv/