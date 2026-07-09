#!/usr/bin/env python
"""
签名 manifest.json -> manifest.sig
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bt_utils.release_signature import sign_manifest


def main():
    parser = argparse.ArgumentParser(description="Sign manifest.json")
    parser.add_argument("--manifest", required=True, help="manifest.json 路径")
    parser.add_argument("--private-key", required=True, help="私钥路径")
    parser.add_argument("--output", default="", help="输出签名文件路径")
    args = parser.parse_args()

    manifest_path = os.path.normpath(args.manifest)
    private_key_path = os.path.normpath(args.private_key)

    if not os.path.exists(manifest_path):
        print(f"Error: manifest not found: {manifest_path}")
        exit(1)
    if not os.path.exists(private_key_path):
        print(f"Error: private key not found: {private_key_path}")
        exit(1)

    output = args.output or os.path.join(os.path.dirname(manifest_path), "manifest.sig")

    if sign_manifest(manifest_path, private_key_path, output):
        print(f"Signed: {manifest_path} -> {output}")
    else:
        print("Error: signing failed")
        exit(1)


if __name__ == "__main__":
    main()
