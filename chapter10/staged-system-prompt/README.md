# 实验 10-1：根据执行阶段决定系统提示词（Staged System Prompt）

《深入理解 AI Agent》配套实验代码。

## 实验目的

同一个 Coding Agent，在任务的不同**执行阶段**加载**不同的系统提示词 + 不同的工具集**，
从而在同一段对话里扮演不同角色、表现出不同的行为模式；同时让**对话历史与任务状态在阶段间连续共享**。

本实验用一个「Coding Agent」串起三个阶段：

| 阶段 | 角色 | 系统提示词强调 | 配套工具集 | 触发进入下一阶段的工具 |
| --- | --- | --- | --- | --- |
| 1 需求澄清 | 需求分析师 | 只提问确认、**不写代码** | `ask_clarifying_question` / `save_requirement` / `complete_requirements_analysis` | `complete_requirements_analysis` → 阶段2 |
| 2 代码实现 | 软件工程师 | 按已确认需求写高质量 Python | `write_file` / `read_file` / `execute_code` / `submit_for_review` | `submit_for_review` → 阶段3 |
| 3 代码审查 | 代码审查员 | 批判性把关质量 | `run_linter` / `run_tests` / `analyze_complexity` / `request_revision` / `approve_code` | `request_revision` → **回退阶段2**；`approve_code` → 完成 |

## 架构

```
demo.py                入口：一条命令跑通三阶段（任务 = “写一个整理下载文件夹的 Python 脚本”）
agent.py               StagedAgent：阶段状态机 + 工具调用循环 + 跨阶段共享上下文 + 执行日志
tools.py               三套工具的 Schema 与真实实现（虚拟工作区 / 真实执行代码 / linter / 复杂度分析）
simulated_user.py      模拟用户：需求澄清阶段自动回答 Agent 的提问（预设答案），实现无人值守
config.py              从环境变量读取 API Key / base_url / model
```

关键设计：

- **共享上下文**：`StagedAgent.history` 是一条贯穿始终的消息列表，切换阶段时**只替换 system 提示词、只切换传给模型的 tools**，历史消息（需求、代码、审查意见）全部保留。每次请求都是 `[system(当前阶段)] + history`。
- **阶段转换由工具调用触发**：主循环识别到 `complete_requirements_analysis` / `submit_for_review` / `request_revision` / `approve_code` 这些「信号工具」被调用时，注入一条跨阶段「交接」消息并切换阶段。
- **回退机制**：审查阶段发现问题时调用 `request_revision(issues)`，把问题清单退回实现阶段；设有 `max_revisions` 安全阀，避免无限循环烧 token。
- **真实执行**：`execute_code` / `run_tests` 会把代码写入临时目录并用子进程真实运行；`run_linter` / `analyze_complexity` 基于 `ast` 做真实静态分析，不是假返回。

## 如何运行

```bash
pip install -r requirements.txt

# 配置（二选一）
export OPENAI_API_KEY=sk-...           # 方式 A：直接 export
cp env.example .env && vi .env         # 方式 B：写到 .env

python demo.py
```

可配环境变量（见 `env.example`）：`OPENAI_API_KEY`（必填）、`OPENAI_BASE_URL`（默认官方）、
`OPENAI_MODEL`（默认 `gpt-4o-mini`，便宜省钱）、`OPENAI_TEMPERATURE`（默认 0.3）。
也可切到兼容 OpenAI 协议的 Kimi / Doubao。

## 演示说明了什么问题

一次真实运行（`gpt-4o-mini`）会看到：

1. **需求澄清阶段**：Agent 表现为「不断提问」——主动追问处理哪些文件类型、是否递归、是否保留原名、移动还是复制、目标目录怎么定，并逐条 `save_requirement`。它**完全不写代码**。
2. **代码实现阶段**：同一个 Agent 换了提示词后表现为「写代码」——`write_file` 产出 Python 脚本，`execute_code` 自测，然后 `submit_for_review`。
3. **代码审查阶段**：Agent 表现为「批判审查」——依次跑 `run_linter` / `run_tests` / `analyze_complexity`，发现真实问题（如缺少模块 docstring、冒烟测试 `FileNotFoundError`）后 `request_revision` **退回实现阶段**。
4. 实现阶段据问题清单**重写并修复**，再次提交；审查通过后 `approve_code`，任务完成。

也就是说：**提示词 + 工具集随阶段切换，行为模式随之明显不同**，而任务状态（需求、代码、审查意见）在阶段间始终连续共享。运行结束时会打印每个角色的「行为分布」统计，直观对比三个阶段的行为差异。
