#!/usr/bin/env python
"""
校验 manifest.sig
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bt_utils.update_paths import get_public_key_path
from bt_utils.release_signature import verify_manifest


def main():
    parser = argparse.ArgumentParser(description="Verify manifest signature")
    parser.add_argument("--manifest", required=True, help="manifest.json 路径")
    parser.add_argument("--sig", required=True, help="manifest.sig 路径")
    parser.add_argument("--public-key", default="", help="公钥路径")
    args = parser.parse_args()

    public_key = args.public_key or get_public_key_path()

    if verify_manifest(args.manifest, args.sig, public_key):
        print("Signature verification: PASSED")
    else:
        print("Signature verification: FAILED")
        exit(1)


if __name__ == "__main__":
    main()
