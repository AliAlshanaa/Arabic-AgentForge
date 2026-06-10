from arabic_agentforge.nlp import Dialect, DialectHandler


def test_detect_gulf_dialect():
    handler = DialectHandler()
    assert handler.detect("وش تبي اليوم") == Dialect.GULF


def test_detect_egyptian_dialect():
    handler = DialectHandler()
    assert handler.detect("عايز اروح دلوقتي") == Dialect.EGYPTIAN


def test_detect_levantine_dialect():
    handler = DialectHandler()
    assert handler.detect("بدي روح هلق") == Dialect.LEVANTINE


def test_detect_msa_when_no_markers_present():
    handler = DialectHandler()
    assert handler.detect("أرغب في الذهاب الآن") == Dialect.MSA


def test_normalize_to_msa_replaces_known_dialect_words():
    handler = DialectHandler()
    assert handler.normalize_to_msa("وش تبي") == "ما تريد"
    assert handler.normalize_to_msa("عايز اروح") == "أريد اروح"
