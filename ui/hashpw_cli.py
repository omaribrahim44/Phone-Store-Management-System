#!/usr/bin/env python3
# hash_pw.py - improved
"""
Generate salted sha256 password hashes and optionally verify them.

Usage:
    python hash_pw.py             # interactive: prompts for new password (with confirmation)
    python hash_pw.py --password  # read password from argument (not recommended)
    python hash_pw.py --verify <stored_hash>   # verify a plaintext password against stored hash
    python hash_pw.py --sql <username>         # prints SQL UPDATE statement to set password for username

Note: The hashing format is: salt$hexhash
"""

import os
import hashlib
import argparse
import getpass
from typing import Tuple


def hash_password(plain: str) -> str:
    """Return salted sha256 hash in format: salt$hash"""
    salt = os.urandom(8).hex()
    h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
    return f"{salt}${h}"


def verify_password(stored: str, plaintext: str) -> bool:
    """Verify plaintext against stored 'salt$hash' string."""
    try:
        salt, h = stored.split("$", 1)
        return hashlib.sha256((salt + plaintext).encode("utf-8")).hexdigest() == h
    except Exception:
        return False


def prompt_password(confirm: bool = True) -> str:
    """Prompt user for password (hidden). Optionally confirm."""
    pw = getpass.getpass("Enter password: ").strip()
    if confirm:
        pw2 = getpass.getpass("Confirm password: ").strip()
        if pw != pw2:
            raise ValueError("Passwords do not match.")
    if not pw:
        raise ValueError("Password cannot be empty.")
    return pw


def main():
    parser = argparse.ArgumentParser(description="Generate / verify salted sha256 password hashes.")
    parser.add_argument("--password", "-p", help="Provide password via argument (less secure).")
    parser.add_argument("--verify", "-v", help="Verify provided stored hash. Usage: --verify <stored_hash>")
    parser.add_argument("--sql", "-s", nargs='?', const="admin", help="Print SQL UPDATE for given username (default 'admin').")
    parser.add_argument("--no-confirm", action="store_true", help="Do not ask to re-enter password (useful for scripts).")
    args = parser.parse_args()

    try:
        if args.verify:
            # verify flow: ask for plaintext then compare
            stored = args.verify.strip()
            pw = args.password or getpass.getpass("Password to verify: ")
            ok = verify_password(stored, pw)
            print("Verification result:", "MATCH" if ok else "NO MATCH")
            return

        if args.password:
            pw = args.password
            if not args.no_confirm:
                # still ask confirmation to be safe
                pw2 = getpass.getpass("Confirm password: ")
                if pw != pw2:
                    print("Error: passwords do not match.")
                    return
        else:
            pw = prompt_password(confirm=not args.no_confirm)

        hashed = hash_password(pw)
        print("\nHashed value (format salt$hash):")
        print(hashed)

        if args.sql is not None:
            username = args.sql
            # produce a safe SQL snippet (parameterized recommended when running in code)
            print("\nSQL (example) - use parameterized query when possible:")
            print(f"UPDATE users SET password = '{hashed}', created_at = CURRENT_TIMESTAMP WHERE username = '{username}';")
            print("# NOTE: prefer using parameterized queries in scripts to avoid SQL injection.")

    except ValueError as ve:
        print("Error:", ve)
    except KeyboardInterrupt:
        print("\nCancelled by user.")


if __name__ == "__main__":
    main()
