import hashlib
import json
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from backend.services.automation_logger import (
    record_automation_execution
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BASELINE_DIR = PROJECT_ROOT / "automation" / "integrity_checker"
BASELINE_FILE = BASELINE_DIR / "baseline.json"

MONITORED_DIRECTORIES = [
    PROJECT_ROOT / "backend",
    PROJECT_ROOT / "frontend",
]

EXCLUDED_PARTS = {
    "__pycache__",
    ".git",
    "venv",
}


def _is_monitored_file(path: Path) -> bool:
    """
    Determine whether a file belongs to the
    SecureSphere source-code integrity baseline.
    """

    if not path.is_file():
        return False

    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False

    # Monitor source/configuration files only.
    allowed_extensions = {
        ".py",
        ".html",
        ".js",
        ".css",
        ".json",
        ".sql",
    }

    return path.suffix.lower() in allowed_extensions


def get_monitored_files():
    """
    Return all source files included in the
    SecureSphere integrity baseline.
    """

    files = []

    for directory in MONITORED_DIRECTORIES:

        if not directory.exists():
            continue

        for path in directory.rglob("*"):

            if _is_monitored_file(path):
                files.append(path)

    return sorted(files)


def calculate_sha256(path: Path) -> str:
    """
    Calculate SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with path.open("rb") as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b"",
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


def create_integrity_baseline():
    """
    Create a SHA-256 baseline for monitored
    SecureSphere source files.
    """

    BASELINE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    baseline = {
        "created_at": datetime.utcnow().isoformat(),
        "project_root": str(PROJECT_ROOT),
        "files": {},
    }

    for path in get_monitored_files():

        relative_path = str(
            path.relative_to(PROJECT_ROOT)
        )

        baseline["files"][relative_path] = (
            calculate_sha256(path)
        )

    BASELINE_FILE.write_text(
        json.dumps(
            baseline,
            indent=2,
        )
    )

    return baseline


def check_integrity(
    db: Session | None = None,
):
    """
    Compare current source files against the
    stored SHA-256 baseline.

    If no baseline exists, create one and
    return BASELINE_CREATED.
    """

    if not BASELINE_FILE.exists():

        baseline = create_integrity_baseline()

        result = {
            "automation_name": "INTEGRITY_CHECK",
            "execution_time": datetime.utcnow().isoformat(),
            "status": "BASELINE_CREATED",
            "summary": (
                "Integrity baseline created for "
                f"{len(baseline['files'])} monitored files."
            ),
            "metrics": {
                "baseline_files": len(
                    baseline["files"]
                ),
                "modified_files": 0,
                "missing_files": 0,
                "new_files": 0,
            },
            "findings": [],
        }

    else:

        baseline = json.loads(
            BASELINE_FILE.read_text()
        )

        baseline_files = baseline.get(
            "files",
            {},
        )

        current_files = {}

        for path in get_monitored_files():

            relative_path = str(
                path.relative_to(PROJECT_ROOT)
            )

            current_files[relative_path] = (
                calculate_sha256(path)
            )

        modified_files = sorted(
            path
            for path in baseline_files
            if path in current_files
            and baseline_files[path]
            != current_files[path]
        )

        missing_files = sorted(
            path
            for path in baseline_files
            if path not in current_files
        )

        new_files = sorted(
            path
            for path in current_files
            if path not in baseline_files
        )

        findings = []

        if modified_files:
            findings.append(
                f"{len(modified_files)} monitored file(s) modified."
            )

        if missing_files:
            findings.append(
                f"{len(missing_files)} baseline file(s) missing."
            )

        if new_files:
            findings.append(
                f"{len(new_files)} new source file(s) detected."
            )

        if not findings:
            status = "INTEGRITY_OK"
            summary = (
                "No unauthorized source-file changes "
                "were detected."
            )
        else:
            status = "CHANGES_DETECTED"
            summary = (
                "Source-file integrity changes "
                "were detected."
            )

        result = {
            "automation_name": "INTEGRITY_CHECK",
            "execution_time": datetime.utcnow().isoformat(),
            "status": status,
            "summary": summary,
            "metrics": {
                "baseline_files": len(baseline_files),
                "current_files": len(current_files),
                "modified_files": len(
                    modified_files
                ),
                "missing_files": len(
                    missing_files
                ),
                "new_files": len(
                    new_files
                ),
            },
            "findings": findings,
            "modified_files": modified_files,
            "missing_files": missing_files,
            "new_files": new_files,
        }

    if db is not None:

        log_status = (
            "SUCCESS"
            if result["status"]
            in {
                "BASELINE_CREATED",
                "INTEGRITY_OK",
                "CHANGES_DETECTED",
            }
            else "FAILED"
        )

        record_automation_execution(
            db=db,
            automation_name=result[
                "automation_name"
            ],
            status=log_status,
            output_summary=result[
                "summary"
            ],
            output_data=result,
            input_source=(
                "SecureSphere source directories"
            ),
        )

        db.commit()

    return result
