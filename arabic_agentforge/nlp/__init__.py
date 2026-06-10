"""Arabic-native NLP utilities: normalization, dialect handling, and chunking."""

from .arabic_processor import ArabicTextProcessor
from .chunker import ArabicChunker
from .dialect_handler import Dialect, DialectHandler

__all__ = ["ArabicTextProcessor", "ArabicChunker", "Dialect", "DialectHandler"]
