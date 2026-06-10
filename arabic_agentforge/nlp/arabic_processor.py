"""Arabic-native text normalization and analysis."""

from __future__ import annotations

import re
import unicodedata

# Arabic diacritics (tashkeel) and Quranic annotation marks
_DIACRITICS_PATTERN = re.compile(
    "["
    "ؐ-ؚ"
    "ً-ٟ"
    "ٰ"
    "ۖ-ۜ"
    "۟-ۨ"
    "۪-ۭ"
    "]"
)

_TATWEEL = "ـ"

# Common Arabic letter-shape variants normalized to a canonical form
_LETTER_NORMALIZATION = {
    "آ": "ا",  # alef with madda above -> alef
    "أ": "ا",  # alef with hamza above -> alef
    "إ": "ا",  # alef with hamza below -> alef
    "ٱ": "ا",  # alef wasla -> alef
    "ى": "ي",  # alef maksura -> yeh
    "ة": "ه",  # teh marbuta -> heh
}

# Arabic, Arabic Supplement, and Arabic Extended-A blocks
_ARABIC_LETTER_PATTERN = re.compile("[؀-ۿݐ-ݿࢠ-ࣿ]")


class ArabicTextProcessor:
    """Normalizes Arabic text and detects script/direction for downstream pipelines."""

    def strip_diacritics(self, text: str) -> str:
        """Remove tashkeel (diacritical marks) from `text`."""
        return _DIACRITICS_PATTERN.sub("", text)

    def remove_tatweel(self, text: str) -> str:
        """Remove the Arabic tatweel/kashida elongation character."""
        return text.replace(_TATWEEL, "")

    def normalize_letters(self, text: str) -> str:
        """Collapse common letter-shape variants (alef forms, alef maksura, taa marbuta)."""
        for src, dst in _LETTER_NORMALIZATION.items():
            text = text.replace(src, dst)
        return text

    def normalize(
        self,
        text: str,
        *,
        strip_diacritics: bool = True,
        normalize_letters: bool = True,
    ) -> str:
        """Apply Unicode normalization plus the optional Arabic-specific cleanups."""
        text = unicodedata.normalize("NFKC", text)
        text = self.remove_tatweel(text)
        if strip_diacritics:
            text = self.strip_diacritics(text)
        if normalize_letters:
            text = self.normalize_letters(text)
        return re.sub(r"\s+", " ", text).strip()

    def is_arabic(self, text: str, threshold: float = 0.3) -> bool:
        """Return True if at least `threshold` of the alphabetic characters are Arabic."""
        letters = [c for c in text if c.isalpha()]
        if not letters:
            return False
        arabic_letters = [c for c in letters if _ARABIC_LETTER_PATTERN.match(c)]
        return (len(arabic_letters) / len(letters)) >= threshold

    def text_direction(self, text: str) -> str:
        """Return "rtl" for predominantly Arabic text, "ltr" otherwise."""
        return "rtl" if self.is_arabic(text) else "ltr"
