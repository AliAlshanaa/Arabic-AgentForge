"""Hallucination guard tuned for Arabic-language agent responses."""

from __future__ import annotations

from dataclasses import dataclass

from .citation import Citation, CitationEnforcer


@dataclass
class GuardResult:
    """Outcome of a hallucination-guard check."""

    passed: bool
    reason: str = ""


class ArabicHallucinationGuard:
    """Rejects responses that lack citations or fall below a confidence threshold."""

    def __init__(self, citation_required: bool = True, confidence_threshold: float = 0.85):
        self.citation_required = citation_required
        self.confidence_threshold = confidence_threshold
        self._citations = CitationEnforcer()

    def check(
        self,
        response: str,
        *,
        confidence: float = 1.0,
        sources: list[Citation] | None = None,
    ) -> GuardResult:
        """Check `response` against the confidence threshold and citation requirements."""
        if confidence < self.confidence_threshold:
            return GuardResult(
                passed=False,
                reason=f"confidence {confidence:.2f} below threshold {self.confidence_threshold:.2f}",
            )

        if self.citation_required and sources:
            if not self._citations.has_citations(response):
                return GuardResult(passed=False, reason="response contains no citation markers")
            if not self._citations.validate(response, sources):
                return GuardResult(passed=False, reason="response cites a source that does not exist")

        return GuardResult(passed=True)
