import os 
import json
from groq import Groq
from pydantic import BaseModel, ValidationError
from typing import Literal

from dotenv import load_dotenv
from agents.llm_helper import call_llm
from state import CustomerSupportState

load_dotenv()


class ReviewResult(BaseModel):
    quality_rating: Literal["approved", "needs_edits", "escalate"]
    quality_score: float
    issues_found: list[str]
    suggested_edits: str
    reasoning: str

REVIEWER_PROMPT = """You are a quality assurance reviewer for customer support responses.

Your job: Review the draft response against the retrieved policies and decide if it's ready to send.

REVIEW CRITERIA:
1. POLICY ADHERENCE — All facts in the response must come from the retrieved policies
2. TONE — Empathetic for complaints, professional for technical, appropriate for context
3. COMPLETENESS — Does it actually answer the customer's question?
4. NO HALLUCINATION — No invented timelines, prices, or commitments
5. NO OVERPROMISING — No promises beyond what policies state

QUALITY RATINGS:
- "approved" — Response is accurate, on-policy, ready to send. Quality score 0.85+
- "needs_edits" — Minor issues that can be fixed with small edits. Quality score 0.5-0.85
- "escalate" — Significant issues, response should not be sent without human review. Quality score below 0.5

CUSTOMER MESSAGE: {message}
INTENT: {intent}

RETRIEVED POLICIES:
{policies}

DRAFT RESPONSE TO REVIEW:
{draft}

Respond with ONLY a JSON object:
{{
  "quality_rating": "<approved | needs_edits | escalate>",
  "quality_score": <float 0-1>,
  "issues_found": ["<issue 1>", "<issue 2>"],
  "suggested_edits": "<edit suggestion or empty string>",
  "reasoning": "<one sentence explaining your decision>"
}}

Do not include any text before or after the JSON object."""

def review_response(state: CustomerSupportState) -> CustomerSupportState:
    """
    Review the draft response for quality and policy adherence.
    
    Reads:  customer_message, intent, relevant_policies, draft_response
    Writes: final_response, needs_human_review, review_notes
    """

    client = Groq(api_key=os.getenv("API_KEY"))

    policies_text = "\n\n".join([
        f"[Policy {i+1}]\n{p}"
        for i, p in enumerate(state.get("relevant_policies", []))
    ])

    prompt = REVIEWER_PROMPT.format(
        message=state["customer_message"],
        intent=state.get("intent", "unknown"),
        policies=policies_text or "No policies retrieved",
        draft=state["draft_response"]
    )

    raw_output = call_llm(prompt, max_tokens=400, temperature=0.1)
    try:
        parsed = json.loads(raw_output)
        review = ReviewResult(**parsed)

        if review.quality_rating == "approved":
            state["final_response"] = state["draft_response"]
            state["needs_human_review"] = False
            state["review_notes"] = f"Approved. Score: {review.quality_score:.2f}"

        elif review.quality_rating == "needs_edits":
            # For now we send with notes — production would re-draft
            state["final_response"] = state["draft_response"]
            state["needs_human_review"] = True
            state["review_notes"] = (
                f"Needs edits ({review.quality_score:.2f}). "
                f"Issues: {', '.join(review.issues_found)}. "
                f"Suggested: {review.suggested_edits}"
            )

        else:  # escalate
            state["final_response"] = None
            state["needs_human_review"] = True
            state["escalation_reason"] = (
                f"Reviewer flagged for escalation ({review.quality_score:.2f}). "
                f"Issues: {', '.join(review.issues_found)}"
            )
            state["review_notes"] = review.reasoning

    except (json.JSONDecodeError, ValidationError) as e:
        # Fail safe — escalate on review failure
        state["final_response"] = None
        state["needs_human_review"] = True
        state["escalation_reason"] = f"Review failed: {str(e)}"
    
    return state

# --- Standalone test ---
if __name__ == "__main__":
    from agents.classifier import classify_intent
    from agents.retriever import retrieve_policies
    from agents.drafter import draft_response
    
    test_messages = [
        "My credit card was charged twice for the same order",
        "I want my money back, this product is terrible",
        "The app keeps crashing when I try to log in",
    ]
    
    for msg in test_messages:
        state = {
            "customer_message": msg,
            "intent": None, "confidence": None, "classification_reasoning": None,
            "relevant_policies": None, "sources": None,
            "draft_response": None, "final_response": None,
            "needs_human_review": None, "review_notes": None,
            "escalation_reason": None
        }
        
        state = classify_intent(state)
        state = retrieve_policies(state)
        state = draft_response(state)
        state = review_response(state)
        
        print(f"\n{'='*60}")
        print(f"Customer: {msg}")
        print(f"Intent: {state['intent']} ({state['confidence']:.2f})")
        print(f"\nFinal response: {state['final_response']}")
        print(f"Needs human review: {state['needs_human_review']}")
        print(f"Review notes: {state['review_notes']}")
        if state.get("escalation_reason"):
            print(f"Escalation reason: {state['escalation_reason']}")