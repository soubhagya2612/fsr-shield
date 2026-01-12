import hashlib
import pytest
from src.security import calculate_sha256, verify_file


def test_hash_calculation(tmp_path):
    """Test if calculate_sha256 matches a fresh local calculation."""
    p = tmp_path / "test_file.bin"
    content = b"FSR-Shield-Test"
    p.write_bytes(content)

    expected_hash = hashlib.sha256(content).hexdigest()
    hash_result = calculate_sha256(str(p))

    assert hash_result == expected_hash


def test_verify_file_integrity_gate(tmp_path):
    """Tests the integrity check used as a security gate in main.py."""
    p = tmp_path / "integrity.dll"
    p.write_bytes(b"safe_data")

    correct_hash = calculate_sha256(str(p))

    # Test success case
    is_valid, _ = verify_file(str(p), correct_hash)
    assert is_valid is True

    # Test failure case
    is_valid, _ = verify_file(str(p), "tampered_hash")
    assert is_valid is False
