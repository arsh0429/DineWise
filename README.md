# 🍽️ DineWise - Restaurant Reservation System

AI-powered restaurant reservation assistant for Bangalore, built with RAG + Tool Calling. Runs **100% locally** — no cloud APIs needed.

## Quick Start

### 1. Install Ollama & pull the model
```bash
# Install Ollama from https://ollama.com
ollama pull qwen3:8b
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize the database
```bash
python setup.py
```

### 4. Run the app
```bash
streamlit run app.py
```

## Architecture

```
User → Streamlit → Orchestrator → LLM (Qwen 3:8B via Ollama) → Tool Calls → Database
                       ↑
                   RAG Context (ChromaDB + MiniLM embeddings)
```

## Features
- 🔍 Semantic restaurant search across 120 Bangalore restaurants (15 cuisines × 8 neighborhoods)
- 📍 8 neighborhoods: Koramangala, Indiranagar, Whitefield, HSR Layout, MG Road, Jayanagar, JP Nagar, Malleshwaram
- 🍕 15 cuisines: North Indian, South Indian, Chinese, Italian, Continental, Japanese, Thai, Mexican, Mediterranean, Mughlai, Coastal, Cafe, Bakery, Pan-Asian, BBQ & Grills
- 💰 Price ranges in ₹ (₹200-400 to ₹1200+)
- 🪑 Per-slot seat capacity tracking with real-time availability
- 📝 Reservation confirmations with booking receipts
- 📱 Phone number validation (10 digits)
- 🧠 RAG-grounded responses with cuisine relevance filtering
- 🔄 Multi-turn conversation with intent-first approach

## Tech Stack
- **LLM**: Qwen 3:8B via Ollama (local, no API key needed)
- **RAG**: ChromaDB + all-MiniLM-L6-v2 sentence embeddings
- **Backend**: SQLAlchemy + SQLite
- **Frontend**: Streamlit (dark theme)
- **No LangChain** — built from scratch with OpenAI-compatible API

## How It Works
1. User describes what they want (cuisine, area, budget, occasion)
2. LLM gathers preferences through natural conversation (1 question at a time)
3. Semantic search finds relevant restaurants via ChromaDB embeddings
4. LLM filters results by cuisine relevance and presents options
5. User selects a restaurant → LLM guides through booking flow
6. Reservation stored in SQLite with capacity tracking per time slot
