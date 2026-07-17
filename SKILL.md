---
name: reporter
description: Generate structured Chinese daily, weekly, or monthly work reports from recent Codex or Claude Code memory files, ask the user to choose the report type and detail level when unspecified, and create or update recurring Codex automations after collecting the report scope, recurrence, and execution time. Use when the user asks to write, summarize, polish, or manually generate a 日报, 周报, 月报, daily report, weekly report, monthly report, work summary, or recurring work-report automation.
---

# Work Report

Generate evidence-based Chinese daily, weekly, and monthly work reports from recent AI memory files. Invoke this Skill explicitly with `$reporter` when needed.

## Choose the run mode

- Treat requests such as “生成今天的日报”“生成本周周报” or “生成本月月报” as manual runs. Do not create an automation.
- Treat requests such as “每天自动生成日报” or “每月自动生成月报” as automation setup.
- If the request is genuinely ambiguous, ask whether to generate now or configure a recurring schedule.

## Collect preferences before execution

For an interactive manual run, collect any missing report type and detail level before reading memory or drafting. Ask one concise combined question when both are missing; offer report types `日报`、`周报`、`月报` and detail levels `精简`、`标准`、`详细`. If only one preference is missing, ask only for that preference. Do not silently choose while the user is available to answer.

Use these remaining defaults unless the user specifies otherwise:

- Date range: use the report-type defaults below; honor an explicit calendar range or phrases such as `昨天`、`上周`、`上个月` instead.
- Output: return the report in chat; write or append to a file only when requested.

Use the active timezone to resolve calendar boundaries:

- `日报`: the requested calendar day; default to today through the current time.
- `周报`: the requested calendar week; default to the rolling seven days ending now. Interpret `本周` and `上周` as calendar weeks.
- `月报`: the requested calendar month; default to the current calendar month through the current time. Interpret `上个月` as the complete previous calendar month.

Offer these detail levels:

- `精简`: 20–45 Chinese characters per item, one outcome-focused sentence.
- `标准`: 40–90 Chinese characters per item, usually covering action, result, and status.
- `详细`: 80–150 Chinese characters per item, optionally including key difficulty, blocker, or next step.

If an unattended automation run has no configured report type or level, infer the type from an unambiguous task name or prompt; otherwise use `周报` and `标准` and state both fallbacks in the result. Do not pause an unattended run to ask a question.

## Collect recent memory

1. Prefer paths explicitly supplied by the user.
2. Otherwise run `scripts/collect_report_context.py` from this Skill directory with `--format json` and a discovery window that covers the selected report: normally `--days 1` for a current-day report, `--days 7` for a rolling weekly report, or the inclusive calendar-day count up to 31 for one monthly period. Add a small discovery buffer when the exact boundary may be missed by file modification time. Use `--source PATH` repeatedly for extra files or directories. Prefer JSON for agent consumption; use Markdown only for human inspection. The script only builds a candidate bundle; it does not decide which claims belong in the report.
3. Inspect the returned source paths and warnings. Read a source directly if it was truncated or if exact context is needed.
4. Filter content by dates written inside the memory, session, or work item. File modification time is only a discovery signal and is not proof that every entry belongs to the requested report range.

The collector supports:

- Codex automation memory under `~/.codex/automations/*/memory.md`;
- Codex memory indexes and recent rollout summaries under `~/.codex/memories/`;
- Claude Code auto memory under `~/.claude/projects/<project-key>/memory/*.md`;
- Claude Code global or project-local `MEMORY.md`, `memory.md`, `CLAUDE.md`, `.claude/memory/*.md`, and `.claude/memories/*.md`;
- user-provided memory files or bounded directories.

Honor `CLAUDE_CONFIG_DIR` when it is set. Use `--claude-root PATH` for a custom Claude Code data directory and `--project-root PATH` for project-local files. For a project-specific report, also pass `--claude-project PROJECT_PATH_OR_KEY`; repeat it to include multiple Claude projects. Omit it only when the report should aggregate all Claude projects.

Claude Code auto memory commonly uses an index file such as `memory/MEMORY.md` plus sibling topic files with YAML frontmatter. Treat both as Markdown evidence. Treat `CLAUDE.md` as background context only; it must not independently support a report item. Use file modification time only to discover recent candidates; use dates inside the topic content to decide whether a work item belongs in the report. If Claude files are found but all are older than the requested window, report that clearly instead of claiming incompatibility.

Do not recursively scan an entire home directory or workspace. Do not expose credentials, tokens, private keys, or unrelated personal data found in memory.

## Build the report

Read `references/format-spec.md` before drafting.

1. Establish the report type, exact date range, and timezone. Display explicit dates in the output; do not rely only on relative labels such as `本周`.
2. Extract work items supported by memory in that range.
3. Merge duplicate mentions of the same task across sources.
4. Group items by stable project, product, or work domain. Avoid one-item micro-sections when two items naturally belong together.
5. Rewrite command logs and conversational fragments as outcome-oriented work statements.
6. Preserve technical names such as `TokenService`, `CoreDNS`, model names, APIs, and deployment modes when they help identify the work.
7. Preserve supported progress percentages, throughput, resource specifications, failure rates, and other decision-useful measurements. Never invent or extrapolate numbers.
8. Mark status accurately: completed, in progress, blocked, or pending verification. Never turn an attempted or failing task into a completed result.
9. Use the compact, paste-ready layout in `references/format-spec.md` by default. Match an existing document or user-provided sample when requested.
10. Generate the final report directly. Do not include the source inventory, hidden reasoning, or raw memory excerpts unless requested.

If evidence is insufficient, say which dates or sources are missing and produce only the supported portion. Never invent work to make the report look complete.

## Write to an existing report

Only edit a report file when the user asks. Preserve earlier daily, weekly, or monthly sections and the file's established heading/list style. Append a new report-type and date block when absent. If the same type and date block already exists, show or apply a scoped replacement for that block rather than duplicating it.

## Configure Codex automation

When the user requests scheduling:

1. Ask whether to create a new automation or update an existing one when the request does not make that clear.
2. Ask which report to generate: `日报`、`周报`、`月报`. Keep report type separate from automation recurrence; for example, a user may generate a weekly report every Monday.
3. Ask for the report coverage policy when it is not implied: `截至触发时的当前周期` or `上一完整周期`. State the resulting date semantics before creation.
4. Ask for the repeat cycle. Support at least `每天`, `工作日`, `每周`, and `每月`; accept a custom cycle only when the automation interface supports it.
5. Ask for the fields required by that cycle:
   - `每天`: execution time;
   - `工作日`: execution time;
   - `每周`: one or more weekdays and execution time;
   - `每月`: day of month and execution time.
6. Ask for timezone and report detail level. Also collect explicit memory paths and an output path when the user needs them. If timezone is omitted, use the active local timezone and state it before creation.
7. Summarize the human-readable configuration and obtain confirmation before creating a new recurring task. Do not expose a raw recurrence rule.
8. Inspect `$CODEX_HOME/automations/*/automation.toml` for a matching report type, name, or prompt. Prefer updating the matching automation over creating a duplicate.
9. Call the Codex `automation_update` tool; do not hand-edit `automation.toml`. Use the Codex `list_projects` tool to resolve the target project when a project ID is required.
10. Make the automation prompt self-contained. Include the `$reporter` invocation, report type, exact date-range policy, detail level, timezone, Codex and Claude Code memory roots or explicit paths, output destination when requested, and the instruction to avoid fabrication.
11. In an unattended run, do not ask follow-up questions. Use configured values, apply the documented fallbacks, and report missing evidence explicitly.
12. After the tool succeeds, confirm the task name, enabled state, report type, date-range policy, human-readable repeat cycle, execution time, timezone, memory scope, detail level, and output destination.

Creating this Skill does not itself create a recurring automation. Only create one after the user requests scheduling and supplies the required schedule.

## Validation

Read `references/script-template.md` before modifying or validating the collector. Run the structure and compilation checks plus a normal Codex-memory path, a Claude project-scoped path, a Markdown-fence path, and an error path.
