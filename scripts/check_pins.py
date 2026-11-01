#!/usr/bin/env python3
"""
Verify that installed package versions match requirements.txt pins.

Exits 0 if all pinned packages are installed at the exact version.
Exits 1 if any mismatch or missing package is found.
"""
import sys
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path


def normalize_name(name: str) -> str:
    """Normalize package name (case-insensitive, - to _)."""
    return name.lower().replace("-", "_").replace(".", "_")


def main():
    requirements_path = Path(__file__).parent.parent / "requirements.txt"
    
    if not requirements_path.exists():
        print(f"ERROR: {requirements_path} not found", file=sys.stderr)
        return 1
    
    mismatches = []
    missing = []
    
    with open(requirements_path) as f:
        for line in f:
            line = line.strip()
            # Skip comments, empty lines, and -r includes
            if not line or line.startswith("#") or line.startswith("-r"):
                continue
            
            # Parse name==version
            if "==" not in line:
                continue
            
            parts = line.split("==")
            if len(parts) != 2:
                continue
            
            pkg_name = parts[0].strip()
            expected_version = parts[1].strip()
            
            # Get installed version
            try:
                installed_version = version(pkg_name)
            except PackageNotFoundError:
                missing.append(f"  {pkg_name}: not installed")
                continue
            
            # Compare versions
            if installed_version != expected_version:
                mismatches.append(
                    f"  {pkg_name}: expected {expected_version}, "
                    f"got {installed_version}"
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
    
    print("✓ All pinned packages match requirements.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
