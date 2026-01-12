import hashlib


def calculate_sha256(file_path):
    """Calculate the SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read the file in chunks to handle large files efficiently
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def verify_file(file_path, expected_hash):
    """Compare calculated hash with the expected one."""
    actual_hash = calculate_sha256(file_path)
    if actual_hash.lower() == expected_hash.lower():
        return True, actual_hash
    return False, actual_hash
