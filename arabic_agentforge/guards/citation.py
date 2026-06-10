"""Citation tracking and enforcement for Arabic content generation."""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class Citation:
    """A single source reference that a response can point to via `[n]` markers."""

    source: str
    excerpt: str = ""


_CITATION_MARKER = re.compile(r"\[(\d+)\]")


class CitationEnforcer:
    """Validates that `[n]`-style citation markers in a response refer to real sources."""

    def extract_markers(self, text: str) -> list[int]:
        """Return the citation indices referenced in `text`, e.g. [1, 2]."""
        return [int(m) for m in _CITATION_MARKER.findall(text)]

    def has_citations(self, text: str) -> bool:
        """Return True if `text` contains at least one `[n]` marker."""
        return bool(self.extract_markers(text))

    def validate(self, text: str, sources: list[Citation]) -> bool:
        """Return True if every marker in `text` is within range of `sources`."""
        markers = self.extract_markers(text)
        if not markers:
            return False
        return all(1 <= marker <= len(sources) for marker in markers)

    def format_sources(self, sources: list[Citation]) -> str:
        """Render `sources` as a numbered reference list matching `[n]` markers."""
        return "\n".join(f"[{i + 1}] {citation.source}" for i, citation in enumerate(sources))
