"""Evaluation script — measures RAG search quality vs SQL baseline"""
import json
import time
from data.models import Restaurant, get_session
from rag.vector_store import VectorStore

# Test cases: (query, neighborhood, expected_cuisine)
TEST_CASES = [
    ("Italian pizza pasta", "Koramangala", "Italian"),
    ("South Indian dosa idli", "Indiranagar", "South Indian"),
    ("Chinese noodles dim sum", "Whitefield", "Chinese"),
    ("Japanese sushi ramen", "HSR Layout", "Japanese"),
    ("Mexican tacos burritos", "MG Road", "Mexican"),
    ("Thai curry pad thai", "Jayanagar", "Thai"),
    ("North Indian tandoori naan", "JP Nagar", "North Indian"),
    ("Mughlai biryani kebab", "Malleshwaram", "Mughlai"),
    ("Continental European steak", "Koramangala", "Continental"),
    ("Coastal seafood fish prawns", "Indiranagar", "Coastal"),
    ("BBQ grilled meat smoky", "Whitefield", "BBQ & Grills"),
    ("Mediterranean hummus falafel", "HSR Layout", "Mediterranean"),
    ("Cafe coffee latte", "MG Road", "Cafe"),
    ("Bakery cake pastry bread", "Jayanagar", "Bakery"),
    ("Pan-Asian fusion bowl", "JP Nagar", "Pan-Asian"),
    ("romantic Italian dinner date", "Koramangala", "Italian"),
    ("casual dosa place", "MG Road", "South Indian"),
    ("cheap Chinese food", "Whitefield", "Chinese"),
    ("premium sushi experience", "Indiranagar", "Japanese"),
    ("family friendly biryani", "Malleshwaram", "Mughlai"),
]


def sql_baseline_search(session, query, neighborhood, expected_cuisine):
    """Simple SQL WHERE clause — the baseline to beat"""
    results = session.query(Restaurant).filter(
        Restaurant.neighborhood == neighborhood,
        Restaurant.cuisines.contains(expected_cuisine)
    ).all()
    return results


def rag_search(vector_store, query, neighborhood):
    """RAG semantic search via ChromaDB"""
    results = vector_store.search(query=query, n_results=5, neighborhood=neighborhood)
    return results


def evaluate():
    session = get_session()
    vs = VectorStore()

    rag_correct = 0
    sql_correct = 0
    rag_times = []
    sql_times = []

    print(f"{'='*70}")
    print(f"  DineWise Search Evaluation — {len(TEST_CASES)} test queries")
    print(f"{'='*70}\n")
    print(f"{'Query':<35} {'Expected':<15} {'RAG':<6} {'SQL':<6}")
    print(f"{'-'*35} {'-'*15} {'-'*6} {'-'*6}")

    for query, neighborhood, expected_cuisine in TEST_CASES:
        # RAG search
        t0 = time.time()
        rag_results = rag_search(vs, query, neighborhood)
        rag_time = time.time() - t0
        rag_times.append(rag_time)

        # Check if top result has correct cuisine
        rag_hit = False
        for r in rag_results[:3]:  # Check top 3
            name = r.get("metadata", {}).get("name", "")
            db_r = session.query(Restaurant).filter(Restaurant.name == name).first()
            if db_r and expected_cuisine in db_r.cuisines:
                rag_hit = True
                break

        # SQL baseline
        t0 = time.time()
        sql_results = sql_baseline_search(session, query, neighborhood, expected_cuisine)
        sql_time = time.time() - t0
        sql_times.append(sql_time)

        sql_hit = len(sql_results) > 0

        if rag_hit:
            rag_correct += 1
        if sql_hit:
            sql_correct += 1

        rag_icon = "✅" if rag_hit else "❌"
        sql_icon = "✅" if sql_hit else "❌"
        short_query = query[:33] + ".." if len(query) > 35 else query
        print(f"{short_query:<35} {expected_cuisine:<15} {rag_icon:<6} {sql_icon:<6}")

    # Summary
    rag_accuracy = (rag_correct / len(TEST_CASES)) * 100
    sql_accuracy = (sql_correct / len(TEST_CASES)) * 100
    avg_rag_time = sum(rag_times) / len(rag_times) * 1000
    avg_sql_time = sum(sql_times) / len(sql_times) * 1000

    print(f"\n{'='*70}")
    print(f"  RESULTS")
    print(f"{'='*70}")
    print(f"  RAG Search:  {rag_correct}/{len(TEST_CASES)} correct ({rag_accuracy:.0f}%) | Avg: {avg_rag_time:.0f}ms")
    print(f"  SQL Baseline: {sql_correct}/{len(TEST_CASES)} correct ({sql_accuracy:.0f}%) | Avg: {avg_sql_time:.0f}ms")
    print(f"{'='*70}")

    if rag_accuracy > sql_accuracy:
        print(f"  ✅ RAG beats SQL baseline by {rag_accuracy - sql_accuracy:.0f}%")
    elif rag_accuracy == sql_accuracy:
        print(f"  ⚖️ RAG matches SQL baseline — consider if the complexity is worth it")
    else:
        print(f"  ⚠️ SQL baseline beats RAG by {sql_accuracy - rag_accuracy:.0f}% — RAG needs improvement")

    # Save metrics for DVC tracking
    metrics = {
        "rag_accuracy": round(rag_accuracy, 1),
        "sql_accuracy": round(sql_accuracy, 1),
        "rag_avg_latency_ms": round(avg_rag_time, 1),
        "sql_avg_latency_ms": round(avg_sql_time, 1),
        "test_count": len(TEST_CASES),
        "rag_correct": rag_correct,
        "sql_correct": sql_correct
    }
    with open("metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\n  📊 Metrics saved to metrics.json")

    session.close()
    return rag_accuracy, sql_accuracy


if __name__ == "__main__":
    evaluate()
