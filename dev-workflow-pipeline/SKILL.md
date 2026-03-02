---
name: dev-workflow-pipeline
description: 在 AgenticX 开发中涉及研究、代码生成、提交、审查或知识沉淀时使用，或者不确定pipeline下一步该做什么时触发
---

# AgenticX 开发工作流pipeline

将 6 个命令编排为一条完整pipeline：**研究 → 实现 → 提交 → 审查 → 修复闭环 → 知识沉淀**。每一步的输出是下一步的输入。本 skill 负责判断你当前在Pipeline的哪个位置，并引导你进入下一步。

## pipeline流程

```
/codedeepresearch ──proposal.md──▶ /codegen ──代码+测试──▶ /commit
                                      ▲                       │
                              (被中断了?)                 commit body
                                      │                   (FR/NFR/AC)
                              /codegen-proceed                │
                                                              ▼
            /update-conclusion ◀──全部通过── /codeview --spec
               │                                   ▲     │
               ▼                                   │     ▼
         conclusions/*.md                     /commit ◀─ 修复
         (反哺下次研究)                       (--fix --commit)
```

## 命令间数据流

| 上游命令 | 下游命令 | 传递产物 | 获取方式 |
|---------|---------|---------|---------|
| `/codedeepresearch` | `/codegen` | proposal.md | `research/codedeepresearch/<name>/<name>_proposal.md` |
| `/codegen` | `/commit` | 代码 + 冒烟测试 | `agenticx/**` + `tests/test_smoke_<name>_*.py` |
| `/commit` | `/codeview` | commit body（含 FR/NFR/AC） | `git log -1 --format='%b'` |
| `/codeview --fix` | `/commit` | 修复后的代码 | 通过 `--fix --commit` 回到提交环节 |
| `/commit`（最终版） | `/update-conclusion` | 最新 git 提交的变更 | `git show --name-status -1` |
| `/update-conclusion` | 下一次 `/codedeepresearch` | 更新后的模块总结 | `conclusions/*_conclusion.md` |

## 状态检测：我在哪一步？

进入新会话或用户不确定下一步时，**按顺序**检查以下信号，匹配到第一个即建议对应操作：

### 信号 1：存在未提交的改动

```bash
git status --porcelain
```

有修改/新增文件 → **建议 `/commit`**，然后 `/codeview --spec`

### 信号 2：最近的提交尚未审查

```bash
git log -1 --format='%b' | head -5
```

commit body 包含 `## Requirements` 但本次会话未做审查 → **建议 `/codeview --working --spec="$(git log -1 --format='%b')"`**

### 信号 3：研究已完成但代码未开始

```bash
ls research/codedeepresearch/*/_proposal.md 2>/dev/null
```

有 proposal 但没有对应的冒烟测试（`tests/test_smoke_<name>_*.py`） → **建议 `/codegen <name>`**

### 信号 4：冒烟测试有失败

```bash
pytest -q --tb=line -k "smoke_" 2>&1 | tail -3
```

有红色测试 → **建议 `/codegen-proceed`** 恢复并修复

### 信号 5：模块总结已过时

对比 `git log -1 --format='%ci'` 与 `conclusions/` 文件时间戳，总结更旧 → **建议 `/update-conclusion`**

### 信号 6：用户提到了新的上游仓库

用户给出 GitHub URL 或提到要研究某个项目 → **建议 `/codedeepresearch <url>`**

## 常用场景速查

### 完整流程（顺利走完全程）

```bash
# 第一步：深度研究
/codedeepresearch https://github.com/owner/repo

# 第二步：实现（自动读取 proposal.md）
/codegen repo_name

# 第三步：结构化提交（commit body 含 FR/NFR/AC）
/commit @agenticx @tests

# 第四步：基于 commit 需求做审查
/codeview --working --spec="$(git log -1 --format='%b')"

# 第五步（如有问题）：修复 → 重新提交 → 重新审查（循环直到全部通过）

# 第六步：知识沉淀
/update-conclusion /path/to/AgenticX /path/to/AgenticX/conclusions
```

### 中断后恢复

```bash
/codegen-proceed
# 自动检测：哪些测试通过、哪些红了、下一个该做什么
# 先修红 → 再从断点继续推进
```

### 快速提交-审查循环（无需研究阶段）

```bash
# 手动写完代码后：
/commit @agenticx/core
/codeview --working --spec="$(git log -1 --format='%b')"
```

### 使用外部需求文档审查

```bash
/codeview --working --spec=research/codedeepresearch/openclaw/openclaw_proposal.md
```

## 命令速查表

| 命令 | 何时使用 | 输入 | 输出 |
|-----|---------|-----|-----|
| `/codedeepresearch <url>` | 研究上游仓库 | GitHub URL + 可选博客链接 | proposal.md、gap_analysis.md、source_notes.md |
| `/codegen <name> [scope]` | 实现功能 | proposal.md | `agenticx/` 下的代码 + 冒烟测试 |
| `/codegen-proceed` | 恢复被中断的 codegen | （自动检测） | 继续产出代码 + 测试 |
| `/commit [paths] [--spec]` | 结构化提交 | 暂存的改动 | 含 FR/NFR/AC 的 git commit |
| `/codeview <target> [--spec]` | 代码审查 | 分支/工作区/文件 + 可选需求规格 | 审查报告 |
| `/update-conclusion <代码路径> <总结路径>` | 同步知识 | 最新 git 提交 | 更新后的 `conclusions/*.md` |

执行任何命令时，请读取 [commands/](commands/) 下对应的详细指令文件。

## 反模式

| 不要这样做 | 原因 | 应该这样做 |
|-----------|-----|-----------|
| 跳过提交直接审查 | `/codeview --spec` 需要 commit body 作为输入 | 先 `/commit`，再审查 |
| 跳过审查直接沉淀 | 总结应基于经过验证的代码 | 审查通过后再 `/update-conclusion` |
| 没有 proposal 就跑 `/codegen` | 没有规格就没有实现依据 | 先 `/codedeepresearch` |
| 一个 commit 塞多个功能点 | 破坏精准的需求对齐审查 | 一个功能点一个 commit |
| 手写模块总结 | 久了必然与代码脱节 | 用 `/update-conclusion` 自动同步 |
| 修了审查问题但不重新提交 | 审计链路断裂 | 修完必须 `/commit`，再重新 `/codeview` |
