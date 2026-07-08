#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Generate THIRD_PARTY_LICENSES.txt from installed packages.

Usage:
    pip install pip-licenses
    python tools/generate_third_party_licenses.py
"""

import subprocess
import sys
import os


def main():
    output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               "THIRD_PARTY_LICENSES.txt")
    
    try:
        import pip_licenses
    except ImportError:
        print("pip-licenses not installed. Run: pip install pip-licenses")
        sys.exit(1)
    
    result = subprocess.run(
        [sys.executable, "-m", "pip_licenses", "--format=markdown"],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    
    if result.returncode == 0:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Third-Party Licenses\n")
            f.write("====================\n\n")
            f.write(result.stdout)
        print(f"Generated: {output_file}")
    else:
        print(f"Error: {result.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
