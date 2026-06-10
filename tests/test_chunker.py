import pytest

from arabic_agentforge.nlp import ArabicChunker


def test_split_sentences_handles_arabic_punctuation():
    chunker = ArabicChunker()
    text = "هذا اليوم جميل. الطقس رائع؟ نعم بالتأكيد!"
    assert chunker.split_sentences(text) == [
        "هذا اليوم جميل.",
        "الطقس رائع؟",
        "نعم بالتأكيد!",
    ]


def test_chunk_returns_single_chunk_for_short_text():
    chunker = ArabicChunker(max_chunk_size=500, overlap=50)
    text = "هذا اليوم جميل. الطقس رائع."
    chunks = chunker.chunk(text)
    assert len(chunks) == 1
    assert "هذا اليوم جميل." in chunks[0]
    assert "الطقس رائع." in chunks[0]


def test_chunk_splits_long_text_with_overlap():
    chunker = ArabicChunker(max_chunk_size=15, overlap=5)
    text = "جملة واحدة. جملة اثنين. جملة ثلاثة. جملة اربعة."
    chunks = chunker.chunk(text)

    assert len(chunks) > 1
    for previous, current in zip(chunks, chunks[1:]):
        assert current.startswith(previous[-5:])


def test_overlap_must_be_smaller_than_max_chunk_size():
    with pytest.raises(ValueError):
        ArabicChunker(max_chunk_size=10, overlap=10)
