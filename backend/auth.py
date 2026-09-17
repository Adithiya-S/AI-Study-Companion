import os
import hashlib
import hmac
import json
import base64
import time
import secrets
from typing import Optional, Dict
from .config import JWT_SECRET


def hash_password(password: str) -> str:
    """Hash password securely using PBKDF2-HMAC-SHA256 with a unique 16-byte salt."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000)
    return f"pbkdf2:{salt}:{dk.hex()}"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against salted PBKDF2 or legacy HMAC hash."""
    if hashed_password.startswith("pbkdf2:"):
        try:
            _, salt, hex_hash = hashed_password.split(":", 2)
            dk = hashlib.pbkdf2_hmac("sha256", plain_password.encode("utf-8"), salt.encode("utf-8"), 100_000)
            return hmac.compare_digest(dk.hex(), hex_hash)
        except Exception:
            return False

    # Backwards compatibility for legacy unsalted HMAC hashes
    legacy_hash = hmac.new(JWT_SECRET.encode(), plain_password.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(legacy_hash, hashed_password)


def create_token(user_id: str, email: str) -> str:
    """Create a lightweight signed JWT-compatible token with 30-day expiration."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": user_id,
        "email": email,
        "exp": int(time.time()) + (86400 * 30),  # 30 days
    }
    encoded_header = base64.urlsafe_b64encode(json.dumps(header).encode()).decode().rstrip("=")
    encoded_payload = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode().rstrip("=")
    signature = hmac.new(
        JWT_SECRET.encode(),
        f"{encoded_header}.{encoded_payload}".encode(),
        hashlib.sha256,
    ).digest()
    encoded_sig = base64.urlsafe_b64encode(signature).decode().rstrip("=")
    return f"{encoded_header}.{encoded_payload}.{encoded_sig}"


def decode_token(token: str) -> Optional[Dict]:
    """Decode and cryptographically verify a JWT Bearer token."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts

        # Verify signature
        expected_sig = hmac.new(
            JWT_SECRET.encode(),
            f"{header_b64}.{payload_b64}".encode(),
            hashlib.sha256,
        ).digest()
        actual_sig = base64.urlsafe_b64decode(sig_b64 + "==")
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        # Verify expiration
        payload = json.loads(base64.urlsafe_b64decode(payload_b64 + "==").decode())
        if payload.get("exp", 0) < time.time():
            return None

        return payload
    except Exception:
        return None
