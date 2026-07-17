# Collector usage and validation

Use `scripts/collect_report_context.py` to discover bounded Codex and Claude Code memory candidates for daily, weekly, or monthly reports. Prefer `--format json` for agent consumption.

## Important options

- `--days N`: set the rolling discovery window. Choose a window that covers the exact daily, weekly, or monthly report range; semantic filtering still happens after collection.
- `--source PATH`: include an explicit file or bounded directory; repeat as needed.
- `--codex-root PATH`: override `CODEX_HOME` or `~/.codex`.
- `--claude-root PATH`: override `CLAUDE_CONFIG_DIR` or `~/.claude`.
- `--project-root PATH`: select project-local `MEMORY.md`, `CLAUDE.md`, and `.claude` files.
- `--claude-project PATH_OR_KEY`: limit Claude auto memory to one project; repeat to include several projects.
- `--format json`: produce machine-readable output.

## Validation commands

Run the Codex structure check and compile the collector:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" <skill-folder>
PYTHONPYCACHEPREFIX=/tmp/reporter-pycache python3 -m py_compile <skill-folder>/scripts/collect_report_context.py
```

Run a normal Codex-memory path:

```bash
python3 <skill-folder>/scripts/collect_report_context.py \
  --days 7 --source <memory-file> --format json
```

Repeat the normal path with representative daily and monthly windows:

```bash
python3 <skill-folder>/scripts/collect_report_context.py \
  --days 1 --source <memory-file> --format json
python3 <skill-folder>/scripts/collect_report_context.py \
  --days 31 --source <memory-file> --format json
```

Run a Claude project-scoped path and confirm that unrelated projects are absent:

```bash
python3 <skill-folder>/scripts/collect_report_context.py \
  --days 30 --claude-project <project-path> --format json
```

Run a Markdown path with a source that contains triple-backtick code blocks. Confirm that the outer fence grows to four or more backticks:

```bash
python3 <skill-folder>/scripts/collect_report_context.py \
  --days 7 --source <markdown-with-code-fences>
```

Run an error path and confirm a nonzero exit with a clear message:

```bash
python3 <skill-folder>/scripts/collect_report_context.py --days 0
```
