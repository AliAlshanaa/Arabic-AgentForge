"""RTL-aware chunking of Arabic (and mixed-direction) text."""

from __future__ import annotations

import re

# Split after Arabic/Latin sentence-ending punctuation followed by whitespace
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?؟؛])\s+")


class ArabicChunker:
    """Splits text into sentence-aware chunks suitable for RAG and context windows."""

    def __init__(self, max_chunk_size: int = 500, overlap: int = 50):
        if overlap >= max_chunk_size:
            raise ValueError("overlap must be smaller than max_chunk_size")
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def split_sentences(self, text: str) -> list[str]:
        """Split `text` into a list of non-empty sentences."""
        sentences = _SENTENCE_SPLIT.split(text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def chunk(self, text: str) -> list[str]:
        """Group sentences into chunks of at most `max_chunk_size` characters,
        carrying `overlap` characters from the previous chunk forward."""
        sentences = self.split_sentences(text)
        chunks: list[str] = []
        current: list[str] = []
        current_len = 0

        for sentence in sentences:
            if current and current_len + len(sentence) + 1 > self.max_chunk_size:
                chunks.append(" ".join(current))
                overlap_text = chunks[-1][-self.overlap:].strip()
                current = [overlap_text, sentence] if overlap_text else [sentence]
                current_len = sum(len(s) for s in current) + len(current) - 1
            else:
                current.append(sentence)
                current_len += len(sentence) + (1 if len(current) > 1 else 0)

        if current:
            chunks.append(" ".join(current))

        return chunks
