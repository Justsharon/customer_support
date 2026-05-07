import os
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

from state import CustomerSupportState

# Confidence threshold for retrieved chunks
DISTANCE_THRESHOLD = 1.5

# Build the policy collection (cached at module load)
def _build_policy_collection() -> chromadb.Collection:
    """Load all policy files into a ChromaDB collection (persistent)"""
    
    # Use persistent storage
    db_path = Path(__file__).parent.parent / "chroma_db"
    client = chromadb.PersistentClient(path=str(db_path))

    # Check if collection already exists, otherwise create
    try:
        collection = client.get_collection("policies")
        if collection.count() > 0:
            return collection
    except Exception:
        pass # collection doesn't exist yet

    # create or recreate the collection
    try:
        client.delete_collection("policies")
    except Exception:
        pass

    collection = client.create_collection(name="policies")

    policy_dir = Path(__file__).parent.parent / "policies"

    documents = []
    metadatas = []
    ids = []

    for policy_file in policy_dir.glob("*.txt"):
        category = policy_file.stem 
        text = policy_file.read_text()
        chunks = [c.strip() for c in text.split("\n\n") if c.strip()]

        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "category": category,
                "chunk_index": i,
                "source": policy_file.name
            })
            ids.append(f"{category}_chunk_{i}")
    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Built persistent policy collection: {len(documents)} chunks")
    return collection

# Initialise once at module load
_collection = _build_policy_collection()

def retrieve_policies(state: CustomerSupportState) -> CustomerSupportState:
    """
    Retrieve relevant policies based on classified intent

    Reads: customer_message, intent
    Writes: relevant_policies, sources
    """

    intent = state.get("intent", "other")
    message = state["customer_message"]

    # Filter by classified intent category, search by message content
    raw = _collection.query(
        query_texts=[message],
        n_results=3,
        where={"category": {"$eq": intent}}
    )

    #filetr by distaance threshold
    relevant = []
    sources = []

    for i, doc in enumerate(raw["documents"][0]):
        distance = raw["distances"][0][i]
        if distance < DISTANCE_THRESHOLD:
            relevant.append(doc)
            sources.append(
                f"{raw['metadatas'][0][i]['source']} "
                f"(chunk {raw['metadatas'][0][i]['chunk_index']})"
            )

    state["relevant_policies"] = relevant
    state["sources"] = sources

    return state

# --- Standalone test ---
if __name__ == "__main__":
    test_states = [
        {
            "customer_message": "My credit card was charged twice for the same order",
            "intent": "billing",
            "confidence": 0.95
        },
        {
            "customer_message": "Where is my package? It was supposed to arrive yesterday",
            "intent": "shipping",
            "confidence": 0.9
        },
        {
            "customer_message": "I want my money back, this product is terrible",
            "intent": "refund",
            "confidence": 0.9
        },
        {
            "customer_message": "The app keeps crashing when I try to log in",
            "intent": "technical",
            "confidence": 0.95
        },
    ]

    for state in test_states:
        # Initialise other state fields
        state.setdefault("relevant_policies", None)
        state.setdefault("sources", None)

        result = retrieve_policies(state)
        
        print(f"\n{'='*60}")
        print(f"Message: {state['customer_message']}")
        print(f"Intent: {state['intent']}")
        print(f"Policies retrieved: {len(result['relevant_policies'])}")
        for src, policy in zip(result["sources"], result["relevant_policies"]):
            print(f"\n  {src}:")
            print(f"  {policy[:150]}...")
