"""Detection and normalization of Arabic regional dialects."""

from __future__ import annotations

from enum import Enum


class Dialect(str, Enum):
    """Arabic dialect families recognized by `DialectHandler`."""

    MSA = "msa"
    GULF = "gulf"
    LEVANTINE = "levantine"
    EGYPTIAN = "egyptian"


# Marker words strongly associated with each dialect family
_DIALECT_MARKERS: dict[Dialect, set[str]] = {
    Dialect.GULF: {
        "وش", "شلونك", "شلون", "ابغى", "أبغى", "ابي", "أبي",
        "وايد", "زين", "يبا", "عاد", "تبي", "شنو", "ليه",
    },
    Dialect.LEVANTINE: {
        "شو", "هلق", "كتير", "منيح", "هيك", "بدي", "ليش",
        "هلأ", "كمان", "شلونك", "تمام",
    },
    Dialect.EGYPTIAN: {
        "ازيك", "إزيك", "عايز", "عاوز", "كده", "ازاي", "إزاي",
        "خالص", "مش", "دلوقتي", "ايه", "إيه",
    },
}

# Dialectal terms mapped to a Modern Standard Arabic equivalent
_TO_MSA: dict[str, str] = {
    "وش": "ما",
    "شلونك": "كيف حالك",
    "شلون": "كيف",
    "ابغى": "أريد",
    "أبغى": "أريد",
    "ابي": "أريد",
    "أبي": "أريد",
    "وايد": "كثيرا",
    "تبي": "تريد",
    "شنو": "ما",
    "شو": "ما",
    "هلق": "الآن",
    "هلأ": "الآن",
    "كتير": "كثير",
    "منيح": "جيد",
    "بدي": "أريد",
    "ليش": "لماذا",
    "ازيك": "كيف حالك",
    "إزيك": "كيف حالك",
    "عايز": "أريد",
    "عاوز": "أريد",
    "كده": "هكذا",
    "ازاي": "كيف",
    "إزاي": "كيف",
    "مش": "ليس",
    "دلوقتي": "الآن",
    "ايه": "ماذا",
    "إيه": "ماذا",
}


class DialectHandler:
    """Detects the dialect of an Arabic text and normalizes dialectal terms toward MSA."""

    def detect(self, text: str) -> Dialect:
        """Return the dialect with the most marker-word hits, or MSA if none match."""
        words = set(text.split())
        scores = {dialect: len(words & markers) for dialect, markers in _DIALECT_MARKERS.items()}
        best_dialect, best_score = max(scores.items(), key=lambda item: item[1])
        return best_dialect if best_score > 0 else Dialect.MSA

    def normalize_to_msa(self, text: str) -> str:
        """Replace recognized dialectal words with their Modern Standard Arabic equivalent."""
        return " ".join(_TO_MSA.get(word, word) for word in text.split())
