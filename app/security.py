import re
from typing import List


SUSPICIOUS_PATTERNS: List[str] = [
    r"ignore previous instructions",
    r"ignore all previous instructions",
    r"disregard previous instructions",
    r"system prompt",
    r"developer message",
    r"reveal your instructions",
    r"override instructions",
    r"do not follow the user",
]


def detect_prompt_injection(text: str) -> bool:
    normalized_text = text.lower()

    for pattern in SUSPICIOUS_PATTERNS:
        if re.search(pattern, normalized_text):
            return True

    return False


def sanitize_retrieved_text(text: str) -> str:
    if detect_prompt_injection(text):
        return (
            "[Potential prompt-injection content removed from retrieved document.]"
        )

    return text
