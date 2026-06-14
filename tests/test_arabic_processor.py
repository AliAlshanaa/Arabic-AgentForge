import unicodedata

from arabic_agentforge.nlp import ArabicTextProcessor

# Qur'anic sample (Al-Fatiha, "Bismillah"): exercises shadda, fatha/kasra/sukun,
# and the dagger alef (U+0670) used in "الرَّحْمَٰنِ".
QURAN_SAMPLE = "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ"

# Fully vocalized formal/official-style Arabic sentence.
OFFICIAL_SAMPLE = "العَرَبِيَّةُ هِيَ اللُّغَةُ الرَّسْمِيَّةُ."


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


def test_has_diacritics_true_for_quran_and_official_samples():
    processor = ArabicTextProcessor()
    assert processor.has_diacritics(QURAN_SAMPLE)
    assert processor.has_diacritics(OFFICIAL_SAMPLE)


def test_has_diacritics_detects_quranic_dagger_alef():
    processor = ArabicTextProcessor()
    assert processor.has_diacritics("الرَّحْمَٰنِ")


def test_has_diacritics_false_for_undiacritized_text():
    processor = ArabicTextProcessor()
    assert not processor.has_diacritics("اللغة العربية الرسمية")
    assert not processor.has_diacritics("Hello World")


def test_normalize_for_display_preserves_quran_sample():
    processor = ArabicTextProcessor()
    result = processor.normalize_for_display(QURAN_SAMPLE)
    assert result == unicodedata.normalize("NFKC", QURAN_SAMPLE)
    assert processor.has_diacritics(result)


def test_normalize_for_display_preserves_official_sample():
    processor = ArabicTextProcessor()
    result = processor.normalize_for_display(OFFICIAL_SAMPLE)
    assert result == unicodedata.normalize("NFKC", OFFICIAL_SAMPLE)
    assert processor.has_diacritics(result)


def test_normalize_for_matching_treats_diacritized_and_bare_text_the_same():
    processor = ArabicTextProcessor()
    diacritized = "الرَّحْمَٰنِ الرَّحِيمِ"
    bare = "الرحمن الرحيم"
    assert processor.normalize_for_matching(diacritized) == bare
    assert processor.normalize_for_matching(diacritized) == processor.normalize_for_matching(bare)
