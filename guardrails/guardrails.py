from guardrails.vulnerability_checklist import (
    CRISIS_PATTERNS,
    PROMPT_INJECTION_PATTERNS,
    AADHAAR_PATTERN,
    EMAIL_PATTERN,
    PHONE_PATTERN,
    UNSAFE_OUTPUT_PATTERNS,
)
import re
from utils.logger import get_logger

logger = get_logger(__name__)


def check_for_vulnerability(list_of_checks, text) -> bool:
    logger.info("Checking for check_for_vulnerability")
    text = text.lower()
    for sentence in list_of_checks:
        if re.search(sentence.lower(), text):
            logger.info("check_for_vulnerability: True")
            return True
    logger.info("check_for_vulnerability: False")
    return False


def detect_emergency(text) -> bool:
    logger.info("Checking for emergency")
    critical = check_for_vulnerability(CRISIS_PATTERNS, text)
    logger.info("Detect emergency %s", critical)
    return critical


def detect_prompt_injection(text) -> bool:
    logger.info("Checking for PROMPT_INJECTION_PATTERNS")

    return check_for_vulnerability(PROMPT_INJECTION_PATTERNS, text)


def detect_pii(text) -> bool:
    logger.info("Checking for PII ")

    return bool(
        re.search(AADHAAR_PATTERN, text)
        or re.search(EMAIL_PATTERN, text)
        or re.search(PHONE_PATTERN, text)
    )


def check_input(text):
    logger.info("Checking input as part of guardrail implementation")
    emergency = detect_emergency(text)
    prompt_injection = detect_prompt_injection(text)
    pii = detect_pii(text)

    result = {
        "has_emergency": emergency,
        "has_prompt_injection": prompt_injection,
        "has_pii": pii,
        "is_unsafe": emergency or prompt_injection,
    }

    return result


def validate_output(response: str) -> bool:
    output_safe = check_for_vulnerability(UNSAFE_OUTPUT_PATTERNS, response)
    logger.info("Inside output validation - result is %s", output_safe)
    return output_safe


def emergency_response():
    return (
        "I'm really sorry you're going through something this painful. "
        "I’m glad you told me. You don't have to face this moment alone.\n\n"
        "If you feel you may hurt yourself or are in immediate danger, "
        "please contact your local emergency service or go to the nearest "
        "emergency department now.\n\n"
        "You can also call Tele-MANAS at 14416, a 24/7 mental-health support service.\n\n"
        "If possible, please stay with someone you trust and tell them "
        "what you're experiencing."
    )


def safe_fallback():
    return (
        "I want to be careful about how I respond to this. "
        "I may not have enough context to give you a confident answer. "
        "Would you like to tell me a little more about what you're going through?"
    )
