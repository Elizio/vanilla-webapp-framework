#!/usr/bin/env python3
"""Verify installed package versions match requirements.txt pins.

Exits 0 if every ``name==version`` pin is installed at that exact version.
Exits 1 listing missing packages and version mismatches.

Names are compared case-insensitively after normalising ``-``/``.`` to ``_``.
"""

from __future__ import annotations

import sys
from importlib.metadata import distributions
from pathlib import Path


def normalize_name(name: str) -> str:
    """Return a comparable package name (case-insensitive; ``-``/``.`` to ``_``)."""
    return name.lower().replace("-", "_").replace(".", "_")


def installed_versions() -> dict[str, str]:
    """Map normalised distribution names to installed versions."""
    found: dict[str, str] = {}
    for dist in distributions():
        raw_name = dist.metadata.get("Name")
        if not raw_name:
            continue
        found[normalize_name(raw_name)] = dist.version
    return found


def parse_pins(requirements_path: Path) -> list[tuple[str, str]]:
    """Return ``(name, version)`` pairs from ``name==version`` lines."""
    pins: list[tuple[str, str]] = []
    with open(requirements_path) as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            if "==" not in line:
                continue
            name, version = line.split("==", 1)
            name, version = name.strip(), version.strip()
            if name and version:
                pins.append((name, version))
    return pins


def main() -> int:
    """Compare requirements.txt pins against the current environment.

    Returns:
        0 if every pin matches; 1 if the file is missing or any pin differs.
    """
    requirements_path = Path(__file__).resolve().parent.parent / "requirements.txt"
    if not requirements_path.exists():
        print(f"ERROR: {requirements_path} not found", file=sys.stderr)
        return 1

    installed = installed_versions()
    missing: list[str] = []
    mismatches: list[str] = []

    for pkg_name, expected_version in parse_pins(requirements_path):
        key = normalize_name(pkg_name)
        if key not in installed:
            missing.append(f"  {pkg_name}: not installed")
            continue
        actual = installed[key]
        if actual != expected_version:
            mismatches.append(
                f"  {pkg_name}: expected {expected_version}, got {actual}"
            )

    if missing or mismatches:
        print("ERROR: Package version mismatches found:\n", file=sys.stderr)
        if missing:
            print("Missing packages:", file=sys.stderr)
            for msg in missing:
                print(msg, file=sys.stderr)
        if mismatches:
            print("\nVersion mismatches:", file=sys.stderr)
            for msg in mismatches:
                print(msg, file=sys.stderr)
        return 1

    print("All pinned packages match requirements.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
