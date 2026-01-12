import json
import os

# Define the path to the external data file
MANIFEST_FILE = os.path.join("data", "manifest.json")


def load_trusted_hashes():
    """Reads the list of trusted SHA-256 hashes from the data folder."""
    if not os.path.exists(MANIFEST_FILE):
        return []

    try:
        with open(MANIFEST_FILE, "r") as f:
            data = json.load(f)
            # Returns the list of hashes, or an empty list if not found
            return data.get("trusted_hashes", [])
    except (json.JSONDecodeError, IOError):
        # Gracefully handle missing files or corrupted JSON
        return []


def is_hash_trusted(file_hash):
    """Checks if the provided hash exists in our manifest data."""
    trusted_list = load_trusted_hashes()
    return file_hash in trusted_list
