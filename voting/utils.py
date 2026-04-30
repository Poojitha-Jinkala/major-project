import hashlib
import secrets
from datetime import datetime


def generate_vote_hash(user_id: int, election_id: int, candidate_id: int) -> str:
    """
    Generate a SHA-256 hash for a vote to ensure tamper-evident storage.
    The hash encodes the voter, election, candidate, and a random nonce.
    """
    nonce = secrets.token_hex(16)
    timestamp = datetime.now().isoformat()
    raw = f"{user_id}-{election_id}-{candidate_id}-{nonce}-{timestamp}"
    return hashlib.sha256(raw.encode()).hexdigest()


def mask_voter_id(voter_id: str) -> str:
    """Mask voter ID for display purposes: show only last 4 chars."""
    if len(voter_id) <= 4:
        return "****"
    return "*" * (len(voter_id) - 4) + voter_id[-4:]
