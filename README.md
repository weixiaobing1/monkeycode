<div align="center">

# MonkeyCode

**面向本地开发工作流的终端 AI 编程助手**

在终端里读代码、改代码、运行测试，用权限规则控制工具操作，用 Git worktree 隔离子任务。

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white) ![MCP](https://img.shields.io/badge/MCP-stdio%20%7C%20HTTP-6B46C1?style=flat-square) ![Git worktree](https://img.shields.io/badge/Git-worktree-F05032?style=flat-square&logo=git&logoColor=white) ![OpenAI and Anthropic compatible](https://img.shields.io/badge/API-OpenAI%20%7C%20Anthropic-334155?style=flat-square)

[安装](#安装) · [快速开始](#快速开始) · [架构概览](#架构概览) · [相关开源项目](#相关开源项目)

</div>

## 项目简介

MonkeyCode 用 Python 实现了独立的 Agent Runtime，涵盖模型调用、上下文管理、工具调度、权限、会话和记忆。它可以在一次任务中多轮调用工具，并通过 Skills、MCP 和 Hooks 扩展工作流，无需 LangChain 或 LangGraph。

| 开发场景 | MonkeyCode 提供的能力 |
| --- | --- |
| 先调查，再动手 | 用 Plan 模式阅读和搜索代码，再进入 Execute 执行确认的计划 |
| 并行处理子任务 | 启动前台或后台子 Agent，并用 Git worktree 隔离各自的修改 |
| 接入项目工具 | 通过 MCP 注册外部工具，用 Skills 和 Hooks 加入项目约定 |
| 继续长任务 | 恢复历史会话、压缩上下文并保留长期记忆 |

## 核心能力

- **持续 Agent Loop**：支持单轮内多次 `model → tool → model` 循环。
- **持久终端界面**：提供状态区、对话区、输入区、补全和权限切换。
- **工作区工具**：读取、写入、编辑、查找、搜索和运行命令。
- **执行模式**：支持普通对话、`Plan` 和 `Execute`。
- **权限控制**：提供 `Default permissions`、`Auto-review` 和 `Full access`。
- **子 Agent**：支持角色定义、同步执行、后台任务和任务间消息。
- **Git worktree 隔离**：子 Agent 可在独立分支和目录中工作。
- **多 Provider**：支持 OpenAI 和 Anthropic 兼容协议。
- **Skills**：发现并加载项目级、用户级和内置 `SKILL.md`。
- **MCP**：通过 stdio 或 HTTP 接入外部工具。
- **Hooks**：在会话、消息、轮次和工具事件上执行自动化动作。
- **长会话管理**：支持会话恢复、上下文压缩、大型工具结果归档和长期记忆。

## 架构概览

```text
用户输入
   │
   ▼
终端界面 ── Slash Commands / Permission Toggle
   │
   ▼
AgentRunner
   ├── PromptBuilder / Project Instructions / Skills
   ├── ContextManager / MemoryStore / SessionArchive
   ├── OpenAI Provider / Anthropic Provider
   └── ToolScheduler
         ├── Workspace Tools
         ├── PermissionManager
         ├── MCP Tools
         ├── Hooks
         └── Agent / Background Tasks / Worktree
```

主要模块：

| 模块 | 职责 |
| --- | --- |
| `monkeycode/agent.py` | Agent Loop、模型调用和工具轮次 |
| `monkeycode/tui.py` | 终端渲染、输入和交互 |
| `monkeycode/context.py` | Token 估算、归档和上下文压缩 |
| `monkeycode/tool_scheduler.py` | 工具调度、并发、去重和取消 |
| `monkeycode/permissions.py` | 权限模式、规则和危险操作拦截 |
| `monkeycode/session_archive.py` | JSONL 会话归档与恢复 |
| `monkeycode/memory.py` | 项目级和用户级长期记忆 |
| `monkeycode/subagent/` | 子 Agent 定义和加载 |
| `monkeycode/worktree/` | Git worktree 创建、验证和清理 |
| `monkeycode/skills/` | Skill 发现、解析和执行 |
| `monkeycode/mcp/` | MCP 配置、传输和工具适配 |
| `monkeycode/hooks/` | Hook 配置、匹配和动作执行 |

## 环境要求

- Python 3.10 或更高版本。
- Windows、Linux 或 macOS 终端。
- OpenAI 或 Anthropic 兼容 API。
- 使用 worktree 隔离时，当前目录必须是 Git 仓库。

## 安装

克隆仓库后，在仓库根目录安装开发版本：

```powershell
python -m pip install -e ".[dev]"
```

只安装运行依赖：

```powershell
python -m pip install -e .
```

## 快速开始

在准备使用 MonkeyCode 的项目目录中创建 `monkeycode.yaml`：

```yaml
protocol: openai
model: gpt-4o-mini
base_url: https://api.openai.com/v1
api_key: ${MONKEYCODE_API_KEY}

options:
  temperature: 0.7

context:
  enabled: true
  context_window_tokens: 32000
  auto_safety_margin_tokens: 13000
  manual_safety_margin_tokens: 3000
```

在配置文件同目录创建不会提交到 Git 的 `.env`：

```dotenv
MONKEYCODE_API_KEY=your-real-api-key
```

启动：

```powershell
monkeycode
```

也可以显式指定配置：

```powershell
monkeycode --config path\to\config.yaml
```

未传入 `--config` 时，MonkeyCode 会依次寻找当前目录中的 `monkeycode.yaml` 和 `config.yaml`。系统环境变量优先于 `.env` 中的同名变量。

Anthropic 配置示例：

```yaml
protocol: anthropic
model: claude-sonnet-4-5
base_url: https://api.anthropic.com
api_key: ${MONKEYCODE_API_KEY}

options:
  max_tokens: 2048
```

## 基本使用

启动后直接输入任务：

```text
检查登录接口为什么返回 500，修复后运行相关测试
```

MonkeyCode 会读取代码、定位调用链、执行必要修改，并在结束时报告结果和验证情况。

### 常用命令

| 命令 | 用途 |
| --- | --- |
| `/help` | 显示可用命令 |
| `/plan` | 进入只读计划模式 |
| `/do` | 执行已经确认的计划 |
| `/compact` | 手动压缩上下文 |
| `/clear` | 清空当前会话并创建新 session |
| `/resume` | 恢复历史会话 |
| `/status` | 显示运行状态 |
| `/session` | 显示当前会话信息 |
| `/memory` | 显示已加载记忆 |
| `/permission` | 显示当前权限档位 |
| `/skill` | 列出已加载 Skill |
| `/exit`、`/quit` | 退出 MonkeyCode |

在 TUI 中按 `Shift+Tab` 可以循环切换权限档位。

## Agent 模式

### 普通对话

用于问答和轻量检查，只在确实需要时调用工具。

### Plan

使用 `/plan` 进入。该模式只允许读取和搜索，不修改文件或执行有副作用的命令。计划完成后可以使用 `/do` 继续执行。

### Execute

允许 Agent 使用当前权限范围内的工具完成任务，包括修改文件和运行命令。

## 内置工具

| 工具 | 用途 |
| --- | --- |
| `read_file` | 读取工作区内的文本文件 |
| `write_file` | 创建或覆盖文本文件 |
| `edit_file` | 按唯一原文匹配修改文件 |
| `find_files` | 使用 glob 查找路径 |
| `search_code` | 搜索文本、符号和匹配行 |
| `run_command` | 在工作区内执行带超时控制的命令 |
| `Agent` | 启动同步或后台子 Agent |
| `TaskList`、`TaskGet`、`TaskStop` | 管理后台任务 |
| `SendMessage` | 向后台任务发送消息 |
| `load_skill`、`install_skill` | 加载或安装 Skill |

文件工具和命令执行受工作区沙箱及权限系统约束。外部 MCP Server 暴露的工具也会注册到同一工具中心。

## 权限系统

启动时可以指定权限档位：

```powershell
monkeycode --permission-mode "Default permissions"
monkeycode --permission-mode "Auto-review"
monkeycode --permission-mode "Full access"
```

- `Default permissions`：读取默认放行，写入和命令通常需要确认。
- `Auto-review`：对潜在副作用保持人工审核。
- `Full access`：普通工具默认放行，但不会绕过危险命令黑名单、路径沙箱和显式 `deny` 规则。

权限规则按以下位置加载：

```text
~/.monkeycode/permissions.yaml
<workspace>/monkeycode.permissions.yaml
<workspace>/.monkeycode/permissions.local.yaml
```

示例：

```yaml
rules:
  run_command(git status): allow
  run_command(rm *): deny
  write_file(*.env): deny
```

需要人工确认时：

- `y`：仅本次允许。
- `s`：本会话允许相同目标。
- `n`：拒绝，并把结构化失败结果返回 Agent。

## 子 Agent 与 worktree

MonkeyCode 内置以下子 Agent：

- `general-purpose`
- `explore`
- `plan`
- `security-reviewer`

`Agent` 工具可以为独立任务选择角色、前台或后台运行方式，以及是否启用 worktree 隔离。

使用 `isolation: "worktree"` 时，MonkeyCode 从当前 `HEAD` 创建独立分支和目录：

```text
<workspace>/.monkeycode/worktrees/<task-name>
```

子 Agent 的文件和命令工具会绑定到该目录，不会直接修改主工作区。脏修改或包含未合并提交的 worktree 会被保留，避免结果丢失。

配置示例：

```yaml
enableSubAgentBackground: true

worktree:
  enabled: true
  root: ".monkeycode/worktrees"
  ttl_hours: 24
  copy_paths: [".env.local"]
  link_dirs: ["node_modules"]
  include_ignored: []
  hooks_path: ".githooks"
```

可以在 `<workspace>/.monkeycode/agents/` 中添加自定义子 Agent 定义。

## 扩展能力

### Skills

Skill 是包含 `SKILL.md` 的可复用工作流。加载优先级：

```text
<workspace>/.monkeycode/skills/
~/.monkeycode/skills/
MonkeyCode 内置 Skills
```

项目级同名 Skill 会覆盖用户级和内置版本。使用 `/skill` 查看目录，或使用 `/<skill-name>` 调用。

### MCP

MCP 配置按以下位置加载：

```text
~/.monkeycode/mcp.yaml
<workspace>/monkeycode.mcp.yaml
```

示例：

```yaml
mcp_servers:
  filesystem:
    transport: stdio
    command: npx
    args: ["-y", "@modelcontextprotocol/server-filesystem", "${PWD}"]

  docs:
    transport: http
    url: "https://example.com/mcp"
    headers:
      Authorization: "Bearer ${MCP_TOKEN}"
```

当前支持 stdio 和 HTTP transport。MCP 工具使用 `server__tool` 作为注册名，并经过 MonkeyCode 权限系统。

### Hooks

Hook 可以在会话、轮次、消息和工具事件发生时执行 `command`、`prompt`、`http` 或 `subagent` 动作。Hook 子 Agent 始终在后台运行，不阻塞原事件，并且不会继承父 Agent 的 Hooks。

配置位置：

```text
~/.monkeycode/hooks.yaml
<workspace>/monkeycode.hooks.yaml
<workspace>/.monkeycode/hooks.local.yaml
```

拦截危险命令示例：

```yaml
hooks:
  - id: block-dangerous-command
    event: tool.before
    if:
      all:
        - field: tool.name
          match: exact
          value: run_command
        - field: tool.arguments.command
          match: regex
          value: "(?i)remove-item|rm\\s+-rf"
    action:
      type: prompt
      target: tool_result
      content: "该命令命中项目安全策略，请改用更安全的操作。"
```

工具失败后启动子 Agent：

```yaml
hooks:
  - id: investigate-tool-error
    event: tool.error
    action:
      type: subagent
      prompt: "分析本次工具失败并给出修复建议"
      subagent_type: explore
      name: hook-error-investigator
      isolation: none
```

MonkeyCode 会把经过脱敏和长度限制的事件上下文附加到子 Agent prompt。启动结果会记录 `task_id`；启动失败只写入 Hook 结果和日志，不阻断主流程。

## 项目指令、会话与记忆

MonkeyCode 会把以下指令文件注入 system prompt：

```text
<workspace>/MONKEYCODE.md
<workspace>/.monkeycode/instructions.md
~/.monkeycode/instructions.md
```

指令文件支持 `@include path/to/file.md`。Include 会限制深度、防止循环，并禁止越过对应项目或用户目录。

会话默认保存于：

```text
<workspace>/.monkeycode/sessions/
```

恢复指定会话：

```powershell
monkeycode --resume-session <session-id>
```

长期记忆保存于：

```text
<workspace>/.monkeycode/memory/
~/.monkeycode/memory/
```

工具结果或对话历史接近上下文预算时，MonkeyCode 会归档大型结果并压缩较早历史，同时保留近期消息。

## 开发

运行完整测试：

```powershell
python -m pytest -q
```

检查命令行入口：

```powershell
python -m monkeycode --help
```

编译检查：

```powershell
python -m compileall -q monkeycode tests
```

## 当前边界

- Provider 协议目前支持 `openai` 和 `anthropic`。
- MCP 当前以工具接入为主，不支持 Resources、Prompts 和 Sampling。
- 没有内置浏览器、网络搜索、向量索引或代码语义索引。
- worktree 隔离依赖 Git，非 Git 项目无法使用。

## 相关开源项目

这些上游项目适合进一步了解终端 Agent、工具接入和长期记忆。

| 项目 | 方向 | 可以从这里了解 |
| --- | --- | --- |
| [OpenAI Codex](https://github.com/openai/codex) | 终端编码 Agent | 终端交互、命令执行和权限审批 |
| [MCP Reference Servers](https://github.com/modelcontextprotocol/servers) | 工具协议与参考实现 | MCP 服务端如何公开工具，以及参考服务如何组织 |
| [TencentDB Agent Memory](https://github.com/TencentCloud/TencentDB-Agent-Memory) | 团队级 Agent 记忆 | 对话、文档和代码如何沉淀为可共享的记忆资产 |

## License

当前仓库尚未提供 License 文件。公开发布或接受外部贡献前，应先确定许可证。
