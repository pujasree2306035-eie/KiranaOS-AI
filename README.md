# KiranaOS AI

### Autonomous AI Operations Agent for Indian Retail

KiranaOS AI is an AI-powered operations agent designed for small Indian retail stores.

## Live Telegram Bot

Telegram Bot: @KiranaOS_Assistant_bot

The bot allows a shopkeeper to interact using natural language for:

- Inventory management
- Stock receiving
- Multi-item billing
- GST calculation
- Low-stock monitoring
- Khata management
- Daily sales analysis
- PDF invoice generation
- PowerPoint business reports
- Persistent user preferences

## Architecture

Shopkeeper
↓
Telegram
↓
AI Agent / Orchestrator
↓
Reasoning + Context
↓
Business Tools
↓
SQLite Database
↓
Response / PDF / PPTX

## Tech Stack

- Python
- Google Gemini
- Telegram Bot API
- SQLite
- ReportLab
- python-pptx
- Pandas
- Matplotlib

## Project Structure

```text
kiranaos-ai/
├── agent/
├── tools/
├── database/
├── telegram/
├── tests/
├── artifacts/
├── requirements.txt
├── .env.example
└── README.md
