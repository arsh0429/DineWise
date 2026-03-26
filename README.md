# 🍽️ DineWise - Restaurant Reservation System

AI-powered restaurant reservation assistant for Bangalore, built with RAG + Tool Calling.

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up your API key
```bash
cp .env.example .env
# Edit .env and add your Groq API key (free at https://console.groq.com/keys)
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
User → Streamlit → Orchestrator → LLM (Groq) → Tool Calls → Database
                       ↑
                   RAG Context (ChromaDB + MiniLM embeddings)
```

## Features
- 🔍 Semantic restaurant search across 100 Bangalore restaurants
- 📍 8 neighborhoods: Koramangala, Indiranagar, Whitefield, HSR Layout, MG Road, Jayanagar, JP Nagar, Malleshwaram
- 💰 Price ranges in ₹ (₹200-400 to ₹1200+)
- 🕐 Time slot based availability (2-3 slots per restaurant)
- 📝 Reservation confirmations with booking receipts
- 🧠 RAG-grounded responses (no hallucinations)
- 🔄 Conversation memory with smooth re-routing

## Tech Stack
- **LLM**: Llama-3.3-70B via Groq API
- **RAG**: ChromaDB + all-MiniLM-L6-v2
- **Backend**: SQLAlchemy + SQLite
- **Frontend**: Streamlit (dark theme)
- **No LangChain** - built from scratch
