from enterprise_ai.services.rag import split_text

def test_chunking_maintains_order():
    chunks = split_text("a b c d e f", 3, 1)
    assert chunks == ["a b c","c d e","e f"]

def test_chunking_zero_overlap():
    assert split_text("a b c d", 2, 0) == ["a b","c d"]
