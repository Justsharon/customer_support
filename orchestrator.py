from langgraph.graph import StateGraph, END
from state import CustomerSupportState

from agents.classifier import classify_intent
from agents.router import route_after_classification
from agents.retriever import retrieve_policies
from agents.drafter import draft_response
from agents.reviewer import review_response

# --- Special handler nodes for non-standard paths ---

def escalate_to_human(state: CustomerSupportState) -> CustomerSupportState:
    """Handle low-confidence cases that need human review"""
    state["final_response"] = (
        "Thank you for reaching out. Your request requires personal attention "
        "from one of our team members. A support agent will respond to your "
        "message within 4 business hours."
    )
    state["needs_human_review"] = True
    state["escalation_reason"] = state.get("escalation_reason") or (
        f"Low classification confidence ({state.get('confidence', 0):.2f})"
    )
    return state

def polite_refusal(state: CustomerSupportState) -> CustomerSupportState:
    """Handle out-of-scope queries with a courteous refusal"""
    state["final_response"] = (
        "Thank you for your message! Your inquiry doesn't appear to relate to "
        "our standard support categories. If you have a specific question about "
        "billing, shipping, technical issues, or refunds, please let me know "
        "and I'll be happy to help. For other matters, please contact us at "
        "support@example.com."
    )
    state["needs_human_review"] = False
    return state

# --- Build the graph ---
def build_workflow():
    """Construct the full multi-agent customer support workflow"""
    graph = StateGraph(CustomerSupportState)

    # Add all nodes
    graph.add_node("classifier", classify_intent)
    graph.add_node("retriever", retrieve_policies)
    graph.add_node("drafter", draft_response)
    graph.add_node("reviewer", review_response)
    graph.add_node("escalate", escalate_to_human)
    graph.add_node("refusal", polite_refusal)

    # Entry point
    graph.set_entry_point("classifier")

    # Conditional routing after classifier
    graph.add_conditional_edges(
        source="classifier",
        path=route_after_classification,
        path_map={
            "in_scope": "retriever",
            "escalate": "escalate",
            "out_of_scope": "refusal"
        }
    )

    # In-scope path: retriever → drafter → reviewer → END
    graph.add_edge("retriever", "drafter")
    graph.add_edge("drafter", "reviewer")
    graph.add_edge("reviewer", END)


    # Off-ramp paths go directly to END
    graph.add_edge("escalate", END)
    graph.add_edge("refusal", END)

    return graph.compile()

if __name__ == "__main__":
    workflow = build_workflow()
    
    test_messages = [
        "My credit card was charged twice for the same order",
        "Where is my package? It was supposed to arrive yesterday",
        "I want my money back, this product is terrible",
        "Hi, just wanted to say thanks for the great service!",
        "asdf qwerty random nonsense",
    ]
    
    for msg in test_messages:
        # Initialise full state
        initial_state = {
            "customer_message": msg,
            "intent": None, "confidence": None, "classification_reasoning": None,
            "relevant_policies": None, "sources": None,
            "draft_response": None, "final_response": None,
            "needs_human_review": None, "review_notes": None,
            "escalation_reason": None
        }
        
        # Run the full graph
        result = workflow.invoke(initial_state)
        
        print(f"\n{'='*70}")
        print(f"Customer: {msg}")
        print(f"Intent: {result.get('intent')} (confidence: {result.get('confidence', 0):.2f})")
        print(f"\n Response:\n{result.get('final_response')}")
        print(f"\n Needs human review: {result.get('needs_human_review')}")
        if result.get("escalation_reason"):
            print(f" Escalation: {result['escalation_reason']}")
        if result.get("review_notes"):
            print(f" Notes: {result['review_notes']}")