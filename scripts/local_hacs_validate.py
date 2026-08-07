#!/usr/bin/env python3
"""Local HACS compliance checks (parity with CI HACS validation)."""

from __future__ import annotations

import json
import os
import sys

DOMAIN = "delonghi_dehumidifier_api"


def validate_hacs() -> bool:
    errors: list[str] = []

    if not os.path.exists("hacs.json"):
        errors.append("Missing hacs.json in root directory.")
    else:
        try:
            with open("hacs.json", encoding="utf-8") as f:
                hacs = json.load(f)
            if "name" not in hacs:
                errors.append("hacs.json: 'name' is missing.")
        except Exception as e:
            errors.append(f"hacs.json: Invalid JSON: {e}")

    manifest_path = f"custom_components/{DOMAIN}/manifest.json"
    if not os.path.exists(manifest_path):
        errors.append(f"Missing {manifest_path}")
    else:
        try:
            with open(manifest_path, encoding="utf-8") as f:
                manifest = json.load(f)
            required = ["domain", "name", "documentation", "version", "codeowners"]
            errors.extend(
                f"manifest.json: '{key}' is missing."
                for key in required
                if key not in manifest
            )
        except Exception as e:
            errors.append(f"manifest.json: Invalid JSON: {e}")

    if errors:
        for err in errors:
            sys.stderr.write(f"HACS VALIDATION ERROR: {err}\n")
        return False
    return True


if __name__ == "__main__" and not validate_hacs():
    sys.exit(1)
