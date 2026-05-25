"""
Stack backup helpers for exporting Portainer stacks to local files.
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from config import create_config_manager
from portainer_client import PortainerAPIError, PortainerClient

MAX_BACKUP_DATES = 10
SUPPORTED_STACK_TYPES = {
    1: "Swarm",
    2: "Standalone",
}


class StackBackupError(Exception):
    """Raised when exporting stacks to backup files fails."""


def default_backup_directory(base_dir: Optional[Path] = None) -> Path:
    """Return daily backup directory path."""
    backup_date = datetime.now(timezone.utc).strftime("%Y%m%d")
    parent = base_dir or (Path.cwd() / "Stacks")
    return parent / backup_date


def export_all_stacks(output_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Export all supported Portainer stacks to local files.

    Args:
        output_dir: Target directory for this export run. When omitted, a new
            timestamped directory is created under ./portainer-stack-backups.

    Returns:
        Summary dictionary describing exported, skipped, and failed stacks.
    """
    client, portainer_config = _create_client()
    backup_dir = Path(output_dir).expanduser() if output_dir else default_backup_directory()
    backup_dir = backup_dir.resolve()
    _prepare_output_directory(backup_dir)
    _prune_old_backup_dates(backup_dir.parent, keep=MAX_BACKUP_DATES)

    exported = []
    skipped = []
    failed = []
    generated_at = _timestamp()

    for stack_summary in client.get_stacks():
        stack_id = stack_summary.get("Id")
        stack_name = stack_summary.get("Name", f"stack-{stack_id}")
        stack_type = stack_summary.get("Type")

        if not isinstance(stack_id, int):
            failed.append(
                {
                    "id": stack_id,
                    "name": stack_name,
                    "reason": f"Unexpected stack identifier: {stack_id!r}",
                }
            )
            continue

        if stack_type not in SUPPORTED_STACK_TYPES:
            skipped.append(
                {
                    "id": stack_id,
                    "name": stack_name,
                    "type": stack_type,
                    "reason": f"Unsupported stack type {stack_type!r}",
                }
            )
            continue

        try:
            stack_details = client.get_stack(stack_id)
            stack_file_content = client.get_stack_file_content(stack_id)
            stack_directory, compose_filename = _write_stack_backup(
                backup_dir=backup_dir,
                stack_name=stack_name,
                stack_details=stack_details,
                stack_file_content=stack_file_content,
                generated_at=generated_at,
            )
            exported.append(
                {
                    "id": stack_id,
                    "name": stack_name,
                    "type": SUPPORTED_STACK_TYPES.get(stack_type, str(stack_type)),
                    "endpoint_id": stack_details.get("EndpointId"),
                    "directory": stack_directory.name,
                    "compose_file": compose_filename,
                }
            )
        except PortainerAPIError as e:
            failed.append(
                {
                    "id": stack_id,
                    "name": stack_name,
                    "reason": str(e),
                }
            )

    manifest = {
        "generated_at": generated_at,
        "output_dir": str(backup_dir),
        "server_url": portainer_config["server"]["url"],
        "exported_count": len(exported),
        "skipped_count": len(skipped),
        "failed_count": len(failed),
        "exported": exported,
        "skipped": skipped,
        "failed": failed,
    }
    _write_json(backup_dir / "manifest.json", manifest)
    _write_json(
        backup_dir / "status.json",
        {
            "status": "completed" if not failed else "completed_with_errors",
            "generated_at": generated_at,
            "exported_count": len(exported),
            "skipped_count": len(skipped),
            "failed_count": len(failed),
        },
    )
    return manifest


def _create_client() -> tuple[PortainerClient, Dict[str, Any]]:
    config_mgr = create_config_manager()
    portainer_config = config_mgr.get_portainer_config()

    client = PortainerClient(
        url=portainer_config["server"]["url"],
        username=portainer_config["auth"]["username"],
        password=portainer_config["auth"]["password"],
        verify_ssl=portainer_config["server"].get("verify_ssl", True),
        timeout=portainer_config.get("request_timeout", 30),
    )
    return client, portainer_config


def _prepare_output_directory(output_dir: Path) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        raise StackBackupError(f"Output path is not a directory: {output_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    for child in output_dir.iterdir():
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def _prune_old_backup_dates(parent_dir: Path, keep: int) -> None:
    if not parent_dir.exists():
        return

    dated_dirs = [
        entry for entry in parent_dir.iterdir()
        if entry.is_dir() and re.fullmatch(r"\d{8}", entry.name)
    ]
    dated_dirs.sort(key=lambda entry: entry.name, reverse=True)

    for old_dir in dated_dirs[keep:]:
        shutil.rmtree(old_dir)


def _write_stack_backup(
    backup_dir: Path,
    stack_name: str,
    stack_details: Dict[str, Any],
    stack_file_content: str,
    generated_at: str,
) -> tuple[Path, str]:
    directory_name = _sanitize_path_component(stack_name)
    stack_directory = backup_dir / directory_name
    if stack_directory.exists():
        shutil.rmtree(stack_directory)
    stack_directory.mkdir(parents=False, exist_ok=False)

    compose_filename = _compose_filename(stack_details.get("EntryPoint"))
    _write_text(stack_directory / compose_filename, stack_file_content)
    _write_json(
        stack_directory / "metadata.json",
        {
            "exported_at": generated_at,
            "stack": stack_details,
        },
    )
    return stack_directory, compose_filename


def _compose_filename(entry_point: Any) -> str:
    _ = entry_point
    return "docker-compose.yml"


def _sanitize_path_component(value: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return sanitized or "stack"


def _write_text(path: Path, content: str) -> None:
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    temp_path.replace(path)


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
