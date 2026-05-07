from state import CustomerSupportState

# routing threshold
CONFIDENCE_THRESHOLD = 0.5

def route_after_classification(state: CustomerSupportState) -> str:
    """
    Decide what happens after intent classification.
    
    Returns one of:
    - "escalate"   → low confidence, route to human escalation
    - "out_of_scope" → intent is "other", polite refusal
    - "in_scope"   → confident, valid intent → proceed to retrieval
    """
    confidence = state.get("confidence", 0)
    intent = state.get("intent", "other")

    if confidence < CONFIDENCE_THRESHOLD:
        return "escalate"
    elif intent == "other":
        return "out_of_scope"
    else:
        return "in_scope"

# --- Standalone test ---
if __name__ == "__main__":
    test_states = [
        # confidence, intent, expected
        ({"confidence": 0.95, "intent": "billing"}, "in_scope"),
        ({"confidence": 0.3, "intent": "billing"}, "escalate"),
        ({"confidence": 0.9, "intent": "other"}, "out_of_scope"),
        ({"confidence": 0.2, "intent": "other"}, "escalate"),
        ({"confidence": 0.85, "intent": "refund"}, "in_scope"),
    ]

    for state, expected in test_states:
        actual = route_after_classification(state)
        status = "✅" if actual == expected else "❌"
        print(f"{status} confidence={state['confidence']:.2f} intent={state['intent']:>10} → {actual} (expected: {expected})")