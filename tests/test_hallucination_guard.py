from arabic_agentforge.guards import ArabicHallucinationGuard, Citation


def test_passes_with_valid_citation_and_high_confidence():
    guard = ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85)
    sources = [Citation(source="ERPNext Issue #442")]

    result = guard.check("تم إنشاء التذكرة بنجاح [1].", confidence=0.95, sources=sources)

    assert result.passed is True


def test_fails_when_confidence_below_threshold():
    guard = ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85)
    sources = [Citation(source="ERPNext Issue #442")]

    result = guard.check("تم إنشاء التذكرة بنجاح [1].", confidence=0.5, sources=sources)

    assert result.passed is False
    assert "confidence" in result.reason


def test_passes_when_citation_required_but_no_sources():
    guard = ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85)

    result = guard.check("تم إنشاء التذكرة بنجاح.", confidence=0.95, sources=[])

    assert result.passed is True


def test_fails_when_citation_required_with_sources_but_missing_markers():
    guard = ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85)
    sources = [Citation(source="ERPNext Issue #442")]

    result = guard.check("تم إنشاء التذكرة بنجاح.", confidence=0.95, sources=sources)

    assert result.passed is False
    assert "citation" in result.reason


def test_fails_when_citation_index_out_of_range():
    guard = ArabicHallucinationGuard(citation_required=True, confidence_threshold=0.85)
    sources = [Citation(source="ERPNext Issue #442")]

    result = guard.check("تم إنشاء التذكرة بنجاح [2].", confidence=0.95, sources=sources)

    assert result.passed is False


def test_citation_not_required_skips_citation_check():
    guard = ArabicHallucinationGuard(citation_required=False, confidence_threshold=0.5)

    result = guard.check("تم إنشاء التذكرة بنجاح.", confidence=0.95, sources=[])

    assert result.passed is True
