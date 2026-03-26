"""ChromaDB vector store for restaurant semantic search"""
import chromadb
from chromadb.utils import embedding_functions
from data.models import Restaurant, get_session

class VectorStore:
    def __init__(self, persist_dir="data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="restaurants",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"}
        )
    
    def index_restaurants(self):
        """Index all restaurants from database"""
        session = get_session()
        restaurants = session.query(Restaurant).all()
        
        documents, metadatas, ids = [], [], []
        
        for r in restaurants:
            # Create rich text for embedding
            doc = f"{r.name}. {', '.join(r.cuisines)} cuisine in {r.neighborhood}, Bangalore. {r.description} Price: {r.price_range}. Rating: {r.rating}. Ambiance: {', '.join(r.ambiance)}."
            
            documents.append(doc)
            metadatas.append({
                "id": r.id,
                "name": r.name,
                "neighborhood": r.neighborhood,
                "cuisines": ", ".join(r.cuisines),
                "price_range": r.price_range,
                "rating": r.rating,
                "available_slots": ", ".join(r.available_slots),
                "amenities": ", ".join(r.amenities),
                "ambiance": ", ".join(r.ambiance)
            })
            ids.append(r.id)
        
        # Upsert to handle re-indexing
        self.collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
        print(f"✅ Indexed {len(restaurants)} restaurants in vector store")
        session.close()
    
    def search(self, query: str, n_results: int = 5, neighborhood: str = None) -> list[dict]:
        """Semantic search with optional neighborhood filter"""
        where_filter = {"neighborhood": neighborhood} if neighborhood else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_filter,
            include=["documents", "metadatas", "distances"]
        )
        
        if not results["ids"][0]:
            return []
        
        return [
            {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i]
            }
            for i in range(len(results["ids"][0]))
        ]

if __name__ == "__main__":
    # Index restaurants
    store = VectorStore()
    store.index_restaurants()
    
    # Test search
    results = store.search("romantic Italian dinner")
    for r in results:
        print(f"- {r['metadata']['name']} ({r['score']:.0%})")
