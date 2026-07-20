# LLM explain

# explain.py
import os
import requests
from typing import Dict, Tuple
from models import SubmissionOutput

# Environment variable name for Google API key
GOOGLE_API_KEY_ENV = "GOOGLE_API_KEY"

# Fallback actions when LLM fails
FALLBACK_ACTIONS = {
    "NOT READY": "Responsible team must resolve all missing items before handover",
    "BLOCKED": "Construction must close the punch item before handover",
    "READY": "Asset can proceed to handover review",
}

# Google Generative Language endpoint for text-bison (uses API key in query param)
GGL_BASE = "https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generate"

def _compute_status_and_reason(d: Dict) -> Tuple[str, str]:
    required_flags = ["pid", "datasheet", "certificate", "sap"]
    missing = [k for k in required_flags if not bool(d.get(k))]
    punch = (d.get("punch") or "").strip()

    # Determine status
    if punch.lower() != "closed":
        status = "BLOCKED"
    elif missing:
        status = "NOT READY"
    else:
        status = "READY"

    # Build reason
    if status == "READY":
        reason = "All required records are available and punch is closed"
    elif status == "BLOCKED" and missing:
        missing_list = ", ".join(missing)
        reason = f"Punch item is open; {missing_list} is missing"
    elif status == "BLOCKED":
        reason = "Punch item is open"
    else:  # NOT READY
        missing_list = ", ".join(missing)
        reason = f"{missing_list} is missing"

    return status, reason

def _build_prompt(d: Dict) -> str:
    # Keep the prompt compact and explicit; ask for one sentence
    return (
        "You are giving an action to fix an equipment document-completeness check. "
        f"Given this data: {d} "
        "Write exactly one concise sentence explaining who is responsible for submitting the missing document(s). "
        "If punch isn't closed, indicate engineers/construction as responsible. "
        "If documents are missing, indicate the responsible team. Be concise."
    )

def _call_google_bison(prompt: str, max_output_tokens: int = 60, timeout: int = 10) -> str:
    """
    Call Google Generative Language (text-bison) using an API key stored in env var.
    Returns the generated text (first candidate) or raises an exception on failure.
    """
    api_key = os.getenv(GOOGLE_API_KEY_ENV)
    if not api_key:
        raise RuntimeError(f"Google API key not found in env var {GOOGLE_API_KEY_ENV}")

    url = f"{GGL_BASE}?key={api_key}"
    payload = {
        "prompt": {"text": prompt},
        "maxOutputTokens": max_output_tokens,
        "temperature": 0.0,
    }
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    data = resp.json()

    # Parse response: candidates[0].output is the usual field
    candidates = data.get("candidates") or []
    if not candidates:
        # Some responses may use different shapes; try other keys defensively
        raise ValueError("No candidates returned from Google API")
    output = candidates[0].get("output") or ""
    return output.strip()

def explain_evaluation(evaluation_dict: Dict) -> SubmissionOutput:
    """
    Convert evaluation dict into SubmissionOutput, calling Google Gemini (text-bison)
    for 'action' and falling back to deterministic messages if the API fails.
    """
    asset = f"Asset : {evaluation_dict.get('tag')} | {evaluation_dict.get('asset_type')} | {evaluation_dict.get('system')}"
    status, reason = _compute_status_and_reason(evaluation_dict)

    # Build prompt and call the API
    prompt = _build_prompt(evaluation_dict)
    try:
        action_text = _call_google_bison(prompt, max_output_tokens=60)
        # Keep only the first line/sentence to be safe
        action = action_text.splitlines()[0].strip()
        if not action:
            raise ValueError("Empty action from API")
    except Exception:
        action = FALLBACK_ACTIONS.get(status, FALLBACK_ACTIONS["NOT READY"])

    return SubmissionOutput(asset=asset, status=status, reason=reason, action=action)
