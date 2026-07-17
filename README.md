# Reporter

Reporter 是一个兼容 Codex 与 Claude Code 的 Agent Skill，可从近期记忆文件中提取有证据支持的工作事项，生成紧凑、可直接粘贴的中文日报、周报或月报，并可协助配置 Codex 周期自动化任务。

## 功能

- 扫描近期 Codex 与 Claude Code 记忆文件。
- 在生成前确认报告类型、时间范围和详细程度。
- 按项目或工作领域归类，保留完成状态、卡点、后续动作和有依据的量化结果。
- 输出适合群聊、邮件和工作文档的紧凑格式。
- 支持日报、周报、月报及 Codex 周期自动化配置。

## 输出示例

```markdown
本周工作：
2026/07/13—2026/07/17

**AgentSpace Sandbox**

1. 完成 SDK/CLI 核心能力回归验证，并补充通用使用指南。

**TokenService**

1. 完成运营助手相关 Skills 适配并打通交互流程，真实数据查询仍受部署侧鉴权限制。
```

## 安装

Codex：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
git clone https://github.com/oxygen914/reporter.git "${CODEX_HOME:-$HOME/.codex}/skills/reporter"
```

Claude Code 用户级安装：

```bash
mkdir -p "$HOME/.claude/skills"
git clone https://github.com/oxygen914/reporter.git "$HOME/.claude/skills/reporter"
```

Claude Code 项目级安装：

```bash
mkdir -p .claude/skills
git clone https://github.com/oxygen914/reporter.git .claude/skills/reporter
```

## 使用

Codex 中可使用 `$reporter`，Claude Code 中可使用 `/reporter`，也可以直接提出自然语言请求，例如：

- `生成今天的工作日报，标准详细程度。`
- `汇总最近七天的工作并生成周报。`
- `生成本月月报，保留关键指标和未解决卡点。`
- `每周五 18:00 自动生成标准版周报。`

## 目录结构

```text
reporter/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── format-spec.md
│   └── script-template.md
└── scripts/collect_report_context.py
```

## 校验

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" .
PYTHONPYCACHEPREFIX=/tmp/reporter-pycache python3 -m py_compile scripts/collect_report_context.py
```

## License

当前仓库尚未选择开源许可证。在许可证明确之前，请勿默认将公开可见等同于获得复制、修改或分发授权。
