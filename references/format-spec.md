# Work report format specification

## Contents

- Default structure
- Section and item structure
- Writing patterns
- Complex items
- Content rules
- Detail calibration
- Quality check

## Default structure

```markdown
本周工作：
2026/07/13—2026/07/17

**AgentSpace Sandbox**

1. 完善 Sandbox 接入指南，结合 CLI、Go SDK 与 HTTP API 完成核心接口回归验证，并修正文档中的请求参数、响应结构和权限格式。
2. 完成 CLI 的 Go 1.22 兼容适配与验证，调整依赖声明和构建方式，改为引用 SDK 的远端版本。

**TokenService**

1. 完成 AI 运营助手 `ts-manager` 和 `ts-onboard` Skills 适配，打通交互流程并优化产品介绍、用户接入和 SLA 说明。
2. 适配远程 KV Cache，已在目标集群完成 1P1D 联调和压测；3P1D、5P1D 场景仍存在异常退出，相关框架与推理日志已提交排查。
```

Use a plain report label, an explicit slash-formatted date line, a bold project/domain name, and an ordered list. Keep one blank line between the date, domain blocks, and lists. Do not use `#`、`##`、`###` headings in the default paste-ready format. Use Markdown headings only when the target document already uses them or the user asks for a formal document layout.

Select the label and date line by report type:

| Report type | Current-period label | Date example |
| --- | --- | --- |
| 日报 | `今日工作：` | `2026/07/17` |
| 周报 | `本周工作：` | `2026/07/13—2026/07/17` |
| 月报 | `本月工作：` | `2026/07` |

For a previous or custom period, avoid a misleading relative label: use `工作日报：`、`工作周报：` or `工作月报：` and show the exact date or range. For a partial current month, use an explicit range such as `2026/07/01—2026/07/17`. Keep the same bold domain and ordered-list structure for all report types.

## Section and item structure

- Use `**领域或项目名**` for each domain, for example `**Sandbox**`、`**TokenService**`、`**Trace**`.
- Preserve the user's established capitalization and product spelling. Do not rewrite `TokenService` as a generic Chinese label when the technical name is useful.
- Use numbered entries by default, including sections with one item. Keep numbering independent inside each domain.
- Put one independently reportable objective or outcome in each numbered entry.
- Prefer 2–6 entries per domain. Keep a one-entry domain when it is materially distinct; do not merge unrelated work just to avoid a short section.
- Order domains by work importance or the user's existing order. Within a domain, place completed outcomes first, then in-progress work, blockers, and follow-ups.

## Writing patterns

Write a normal item in this order when the evidence supports it:

`动作或目标 + 已取得的结果 + 当前状态/卡点 + 后续动作`

Do not mechanically include all four parts. Omit empty background and obvious next steps. Examples:

- Completed: `完成 Sandbox SDK/CLI 与 server、gateway 能力对齐及 pre 环境回归，完成 v0.1.0 构建打标，并输出 CLI 和 Go SDK 通用使用指南。`
- In progress: `Trace 服务限流改造压测中，已对数据处理和上报链路增加限流保护，降低大流量场景打挂服务的风险。`
- Blocked: `完成视频生成协议调研、适配方案和网关 Mock 验证；当前受测试模型尚未提供限制，真实 API 联调暂未开展。`
- Quantified: `Trace 服务 10 台 8C16Gi 实例可支持 600 QPS，3 台独立 ES 集群可支持 2000+ QPS。`

Keep facts at their supported precision. Preserve meaningful values such as `60%`、`600 QPS`、`8C16Gi`、`复现 1/18 次`, but do not convert observations into stronger capacity guarantees or business conclusions.

## Complex items

Keep a standard item to one or two readable sentences when possible. For a long incident, migration, or multi-stage investigation, use one numbered summary plus indented short bullets instead of one dense paragraph:

```markdown
4. 跟进 P 节点故障恢复后 D 节点异常重启问题，当前评估为低概率边界场景，业务影响可控。
   - 复现：单并发重启 90 次复现 1 次，128 并发重启 18 次复现 1 次。
   - 影响：仅在硬件故障导致 P 节点重启后偶发，触发后具备自动恢复能力。
   - 后续：由相关团队持续提单跟踪，并在新版本上验证复现情况。
```

Use only the sublabels supported by evidence, normally `进展`、`复现`、`结果`、`影响`、`卡点`、`后续`. Do not create nested bullets for routine items.

## Content rules

- State action and outcome first; add status, blocker, or next step only when useful.
- Use concise formal Chinese. Remove chatty wording, command transcripts, exhaustive test lists, and repeated background.
- Keep evidence boundaries explicit with phrases such as `已完成`, `进行中`, `待验证`, or `受……限制`.
- Combine closely related changes into one entry when separating them would create implementation-level noise.
- Split an entry when it contains unrelated products, goals, or outcomes.
- Keep failed or environment-dependent validation distinct from completed implementation.
- Avoid bare fragments such as `稳定性加固` when memory contains a concrete action or result. Keep a short fragment only when no stronger evidence exists.
- Avoid repeating the domain name at the start of every entry unless needed for clarity.
- Do not add generic sections such as `总结`、`下周计划` or `风险` unless the user requests them or the source format contains them.
- Do not include secrets, access tokens, internal credentials, or unnecessary machine-local paths.

## Detail calibration

| Level | Target length | Typical content |
| --- | --- | --- |
| 精简 | 20–45 Chinese characters | action + result |
| 标准 | 40–90 Chinese characters | action + result + status |
| 详细 | 80–150 Chinese characters | action + key implementation/result + blocker or next step |

Length is a guide, not a hard truncation rule. Prefer semantic completeness over mechanically hitting a character count.

## Quality check

Before returning the report, verify:

1. The report label matches the selected type and the next line shows the exact slash-formatted date or range.
2. Every item belongs to the requested date range or is clearly labeled as continuing work.
3. Every completion claim is supported by memory.
4. Duplicate work across memories has been merged.
5. Project and technical names are consistent.
6. Each item is readable in one pass and matches the chosen detail level.
7. Long incidents are split into useful subpoints instead of a dense paragraph.
8. Supported progress and performance measurements are retained without exaggeration.
9. The report contains no raw memory metadata, credentials, or hidden analysis.
