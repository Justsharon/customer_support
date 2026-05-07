import os
import json
from groq import Groq
from pydantic import BaseModel, ValidationError, field_validator
from typing import List
from dotenv import load_dotenv

load_dotenv()

from agents.llm_helper import call_llm
from state import CustomerSupportState

class DraftResponse(BaseModel):
    response: str
    cited_sections: List[str]

    @field_validator("response")
    @classmethod
    def response_not_empty(cls, value):
        if not value or len(value.strip()) < 20:
            raise ValueError("Response must be atleast 20 characters")
        return value
    
DRAFTER_PROMPT = """You are a customer support agent for an e-commerce company.

Your job: Draft a response to the customer using ONLY the policies provided below.

CRITICAL RULES:
- Use ONLY information from the provided policies
- Do NOT invent details, timelines, prices, or commitments
- Do NOT promise things the policies do not explicitly state
- If the policies do not address the customer's specific question, say so honestly
- Match the customer's emotional tone — be empathetic if they're frustrated
- Keep responses concise — 3-5 sentences typically

CUSTOMER INTENT: {intent}

CUSTOMER MESSAGE: {message}

RELEVANT POLICIES:
{policies}

Respond with ONLY a JSON object in this exact format:
{{
  "response": "<your draft response to the customer>",
  "cited_sections": ["<policy section name 1>", "<policy section name 2>"]
}}

Do not include any text before or after the JSON object."""


def draft_response(state: CustomerSupportState) -> CustomerSupportState:
    """
    Draft a customer response grounded in retrieved policies.
    
    Reads:  customer_message, intent, relevant_policies
    Writes: draft_response
    """

    client = Groq(api_key=os.getenv("API_KEY"))
    
    # Format policies as context
    if state.get("relevant_policies"):
        policies_text = "\n\n".join([
            f"[Policy {i+1}]\n{policy}"
            for i, policy in enumerate(state["relevant_policies"])
        ])
    else:
        policies_text = "No specific policies found for this query."

    prompt = DRAFTER_PROMPT.format(
        intent=state.get("intent", "unknown"),
        message=state["customer_message"],
        policies=policies_text
    ) 

    raw_output = call_llm(prompt, max_tokens=400, temperature=0.1)

    try:
        parsed = json.loads(raw_output)
        draft = DraftResponse(**parsed)
        state["draft_response"] = draft.response
         # We'll use cited_sections in the reviewer
    except (json.JSONDecodeError, ValidationError) as e:
        state["draft_response"] = (
            "I apologise, but I'm having trouble processing your request right now. "
            "Let me escalate this to a human agent who can assist you better."
        )
        state["escalation_reason"] = f"Drafter failed: {str(e)}"
    return state

# --- Standalone test ---
if __name__ == "__main__":
    from agents.classifier import classify_intent
    from agents.retriever import retrieve_policies

    test_messages = [
        "My credit card was charged twice for the same order",
        "Where is my package? It was supposed to arrive yesterday",
        "I want my money back, this product is terrible",
    ]

    for msg in test_messages:
        # Initialise full state
        state = {
            "customer_message": msg,
            "intent": None,
            "confidence": None,
            "classification_reasoning": None,
            "relevant_policies": None,
            "sources": None,
            "draft_response": None,
            "final_response": None,
            "needs_human_review": None,
            "review_notes": None,
            "escalation_reason": None
        }

        # run the pipeline so far
        state = classify_intent(state)
        state = retrieve_policies(state)
        state = draft_response(state)

        print(f"\n{'='*60}")
        print(f"Customer: {msg}")
        print(f"Intent: {state['intent']} (confidence: {state['confidence']:.2f})")
        print(f"\nDraft response:")
        print(state["draft_response"])