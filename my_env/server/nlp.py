import logging
from typing import Optional

logger = logging.getLogger("api_gateway.nlp")

_has_transformers: Optional[bool] = None
_classifier: Optional[object] = None


def _load_classifier() -> Optional[object]:
    global _classifier
    if _classifier is not None:
        return _classifier

    global _has_transformers

    if _has_transformers is None:
        try:
            import transformers  # type: ignore[import]
            _has_transformers = True
        except ImportError:
            _has_transformers = False

    if not _has_transformers:
        logger.warning("Transformers is not installed; using fallback priority classifier.")
        return None

    try:
        logger.info("Initializing Local NLP Edge Classifier...")
        from transformers import pipeline

        _classifier = pipeline(
            "zero-shot-classification",
            model="typeform/distilbert-base-uncased-mnli"
        )
        return _classifier
    except Exception as e:
        logger.warning(f"Failed to initialize NLP pipeline: {e}")
        return None


def classify_priority(text: str) -> str:
    """
    True Semantic Edge NLP: Evaluates urgency using context probabilities
    rather than brittle substring matches.
    """
    candidate_labels = ["high priority emergency", "medium priority task", "low priority wishlist"]

    classifier = _load_classifier()
    if classifier is not None:
        try:
            result = classifier(text, candidate_labels)
            top_label = result["labels"][0]
            logger.info(
                f"NLP scores for '{text[:20]}...': {list(zip(result['labels'], result['scores']))}"
            )
            if "high" in top_label:
                return "high"
            elif "low" in top_label:
                return "low"
            else:
                return "medium"
        except Exception as e:
            logger.warning(f"Local NLP pipeline failed during inference: {e}")

    logger.warning("Using fallback priority classifier; defaulting to rule-based semantics.")
    text_lower = text.lower()
    if any(w in text_lower for w in ["urgent", "asap", "deadline", "critical", "emergency"]):
        return "high"
    if any(w in text_lower for w in ["fyi", "newsletter", "info", "update", "read", "optional"]):
        return "low"
    return "medium"
