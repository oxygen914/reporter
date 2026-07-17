#!/usr/bin/env python3
"""Collect bounded, recently modified AI memory files into a review bundle."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_MAX_FILES = 80
DEFAULT_MAX_BYTES_PER_FILE = 250_000
DEFAULT_MAX_TOTAL_BYTES = 1_500_000


@dataclass(frozen=True)
class Candidate:
    path: Path
    explicit: bool
    source: str
    role: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Collect recently modified Codex and Claude Code memory files. "
            "The output is candidate context; semantic date filtering remains required."
        )
    )
    parser.add_argument("--days", type=int, default=7, help="Rolling discovery window")
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Extra memory file or bounded directory; may be repeated",
    )
    parser.add_argument(
        "--codex-root",
        help="Codex data root; defaults to CODEX_HOME or ~/.codex",
    )
    parser.add_argument(
        "--claude-root",
        help="Claude Code data root; defaults to CLAUDE_CONFIG_DIR or ~/.claude",
    )
    parser.add_argument(
        "--claude-project",
        action="append",
        default=[],
        help=(
            "Limit Claude auto memory to a project path or encoded project key; "
            "may be repeated. Omit to scan all Claude projects"
        ),
    )
    parser.add_argument(
        "--project-root",
        help="Project root for local MEMORY.md, CLAUDE.md, and .claude memory",
    )
    parser.add_argument(
        "--now",
        help="Override current time for testing, as ISO-8601 (for example 2026-07-17T18:00:00+08:00)",
    )
    parser.add_argument("--max-files", type=int, default=DEFAULT_MAX_FILES)
    parser.add_argument(
        "--max-bytes-per-file", type=int, default=DEFAULT_MAX_BYTES_PER_FILE
    )
    parser.add_argument(
        "--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES
    )
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown"
    )
    return parser.parse_args()


def parse_now(value: str | None) -> datetime:
    if not value:
        return datetime.now().astimezone()
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.now().astimezone().tzinfo)
    return parsed


def resolve_root(raw_value: str | None, env_name: str | None, fallback: Path) -> Path:
    value = raw_value or (os.environ.get(env_name) if env_name else None)
    return Path(value).expanduser().resolve() if value else fallback.expanduser().resolve()


def encode_claude_project_path(project_path: Path) -> str:
    return "".join(
        character
        if character.isascii() and (character.isalnum() or character in "_-")
        else "-"
        for character in str(project_path)
    )


def resolve_claude_project_dirs(
    claude_root: Path, raw_projects: Iterable[str]
) -> tuple[list[Path] | None, list[str]]:
    if not raw_projects:
        return None, []

    projects_root = claude_root / "projects"
    resolved_projects: list[Path] = []
    warnings: list[str] = []
    for raw_project in raw_projects:
        supplied = Path(raw_project).expanduser()
        if supplied.is_dir() and supplied.parent.resolve() == projects_root.resolve():
            candidate = supplied.resolve()
        elif supplied.is_absolute() or supplied.exists():
            project_path = supplied.resolve()
            candidate = projects_root / encode_claude_project_path(project_path)
        else:
            candidate = projects_root / raw_project

        if candidate.is_dir():
            resolved = candidate.resolve()
            if resolved not in resolved_projects:
                resolved_projects.append(resolved)
        else:
            warnings.append(
                f"Claude project memory directory not found for {raw_project}: {candidate}"
            )

    return resolved_projects, warnings


def add_file(
    results: dict[Path, Candidate],
    path: Path,
    explicit: bool,
    source: str,
    role: str = "evidence",
) -> None:
    if path.expanduser().is_symlink():
        return
    try:
        resolved = path.expanduser().resolve()
    except OSError:
        return
    if resolved.is_file():
        previous = results.get(resolved)
        if previous is None or (explicit and not previous.explicit):
            results[resolved] = Candidate(resolved, explicit, source, role)


def add_glob(
    results: dict[Path, Candidate],
    root: Path,
    pattern: str,
    source: str,
    role: str = "evidence",
) -> None:
    if not root.is_dir():
        return
    try:
        for path in root.glob(pattern):
            add_file(results, path, False, source, role)
    except (OSError, PermissionError):
        return


def add_explicit_source(
    results: dict[Path, Candidate], raw_path: str, max_files: int
) -> list[str]:
    warnings: list[str] = []
    path = Path(raw_path).expanduser()
    if path.is_file():
        add_file(results, path, True, "explicit")
        return warnings
    if not path.is_dir():
        warnings.append(f"Explicit source not found: {path}")
        return warnings

    base_depth = len(path.resolve().parts)
    count = 0
    try:
        for current_root, directories, filenames in os.walk(path):
            current = Path(current_root)
            depth = len(current.resolve().parts) - base_depth
            if depth >= 3:
                directories[:] = []
            directories[:] = [
                name
                for name in directories
                if not name.startswith(".") and name not in {"node_modules", ".git"}
            ]
            for filename in filenames:
                if not filename.lower().endswith((".md", ".jsonl")):
                    continue
                add_file(results, current / filename, True, "explicit-directory")
                count += 1
                if count >= max_files:
                    warnings.append(
                        f"Explicit directory capped at {max_files} files: {path}"
                    )
                    return warnings
    except (OSError, PermissionError) as error:
        warnings.append(f"Could not scan explicit source {path}: {error}")
    return warnings


def discover(
    explicit_sources: Iterable[str],
    max_files: int,
    codex_root: Path,
    claude_root: Path,
    project_root: Path,
    claude_project_dirs: list[Path] | None,
) -> tuple[list[Candidate], list[str]]:
    results: dict[Path, Candidate] = {}
    warnings: list[str] = []

    add_glob(results, codex_root / "automations", "*/memory.md", "codex-automation")
    add_file(results, codex_root / "memories" / "MEMORY.md", False, "codex-memory")
    add_file(
        results,
        codex_root / "memories" / "memory_summary.md",
        False,
        "codex-memory-summary",
    )
    add_glob(
        results,
        codex_root / "memories" / "rollout_summaries",
        "*.md",
        "codex-rollout-summary",
    )

    for name in ("MEMORY.md", "memory.md"):
        add_file(results, claude_root / name, False, "claude-global")
        add_file(results, project_root / name, False, "project-memory")
        add_file(
            results,
            project_root / ".claude" / name,
            False,
            "claude-project",
        )
    add_file(
        results,
        claude_root / "CLAUDE.md",
        False,
        "claude-global-context",
        "context",
    )
    add_file(
        results,
        project_root / "CLAUDE.md",
        False,
        "claude-project-context",
        "context",
    )
    add_file(
        results,
        project_root / ".claude" / "CLAUDE.md",
        False,
        "claude-project-context",
        "context",
    )
    add_glob(results, claude_root / "memory", "*.md", "claude-global-memory")
    add_glob(results, claude_root / "memories", "*.md", "claude-global-memory")
    if claude_project_dirs is None:
        add_glob(
            results,
            claude_root / "projects",
            "*/memory/*.md",
            "claude-project-memory",
        )
    else:
        for claude_project_dir in claude_project_dirs:
            add_glob(
                results,
                claude_project_dir / "memory",
                "*.md",
                "claude-project-memory",
            )
    add_glob(
        results,
        project_root / ".claude" / "memory",
        "*.md",
        "claude-project-local-memory",
    )
    add_glob(
        results,
        project_root / ".claude" / "memories",
        "*.md",
        "claude-project-local-memory",
    )

    for raw_path in explicit_sources:
        warnings.extend(add_explicit_source(results, raw_path, max_files))

    return list(results.values()), warnings


def read_limited(path: Path, byte_limit: int) -> tuple[str, bool, str | None]:
    try:
        with path.open("rb") as handle:
            data = handle.read(byte_limit + 1)
    except (OSError, PermissionError) as error:
        return "", False, str(error)
    truncated = len(data) > byte_limit
    if truncated:
        data = data[:byte_limit]
    return data.decode("utf-8", errors="replace"), truncated, None


def collect(args: argparse.Namespace) -> dict[str, object]:
    if args.days <= 0:
        raise ValueError("--days must be greater than zero")
    if args.max_files <= 0 or args.max_bytes_per_file <= 0 or args.max_total_bytes <= 0:
        raise ValueError("file and byte limits must be greater than zero")

    now = parse_now(args.now)
    since = now - timedelta(days=args.days)
    user_root = Path.home()
    codex_root = resolve_root(args.codex_root, "CODEX_HOME", user_root / ".codex")
    claude_root = resolve_root(
        args.claude_root, "CLAUDE_CONFIG_DIR", user_root / ".claude"
    )
    project_root = resolve_root(args.project_root, None, Path.cwd())
    claude_project_dirs, project_warnings = resolve_claude_project_dirs(
        claude_root, args.claude_project
    )
    candidates, warnings = discover(
        args.source,
        args.max_files,
        codex_root,
        claude_root,
        project_root,
        claude_project_dirs,
    )
    warnings = project_warnings + warnings
    selected: list[tuple[Candidate, datetime]] = []
    claude_candidates = sum(
        1
        for candidate in candidates
        if candidate.source.startswith("claude-") and candidate.role == "evidence"
    )

    for candidate in candidates:
        try:
            modified = datetime.fromtimestamp(
                candidate.path.stat().st_mtime, tz=timezone.utc
            ).astimezone(now.tzinfo)
        except (OSError, PermissionError) as error:
            warnings.append(f"Could not stat {candidate.path}: {error}")
            continue
        if candidate.explicit or modified >= since:
            selected.append((candidate, modified))

    selected_before_limits = len(selected)
    claude_selected = sum(
        1
        for candidate, _ in selected
        if candidate.source.startswith("claude-") and candidate.role == "evidence"
    )
    if claude_candidates and not claude_selected:
        warnings.append(
            f"Found {claude_candidates} Claude Code memory file(s), but none were modified "
            f"within the last {args.days} day(s); use --source or a larger --days value if needed"
        )

    selected.sort(
        key=lambda item: (not item[0].explicit, -item[1].timestamp())
    )
    if len(selected) > args.max_files:
        warnings.append(
            f"Candidate list capped at {args.max_files} files; {len(selected) - args.max_files} omitted"
        )
        selected = selected[: args.max_files]

    files: list[dict[str, object]] = []
    total_bytes = 0
    for candidate, modified in selected:
        remaining = args.max_total_bytes - total_bytes
        if remaining <= 0:
            warnings.append("Total byte limit reached; remaining files omitted")
            break
        limit = min(args.max_bytes_per_file, remaining)
        content, truncated, error = read_limited(candidate.path, limit)
        if error:
            warnings.append(f"Could not read {candidate.path}: {error}")
            continue
        consumed = len(content.encode("utf-8"))
        total_bytes += consumed
        files.append(
            {
                "path": str(candidate.path),
                "source": candidate.source,
                "role": candidate.role,
                "explicit": candidate.explicit,
                "modified_at": modified.isoformat(timespec="seconds"),
                "truncated": truncated,
                "content": content,
            }
        )
        if truncated:
            warnings.append(f"File truncated at {limit} bytes: {candidate.path}")

    return {
        "generated_at": now.isoformat(timespec="seconds"),
        "discovery_since": since.isoformat(timespec="seconds"),
        "roots": {
            "codex": str(codex_root),
            "claude": str(claude_root),
            "project": str(project_root),
            "claude_projects": (
                [str(path) for path in claude_project_dirs]
                if claude_project_dirs is not None
                else ["*"]
            ),
        },
        "discovery_stats": {
            "candidates_total": len(candidates),
            "selected_before_limits": selected_before_limits,
            "claude_candidates": claude_candidates,
            "claude_selected": claude_selected,
            "files_returned": len(files),
        },
        "discovery_note": (
            "Modification time selected candidate files only. Filter individual work items "
            "using dates and evidence inside their content."
        ),
        "files": files,
        "warnings": warnings,
    }


def render_markdown(bundle: dict[str, object]) -> str:
    roots = bundle["roots"]
    stats = bundle["discovery_stats"]
    lines = [
        "# Report memory candidate bundle",
        "",
        f"- Generated at: {bundle['generated_at']}",
        f"- Discovery since: {bundle['discovery_since']}",
        f"- Codex root: {roots['codex']}",
        f"- Claude Code root: {roots['claude']}",
        f"- Project root: {roots['project']}",
        f"- Claude Code project scope: {', '.join(roots['claude_projects'])}",
        f"- Claude Code candidates: {stats['claude_candidates']}",
        f"- Claude Code selected by time: {stats['claude_selected']}",
        f"- Note: {bundle['discovery_note']}",
    ]
    warnings = bundle["warnings"]
    if warnings:
        lines.extend(["", "## Warnings", ""])
        lines.extend(f"- {warning}" for warning in warnings)
    for index, item in enumerate(bundle["files"], start=1):
        content = str(item["content"]).rstrip()
        fence = "```"
        while fence in content:
            fence += "`"
        lines.extend(
            [
                "",
                f"## Source {index}: {item['path']}",
                "",
                f"- Type: {item['source']}",
                f"- Role: {item['role']}",
                f"- Modified at: {item['modified_at']}",
                f"- Explicit: {str(item['explicit']).lower()}",
                f"- Truncated: {str(item['truncated']).lower()}",
                "",
                f"{fence}text",
                content,
                fence,
            ]
        )
    if not bundle["files"]:
        lines.extend(["", "No candidate memory files were found."])
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    try:
        bundle = collect(args)
    except (ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if args.format == "json":
        json.dump(bundle, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        sys.stdout.write(render_markdown(bundle))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
