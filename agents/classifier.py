import os
import json
from groq import Groq
from pydantic import BaseModel, ValidationError, field_validator
from typing import Literal
from dotenv import load_dotenv

load_dotenv()

from agents.llm_helper import call_llm
from state import CustomerSupportState

# --- The structured output contract ---
class IntentClassification(BaseModel):
    intent: Literal["billing", "technical", "shipping", "refund", "complaint", "other"]
    confidence: float
    reasoning: str

    @field_validator("confidence")
    @classmethod
    def confidence_in_range(cls, value):
        if not 0 <= value <= 1:
            raise ValueError(f"Confidence must be between 0 and 1, got {value}")
        return value
    
# --- The prompt ---

CLASSIFIER_PROMPT = """You are a customer support intent classifier for an e-commerce company.

Given a customer message, classify it into EXACTLY ONE of these intents:
- billing: payment issues, charges, invoices, subscription questions
- technical: app crashes, login issues, features not working, bugs
- shipping: delivery delays, missing packages, tracking, address changes
- refund: return requests, refund status, exchange requests
- complaint: dissatisfaction, complaints about service or product quality
- other: anything that does not clearly fit the above

IMPORTANT RULES:
- Choose the SINGLE best category, even if multiple could apply.
- Do NOT assume details that are not explicitly stated.
- If multiple categories are plausible, pick the closest one and LOWER your confidence.
- Do NOT assign high confidence if another category could reasonably apply.
- If the message is not a support request (e.g., greetings, thanks, feature suggestions, unclear text), classify as "other" with LOW confidence.

CONFIDENCE CALIBRATION — CRITICAL:
Confidence reflects how clearly the message matches a support category.

Use HIGH confidence (0.85-1.0) ONLY when:
- The message clearly describes a specific, unambiguous support issue
- No other category is reasonably plausible

Use MODERATE confidence (0.5-0.8) when:
- The intent is somewhat clear but ambiguous OR multiple categories could apply
- The message lacks detail or context

Use LOW confidence (0.0-0.4) when:
- The message is a greeting, gratitude, suggestion, or not a support request
- The message is vague, unclear, or incomplete
- The message is gibberish or nonsensical
- You must choose "other" because nothing clearly fits

CRITICAL:
- Selecting "other" with HIGH confidence is almost always incorrect.
- If "other" is selected, confidence should typically be LOW.

OUTPUT FORMAT:
Respond with ONLY a valid JSON object in this exact format:

{{
    "intent": "<one of the categories above>",
    "confidence": <float between 0 and 1>,
    "reasoning": "<one concise sentence explaining this intent and its confidence>"
}}


Customer message: {message}

Respond with only the JSON object, no additional text."""

# --- The agent function ---
def classify_intent(state: CustomerSupportState) -> CustomerSupportState:
    """
    Classify customer message intent and assign confidence
    Reads: customer_message
    Writes: intent, confidence, classification_reasoning
    """

    prompt = CLASSIFIER_PROMPT.format(message=state["customer_message"])

    raw_output = call_llm(prompt, max_tokens=400, temperature=0.1)

    try:
        parsed = json.loads(raw_output)
        classification = IntentClassification(**parsed) # Pydantic validates

        state["intent"] = classification.intent
        state["confidence"] = classification.confidence
        state["classification_reasoning"] = classification.reasoning
    except (json.JSONDecodeError, ValidationError) as e:
        # Fallback if LLM returns malformed output
        state["intent"] = "other"
        state["confidence"] = 0.0
        state["classification_reasoning"] = f"Classification failed: {str(e)}"
    return state

# --- Standalone test ---

if __name__ == "__main__":
    test_messages = [
        "My credit card was charged twice for the same order",
        "The app keeps crashing when I try to log in",
        "Where is my package? It was supposed to arrive yesterday",
        "I want my money back, this product is terrible",
        "Hi, just wanted to say thanks for the great service!",
        "asdf qwerty random nonsense"
    ]
    
    for msg in test_messages:
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
        
        result = classify_intent(state)
        
        print(f"Message: {msg[:60]}")
        print(f"  Intent: {result['intent']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Reasoning: {result['classification_reasoning']}")
        print()       