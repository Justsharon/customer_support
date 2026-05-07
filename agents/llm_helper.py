import os
import json
from pathlib import Path
from groq import Groq
import ollama

# Recording configuration
RECORDINGS_PATH = Path(__file__).parent.parent / "recordings.json"
RECORD_MODE = os.environ.get("RECORD_LLM", "false").lower() == "true"


def _load_recordings() -> dict:
    """Load saved LLM responses"""
    if RECORDINGS_PATH.exists():
        with open(RECORDINGS_PATH) as f:
            return json.load(f)
    return {}


def _save_recording(prompt: str, response: str) -> None:
    """Append a new recording to the JSON file"""
    recordings = _load_recordings()
    # Use a hash of the prompt as the key to handle long prompts
    import hashlib
    prompt_key = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    recordings[prompt_key] = {
        "prompt_preview": prompt[:200],  # for human readability
        "response": response
    }
    
    with open(RECORDINGS_PATH, "w") as f:
        json.dump(recordings, f, indent=2)


def call_llm(prompt: str, max_tokens: int = 500, temperature: float = 0.3) -> str:
    """
    Call LLM with automatic fallback chain.
    Records responses when RECORD_LLM=true.
    """
    providers = [
        ("groq", _call_groq),
        # ("ollama", _call_ollama),
        ("mock", _call_mock),
    ]

    last_error = None
    for name, fn in providers:
        try:
            response = fn(prompt, max_tokens, temperature)
            
            # Record real responses for future mock use
            if RECORD_MODE and name in ("groq", "ollama"):
                _save_recording(prompt, response)
                print(f"Recorded response from {name}")
            
            return response
        except Exception as e:
            last_error = e
            print(f"{name} failed: {str(e)[:100]}. Trying next provider...")
            continue

    raise RuntimeError(f"All providers exhausted. Last error: {last_error}")


def _call_groq(prompt, max_tokens, temperature):
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def _call_ollama(prompt, max_tokens, temperature):
    response = ollama.chat(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": prompt}],
        options={
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    )
    return response["message"]["content"].strip()


def _call_mock(prompt, max_tokens, temperature):
    """
    Mock that replays real recorded responses when available.
    Falls back to pattern matching for unknown prompts.
    """
    print("MOCK CALLED")
    
    # Try recorded responses first
    import hashlib
    prompt_key = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    recordings = _load_recordings()
    
    if prompt_key in recordings:
        print("Replaying recorded response")
        return recordings[prompt_key]["response"]
    
    # Fall back to pattern-based mocks for unknown prompts
    print("No recording found, using pattern fallback")
    return _pattern_based_mock(prompt)


def _pattern_based_mock(prompt: str) -> str:
    """Pattern-based fallback for unrecorded prompts"""
    if "Customer message:" in prompt:
        msg_section = prompt.split("Customer message:")[1]
        prompt_lower = msg_section.lower()
    elif "CUSTOMER MESSAGE:" in prompt:
        msg_section = prompt.split("CUSTOMER MESSAGE:")[1]
        prompt_lower = msg_section.lower()
    else:
        prompt_lower = prompt.lower()
    
    # Classifier mocks
    if "classify" in prompt.lower() and "intent" in prompt.lower():
        if "charged" in prompt_lower or "credit card" in prompt_lower:
            return json.dumps({
                "intent": "billing", "confidence": 0.95,
                "reasoning": "Customer mentions billing issue."
            })
        elif "package" in prompt_lower or "delivery" in prompt_lower:
            return json.dumps({
                "intent": "shipping", "confidence": 0.90,
                "reasoning": "Customer asking about delivery."
            })
        elif "money back" in prompt_lower or "refund" in prompt_lower:
            return json.dumps({
                "intent": "refund", "confidence": 0.88,
                "reasoning": "Customer requesting refund."
            })
        elif "crash" in prompt_lower or "log in" in prompt_lower:
            return json.dumps({
                "intent": "technical", "confidence": 0.95,
                "reasoning": "Technical issue reported."
            })
        elif "thanks" in prompt_lower or "thank" in prompt_lower:
            return json.dumps({
                "intent": "other", "confidence": 0.20,
                "reasoning": "Gratitude expression."
            })
        else:
            return json.dumps({
                "intent": "other", "confidence": 0.10,
                "reasoning": "Unclear message."
            })
    
    if "draft a response" in prompt.lower() or "customer support agent" in prompt.lower():
        return json.dumps({
            "response": "Thank you for reaching out. Based on our policy, your request will be processed.",
            "cited_sections": ["Policy"]
        })
    
    if "quality assurance reviewer" in prompt.lower():
        return json.dumps({
            "quality_rating": "approved", "quality_score": 0.85,
            "issues_found": [], "suggested_edits": "",
            "reasoning": "Response is acceptable."
        })
    
    return json.dumps({"error": "no mock matched"})