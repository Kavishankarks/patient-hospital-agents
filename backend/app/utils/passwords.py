import binascii
import hashlib
import secrets

PBKDF2_ITERATIONS = 120_000

def normalize_mobile(mobile: str) -> str:
    return ''.join(ch for ch in mobile if ch.isdigit() or ch == '+')

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), PBKDF2_ITERATIONS)
    return f'{salt}${binascii.hexlify(dk).decode("ascii")}'

def verify_password(password: str, stored: str) -> bool:
    try:
        salt, expected_hex = stored.split('$', 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), PBKDF2_ITERATIONS)
    return secrets.compare_digest(binascii.hexlify(dk).decode('ascii'), expected_hex)
