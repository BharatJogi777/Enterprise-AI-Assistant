import pytest
from pydantic import ValidationError
from enterprise_ai.core.config import Settings
from enterprise_ai.services.rag import split_text

def test_settings_defaults():
    cfg = Settings(_env_file=None)
    assert cfg.api_v1_prefix == "/api/v1"
    assert cfg.embedding_dimensions == 768

def test_invalid_log_level():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, log_level="VERBOSE")

def test_chunk_overlap_validation():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, chunk_size=100, chunk_overlap=100)

def test_chunking_overlap():
    assert split_text("one two three four five six", 3, 1) == [
        "one two three", "three four five", "five six"]

def test_empty_chunking():
    assert split_text(" ", 10, 2) == []
