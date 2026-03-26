"""One-time setup: create DB, seed restaurants, index in vector store"""
from data.models import init_db
from data.seed import generate_restaurants
from rag.vector_store import VectorStore

def setup():
    print("🚀 Setting up DineWise...")
    
    # 1. Create database tables
    print("\n📦 Creating database...")
    init_db()
    
    # 2. Generate restaurants (every cuisine × every neighborhood)
    print("\n🍽️ Generating restaurants...")
    generate_restaurants()
    
    # 3. Index in vector store
    print("\n🔍 Indexing for semantic search...")
    store = VectorStore()
    store.index_restaurants()
    
    print("\n✅ Setup complete! Run: streamlit run app.py")

if __name__ == "__main__":
    setup()
