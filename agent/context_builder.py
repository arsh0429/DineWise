"""Context builder for RAG-augmented prompts"""

class ContextBuilder:
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def build_context(self, query: str, neighborhood: str = None, exclude_ids: list = None) -> str:
        """Build restaurant context for LLM prompt"""
        results = self.vector_store.search(query, n_results=8, neighborhood=neighborhood)
        
        if not results:
            return ""
        
        # Filter excluded restaurants
        if exclude_ids:
            results = [r for r in results if r["id"] not in exclude_ids]
        
        results = results[:5]  # Top 5 after filtering
        
        if not results:
            return ""
        
        context = "## Available Restaurants\n\n"
        for i, r in enumerate(results, 1):
            m = r["metadata"]
            context += f"""**{i}. {m['name']}** - {m['neighborhood']}
- Cuisines: {m['cuisines']}
- Price: {m['price_range']} | Rating: ⭐ {m['rating']}
- Available: {m['available_slots']}
- Ambiance: {m['ambiance']}

"""
        return context
