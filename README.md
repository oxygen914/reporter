<div align="center">
  <img src="./assets/reporter-promo/poster.jpg" alt="Reporter：汇总 Codex 与 Claude Code 工作记忆，生成日报、周报和月报" width="100%" />

  # Reporter

  **把散落在 Codex 与 Claude Code 里的工作记录，整理成可直接提交的中文日报、周报和月报。**

  Codex · Claude Code · Daily Report · Weekly Report · Monthly Report · Automation
</div>

Reporter 是一个面向 **Codex 与 Claude Code** 的跨平台 Agent Skill。它会从近期记忆文件中提取有证据支持的工作事项，合并重复记录，保留真实进度、结果、卡点与关键指标，最终输出结构清晰、可直接粘贴到群聊、邮件或工作文档的报告。

> 不只是“总结聊天记录”：Reporter 会按时间范围筛选证据，并避免把尝试中、失败或待验证的工作写成已完成。

## 它能做什么

- **日报 / 周报 / 月报**：支持精简、标准、详细三种粒度。
- **双端记忆聚合**：兼容 Codex automation memory、Codex memories 与 Claude Code auto memory。
- **证据化整理**：合并同一任务的重复描述，保留状态、卡点、后续动作和有依据的量化结果。
- **规范化输出**：按项目或工作领域分组，生成紧凑、正式、可直接提交的中文报告。
- **Codex 自动化**：可引导创建每天、工作日、每周或每月执行的周期报告任务。
- **隐私优先**：不会把凭证、Token、私钥或无关个人信息带入报告。

## 工作流程

```text
Codex memories ─┐
                ├─→ 时间过滤 → 证据去重 → 项目归类 → 状态校准 → 日报 / 周报 / 月报
Claude memories ┘
```

Reporter 将文件修改时间仅用于发现候选内容，真正决定某项工作是否属于报告周期的是记忆内容中的日期与上下文。

## 快速开始

### Codex

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/oxygen914/reporter.git \
  "${CODEX_HOME:-$HOME/.codex}/skills/reporter"
```

调用：

```text
$reporter
```

### Claude Code

用户级安装：

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/oxygen914/reporter.git \
  "$HOME/.claude/skills/reporter"
```

项目级安装：

```bash
mkdir -p .claude/skills
git clone https://github.com/oxygen914/reporter.git .claude/skills/reporter
```

调用：

```text
/reporter
```

## 使用示例

立即生成报告：

```text
周报，详细
生成今天的标准日报
生成上个月的精简月报
汇总 2026-07-13 到 2026-07-17 的工作，保留关键指标和未解决卡点
```

创建 Codex 周期自动化：

```text
使用工作报告生成器创建自动化：每周五 18:00 生成本周详细周报，时区 Asia/Shanghai。
```

自动化配置会区分：

- 报告类型：日报 / 周报 / 月报
- 详细程度：精简 / 标准 / 详细
- 执行周期：每天 / 工作日 / 每周 / 每月
- 统计范围：截至触发时的当前周期 / 上一完整周期
- 时区、记忆路径与可选输出位置

Reporter 只在用户明确要求并确认配置后创建自动化任务；安装 Skill 本身不会自动创建任务。

## 输出示例

```markdown
本周工作：
2026/07/13—2026/07/17

**AgentSpace Sandbox**

1. 完成 Sandbox SDK/CLI 核心能力回归与发布准备，补充 CLI、Go SDK 通用使用指南，并完成版本构建与关键链路验证。

**TokenService**

1. 完成运营助手相关 Skills 适配并打通交互流程；真实数据查询仍受部署侧鉴权限制，后续待环境权限就绪后继续验证。
```

## 记忆文件兼容性

| 来源 | 支持范围 |
| --- | --- |
| Codex | `~/.codex/automations/*/memory.md`、`~/.codex/memories/` |
| Claude Code | `~/.claude/projects/<project>/memory/*.md`、`MEMORY.md`、`memory.md` |
| 项目上下文 | `CLAUDE.md`、`.claude/memory/*.md`、`.claude/memories/*.md` |
| 自定义来源 | 用户明确提供的文件或有限目录 |

`CLAUDE.md` 只作为背景上下文，不能单独证明某项工作已在报告周期内完成。

## 宣传动画

仓库提供一份无外部图片和字体依赖的 Skottie 兼容 Lottie 动画：

- [查看 Lottie JSON](./assets/reporter-promo/lottie.json)
- [查看可编辑颜色配置](./assets/reporter-promo/controls.json)
- [重新构建动画](./assets/reporter-promo/build.mjs)

动画表达“Codex 与 Claude Code 的工作记忆汇入 Reporter，最终生成日报、周报与月报”的完整流程。`build.mjs` 仅用于维护宣传素材，不参与 Skill 运行。

重新生成：

```bash
node assets/reporter-promo/build.mjs
```

## 项目结构

```text
reporter/
├── SKILL.md                         # Skill 入口与执行规则
├── agents/openai.yaml               # Codex UI 展示配置
├── references/
│   ├── format-spec.md               # 报告格式规范
│   └── script-template.md           # 记忆收集脚本说明
├── scripts/
│   └── collect_report_context.py    # Codex / Claude Code 记忆候选收集器
└── assets/reporter-promo/            # README 宣传动画与封面
```

## 校验

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
PYTHONPYCACHEPREFIX=/tmp/reporter-pycache \
  python3 -m py_compile scripts/collect_report_context.py
node -e "JSON.parse(require('fs').readFileSync('assets/reporter-promo/lottie.json', 'utf8'))"
```

## 贡献

修改执行逻辑时请更新 `SKILL.md`；修改报告样式时请更新 `references/format-spec.md`；修改记忆发现逻辑时请同步测试 `scripts/collect_report_context.py`。提交前请至少完成上述校验。

## License

当前仓库尚未选择开源许可证。在许可证明确之前，请勿将“公开可见”理解为已获得复制、修改或分发授权。
