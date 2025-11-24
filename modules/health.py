"""Startup health checks to ensure the system is ready before UI loads."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

import config
from modules.backup_manager import ensure_backup_dir
from modules.db import get_conn
from modules.logger import log
from modules import models


@dataclass
class CheckResult:
    name: str
    ok: bool
    message: str
    critical: bool = False


def run_preflight_checks() -> dict:
    """
    Execute a battery of checks before booting the UI.
    Returns summary dict: {"ok": bool, "checks": List[CheckResult]}
    """
    checks: List[CheckResult] = []

    def record(name: str, ok: bool, message: str, critical: bool = False):
        checks.append(CheckResult(name, ok, message, critical))
        level = log.info if ok else log.error
        level(f"[preflight] {name}: {message}")

    # 1. Configuration sanity
    try:
        cfg = config.load_config()
        required_root_keys = {"database", "logging", "shop_info"}
        missing = required_root_keys - cfg.keys()
        if missing:
            record(
                "Configuration",
                False,
                f"Missing keys: {', '.join(sorted(missing))}",
                critical=True,
            )
        else:
            record("Configuration", True, "Config file loaded")
    except Exception as exc:
        record("Configuration", False, f"Failed to load config: {exc}", critical=True)

    # 2. Database connectivity + schema
    try:
        with get_conn() as conn:
            conn.execute("SELECT 1")
        record("Database connection", True, "Connection established")
    except Exception as exc:
        record("Database connection", False, f"Cannot open DB: {exc}", critical=True)

    try:
        models.check_schema()
        record("Schema check", True, "Schema is up to date")
    except Exception as exc:
        record("Schema check", False, f"Failed to validate schema: {exc}", critical=True)

    # 3. Backup directory
    try:
        ensure_backup_dir()
        backups_path = Path(__file__).resolve().parents[1] / "backups"
        record("Backups directory", True, f"Ready at {backups_path}")
    except Exception as exc:
        record("Backups directory", False, f"Cannot access backups dir: {exc}")

    # 4. Log directory writeability
    log_dir = Path(config.LOG_DIR)
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        test_file = log_dir / ".write_test"
        test_file.write_text("ok")
        test_file.unlink(missing_ok=True)
        record("Logging path", True, f"Writable at {log_dir}")
    except Exception as exc:
        record("Logging path", False, f"Not writable: {exc}")

    overall_ok = all(c.ok or not c.critical for c in checks)
    return {"ok": overall_ok, "checks": checks}

