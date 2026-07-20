# Reading documents logic

from typing import Dict
from models import SubmissionInput

# If any filename contains the keyword substring, that flag becomes True.
KEYWORDS = {
    "pid": "pid",
    "datasheet": "datasheet",
    "certificate": "certificate",
    "sap": "sap"
}

def _contains_keyword(file_names: list[str], keyword: str) -> bool:
    """Return True if any filename contains the keyword (case-insensitive)."""
    if not file_names:
        return False
    lower_names = (fn.lower() for fn in file_names)
    return any(keyword in name for name in lower_names)

def evaluate_submission(submission: SubmissionInput) -> Dict[str, object]:
    """
    Evaluate a SubmissionInput and return a dictionary with:
      - tag, asset_type, system and punch (copied from input)
      - boolean for pid, datasheet, certificate, sap (based on file_names)

    Example output (same as given):
    {
      "tag": "P-101",
      "asset_type": "Pump",
      "system": "Cooling Water",
      "pid": True,
      "datasheet": False,
      "certificate": True,
      "sap": True,
      "punch": "Closed"
    }
    """
    file_names = submission.file_names or []

    result = {
        "tag": submission.tag,
        "asset_type": submission.asset_type,
        "system": submission.system,
        # flags derived from file names
        "pid": _contains_keyword(file_names, KEYWORDS["pid"]),
        "datasheet": _contains_keyword(file_names, KEYWORDS["datasheet"]),
        "certificate": _contains_keyword(file_names, KEYWORDS["certificate"]),
        "sap": _contains_keyword(file_names, KEYWORDS["sap"]),
        # punch copied directly
        "punch": submission.punch,
    }

    return result