from typing import TypedDict, Optional, Literal

IntentType = Literal["billing", "technical", "shipping", "refund", "complaint", "other"]


class CustomerSupportState(TypedDict):
    # input
    customer_message: str

    # Set by classifier
    intent: Optional[IntentType]
    confidence: Optional[float]
    classification_reasoning: Optional[str]

    # Set by retreiver (later)
    relevant_policies: Optional[list[str]]
    sources: Optional[list[str]]
    
    # Set by drafter (later)
    draft_response: Optional[str]
    
    # Set by reviewer (later)
    final_response: Optional[str]
    needs_human_review: Optional[bool]
    review_notes: Optional[str]
    
    # Routing flags
    escalation_reason: Optional[str]