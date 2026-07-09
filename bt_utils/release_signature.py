import json
import os
from typing import Optional

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


def load_private_key(path: str) -> Optional[RSAPrivateKey]:
    try:
        with open(path, "rb") as f:
            return serialization.load_pem_private_key(f.read(), password=None)
    except Exception:
        return None


def load_public_key(path: str) -> Optional[RSAPublicKey]:
    try:
        with open(path, "rb") as f:
            key = serialization.load_pem_public_key(f.read())
            if isinstance(key, RSAPublicKey):
                return key
        return None
    except Exception:
        return None


def sign_manifest(manifest_path: str, private_key_path: str, output_path: str) -> bool:
    private_key = load_private_key(private_key_path)
    if private_key is None:
        return False

    with open(manifest_path, "rb") as f:
        data = f.read()

    signature = private_key.sign(data, padding.PKCS1v15(), hashes.SHA256())

    with open(output_path, "wb") as f:
        f.write(signature)
    return True


def verify_manifest(manifest_path: str, sig_path: str, public_key_path: str) -> bool:
    public_key = load_public_key(public_key_path)
    if public_key is None:
        return False

    try:
        with open(manifest_path, "rb") as f:
            data = f.read()
        with open(sig_path, "rb") as f:
            signature = f.read()
        public_key.verify(signature, data, padding.PKCS1v15(), hashes.SHA256())
        return True
    except Exception:
        return False


def generate_key_pair(private_key_path: str, public_key_path: str) -> bool:
    try:
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.backends import default_backend

        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )

        os.makedirs(os.path.dirname(private_key_path), exist_ok=True)
        with open(private_key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))

        os.makedirs(os.path.dirname(public_key_path), exist_ok=True)
        public_key = private_key.public_key()
        with open(public_key_path, "wb") as f:
            f.write(public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            ))

        return True
    except Exception:
        return False
