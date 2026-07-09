import hashlib
import json
import os
from typing import List

from .update_paths import get_public_key_path


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(65536)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def verify_package_sha256(path: str, expected: str) -> bool:
    return sha256_file(path).lower() == expected.lower()


def verify_manifest_signature(manifest_path: str, sig_path: str, public_key_path: str = "") -> bool:
    if not public_key_path:
        public_key_path = get_public_key_path()

    if not os.path.exists(public_key_path):
        return False

    try:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding, rsa
        from cryptography.hazmat.primitives.serialization import load_pem_public_key

        with open(public_key_path, "rb") as f:
            public_key = load_pem_public_key(f.read())

        with open(manifest_path, "rb") as f:
            manifest_data = f.read()

        with open(sig_path, "rb") as f:
            signature = f.read()

        if isinstance(public_key, rsa.RSAPublicKey):
            public_key.verify(
                signature,
                manifest_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        return False
    except Exception:
        return False


def verify_extracted_files(root_dir: str, manifest: dict) -> List[str]:
    errors = []
    files = manifest.get("files", [])

    for entry in files:
        rel_path = entry.get("path", "")
        expected_hash = entry.get("sha256", "")
        full_path = os.path.join(root_dir, rel_path)

        if not os.path.exists(full_path):
            errors.append(f"缺少文件: {rel_path}")
            continue

        actual_hash = sha256_file(full_path)
        if actual_hash.lower() != expected_hash.lower():
            errors.append(f"文件 hash 不匹配: {rel_path}")

    return errors


def safe_extract_zip(zip_path: str, extract_dir: str):
    import zipfile
    base = os.path.abspath(extract_dir)

    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            target = os.path.abspath(os.path.join(extract_dir, member.filename))
            if not target.startswith(base + os.sep):
                raise ValueError(f"非法路径: {member.filename}")
            zf.extract(member, extract_dir)


def extract_and_verify(zip_path: str, extract_dir: str, manifest: dict) -> List[str]:
    os.makedirs(extract_dir, exist_ok=True)

    safe_extract_zip(zip_path, extract_dir)

    return verify_extracted_files(extract_dir, manifest)
