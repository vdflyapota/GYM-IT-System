import base64, os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

def get_aesgcm_from_env(app):
    key_b64 = app.config.get("AES256_KEY_BASE64")
    if not key_b64:
        raise RuntimeError("AES256_KEY_BASE64 not set")
    key = base64.b64decode(key_b64)
    if len(key) != 32:
        raise RuntimeError("AES256 key must be 32 bytes (256-bit)")
    return AESGCM(key)

def encrypt_field(app, plaintext: bytes) -> bytes:
    aesgcm = get_aesgcm_from_env(app)
    nonce = os.urandom(12)  # 96-bit nonce for AES-GCM
    ct = aesgcm.encrypt(nonce, plaintext, associated_data=None)
    return nonce + ct  # store nonce+ct together

def decrypt_field(app, data: bytes) -> bytes:
    aesgcm = get_aesgcm_from_env(app)
    nonce, ct = data[:12], data[12:]
    return aesgcm.decrypt(nonce, ct, associated_data=None)
