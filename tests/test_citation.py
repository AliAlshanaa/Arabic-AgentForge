from arabic_agentforge.guards import Citation, CitationEnforcer


def test_extract_markers():
    enforcer = CitationEnforcer()
    assert enforcer.extract_markers("النص يستشهد بـ [1] و [2].") == [1, 2]
    assert enforcer.extract_markers("لا استشهاد هنا") == []


def test_has_citations():
    enforcer = CitationEnforcer()
    assert enforcer.has_citations("معلومة موثقة [1]")
    assert not enforcer.has_citations("معلومة بدون مصدر")


def test_validate_accepts_in_range_markers():
    enforcer = CitationEnforcer()
    sources = [Citation(source="A"), Citation(source="B")]
    assert enforcer.validate("نص يحتوي على [1] و [2]", sources)


def test_validate_rejects_out_of_range_markers():
    enforcer = CitationEnforcer()
    sources = [Citation(source="A")]
    assert not enforcer.validate("نص يحتوي على [2]", sources)


def test_validate_rejects_when_no_markers():
    enforcer = CitationEnforcer()
    sources = [Citation(source="A")]
    assert not enforcer.validate("نص بدون استشهاد", sources)


def test_format_sources():
    enforcer = CitationEnforcer()
    sources = [Citation(source="ERPNext Issue #442"), Citation(source="HR Policy v2")]
    assert enforcer.format_sources(sources) == "[1] ERPNext Issue #442\n[2] HR Policy v2"
