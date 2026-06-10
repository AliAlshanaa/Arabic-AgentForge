from arabic_agentforge.nlp import ArabicTextProcessor


def test_strip_diacritics_removes_tashkeel():
    processor = ArabicTextProcessor()
    assert processor.strip_diacritics("مَرْحَبًا") == "مرحبا"


def test_normalize_letters_unifies_alef_and_yeh_forms():
    processor = ArabicTextProcessor()
    assert processor.normalize_letters("أحمد إلى آخر مستشفى") == "احمد الي اخر مستشفي"
    assert processor.normalize_letters("مدرسة") == "مدرسه"


def test_remove_tatweel():
    processor = ArabicTextProcessor()
    assert processor.remove_tatweel("مرحـــبا") == "مرحبا"


def test_normalize_full_pipeline_collapses_whitespace_and_diacritics():
    processor = ArabicTextProcessor()
    result = processor.normalize("  مَرْحَبًا   بِكَ   ")
    assert result == "مرحبا بك"


def test_normalize_can_keep_diacritics_when_disabled():
    processor = ArabicTextProcessor()
    result = processor.normalize("مَرْحَبًا", strip_diacritics=False, normalize_letters=False)
    assert result == "مَرْحَبًا"


def test_is_arabic_detects_arabic_text():
    processor = ArabicTextProcessor()
    assert processor.is_arabic("مرحبا بكم في الشركة")
    assert not processor.is_arabic("Hello World")


def test_text_direction():
    processor = ArabicTextProcessor()
    assert processor.text_direction("مرحبا") == "rtl"
    assert processor.text_direction("hello") == "ltr"
