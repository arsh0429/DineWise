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

## Docker Deployment
```bash
docker build -t dinewise .
docker run -p 8501:8501 -e OLLAMA_BASE_URL=http://host.docker.internal:11434/v1 dinewise
```
> Note: Ollama must be running on the host machine.

## Logging
All interactions are logged to `logs/dinewise.log`:
```
2026-03-27 01:15:00 | INFO | USER: Find Italian restaurants in Koramangala
2026-03-27 01:15:01 | INFO | TOOL CALL: search_restaurants({"query": "Italian Koramangala"})
2026-03-27 01:15:01 | INFO | TOOL RESULT: [{"name": "La Piazza Kor", "cuisines": ["Italian"]...}]
2026-03-27 01:15:03 | INFO | RESPONSE: Here's a great Italian spot in Koramangala...
```

## Limitations & Future Improvements

### Current Limitations
- **Synthetic data only** — 120 restaurants are generated, not scraped from real sources
- **No user authentication** — anyone can cancel any reservation with a booking ID
- **Single-session memory** — conversation history resets when the browser tab closes
- **Local LLM constraints** — Qwen 3:8B occasionally truncates responses or misparses tool arguments
- **No concurrent booking protection** — race conditions possible under simultaneous requests
- **Date parsing** — small models struggle with natural language dates ("next Sunday")

### Future Improvements
- [ ] **Real restaurant data** via Zomato/Swiggy API integration
- [ ] **User authentication** with session-based booking history
- [ ] **Database-level locking** for concurrent reservation safety
- [ ] **Evaluation pipeline** — automated testing of 50+ sample queries to measure search accuracy
- [ ] **Data drift monitoring** — track search relevance degradation over time
- [ ] **Kubernetes deployment** with horizontal scaling
- [ ] **Persistent conversation memory** using Redis or database-backed sessions
- [ ] **Feedback loop** — users rate recommendations to improve search ranking
