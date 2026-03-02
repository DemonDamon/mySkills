# commit

帮我提交代码到 Git 仓库，**按功能点分组生成 commit**，每个 commit 附带结构化的微型需求描述（可作为 `/codeview --spec` 的输入源）。

## 参数

- **指定路径**: `$ARGUMENTS`（相对于仓库根目录的路径）
- 示例: `@agenticx/sandbox @tests/unit` 仅关注这两个路径的变化
- 如果未提供，扫描整个工作区

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `--lite` | 轻量模式：只生成标题行，跳过 Requirements 块 | 不启用，默认生成完整 commit body |
| `--spec=<path>` | 从指定需求文档提取需求，并将该文档自动纳入提交范围（仓库内路径） | 不提供，从代码改动自行推断 |

## 核心工作流程

### 1. 识别变更文件

**必须使用 `--` 路径参数过滤**，而不是用 grep 关键字搜索：

```bash
# ✅ 正确：使用 -- 路径参数
cd <仓库根目录>
git status --porcelain -- <路径1> <路径2>
git diff --name-only -- <路径1> <路径2>

# ❌ 错误：使用 grep 关键字搜索（会匹配到不相关的文件）
git status | grep "sandbox"  # 不要这样做
```

**`--spec` 路径自动并入（关键规则）**：

- 若提供 `--spec`，先解析 spec 路径（支持单个、逗号分隔，或 `@path1@path2` 风格）
- 将 spec 路径与用户指定路径取并集，作为最终过滤路径
- 仅纳入**仓库内**且存在的 spec 文件；仓库外路径仅用于阅读，不参与提交

```bash
# 最终过滤路径 = 用户路径 ∪ spec路径(仓库内)
git status --porcelain -- <用户路径...> <spec路径...>
git diff --name-only -- <用户路径...> <spec路径...>
```

**示例**：
```bash
# 用户输入: /commit @agenticx/sandbox --spec=.cursor/plans/feature.plan.md
cd /Users/damon/myWork/AgenticX
git status --porcelain -- agenticx/sandbox/ .cursor/plans/feature.plan.md
git diff --name-only -- agenticx/sandbox/ .cursor/plans/feature.plan.md
```

识别的变更类型：
- 已修改 (M)
- 新增 (A / ??)
- 删除 (D)
- 重命名 (R)

### 2. 分组变更文件

将变更文件按**功能点**分组（不再是单文件粒度，而是"实现 + 对应测试"一起提交）：
- 同一功能点的实现文件 + 对应测试文件 = 一个 commit
- 纯基础设施改动（CI / config）单独一个 commit
- 纯文档改动单独一个 commit

分组判定依据：
- 文件路径的模块归属（`agenticx/core/` vs `agenticx/llms/`）
- 实现与测试的对应关系（`overflow_recovery.py` ↔ `test_smoke_openclaw_overflow_recovery.py`）
- 如果用户提供了 `--spec`，按 spec 中的功能点编号分组

### 2.5 确认提交人身份（每次执行必须做）

在生成任何 commit 之前，先读取当前 git 用户配置：

```bash
git config user.name
git config user.email
```

将结果作为所有 commit 的署名信息。**不需要额外传 `--author`**，git 会自动使用 `user.name` 和 `user.email`。

在提交计划中展示：

```
👤 提交人：<user.name> <<user.email>>
```

如果 `user.name` 或 `user.email` 为空，必须主动提示用户：
> git 未配置 user.name / user.email，请先运行：
> ```bash
> git config --global user.name "你的名字"
> git config --global user.email "your@email.com"
> ```

### 3. 逐组处理

#### 3.1 查看具体改动

```bash
# 已跟踪文件的改动
git diff -- <具体文件>

# 新增文件（untracked）直接查看内容
cat <新文件> | head -50
```

#### 3.2 推断需求条目

从代码改动中提取这组变更的意图，整理为结构化需求：

**信息来源**（按优先级）：
1. 如果提供了 `--spec`：从需求文档中匹配当前功能点对应的条目
2. 如果当前对话中有 `/codegen` 产出的功能点表格：从中提取
3. 以上都没有：从代码 diff 本身推断（函数名、docstring、类名、测试断言）

**提取规则**：
- **FR（功能性需求）**：这组代码要实现什么行为？从公共 API、函数签名、类 docstring 提取
- **NFR（非功能性需求）**：有没有性能/安全/并发/容错方面的设计？从异常处理、超时设置、锁机制、重试逻辑提取
- **AC（验收条件）**：测试文件中的 test case 名称和断言即验收条件

每类条目不必强求都有——代码改动本身能体现多少就写多少：
- 一个简单的 bug fix 可能只有 1 条 FR + 1 条 AC
- 一个新功能通常有 2-5 条 FR + 1-2 条 NFR + 2-4 条 AC

#### 3.3 生成 Commit 信息

**完整格式**（默认）：

```
<type>(<scope>): <description>

## What & Why
<1-3 句话说明这次改动做了什么、为什么做>
<如有上游来源，标注来源项目和机制名>

## Requirements
- FR-1: <功能性需求描述>
- FR-2: <功能性需求描述>
- NFR-1: <非功能性需求描述>（如有）
- AC-1: <验收条件>
- AC-2: <验收条件>
```

**轻量格式**（`--lite` 模式）：

```
<type>(<scope>): <description>
```

**字段规范**：
- **type**: `feat/fix/docs/style/refactor/perf/test/chore/build/ci`
- **scope**: 模块名（如: `overflow_recovery`, `auth_profile`, `sandbox`）
- **description**: 简洁明了，体现主要改动
- **语言**: 标题行必须为**英文**；Requirements 块中英文皆可（FR/NFR/AC 前缀保持英文，描述可用中文）
- **FR/NFR/AC 编号**: 在单个 commit 内从 1 开始编号，无需全局唯一

**严格禁止在 commit message 中出现**：
- `Made-with: Cursor`、`Co-authored-by: Cursor`、`Generated-by:` 等任何 AI 工具 trailer
- 任何非本人身份的署名（git 的 `user.name` / `user.email` 即为唯一署名来源）
- `--author` 参数（除非用户明确要求覆盖）

### 4. 生成提交计划

列出所有要提交的内容：

```
📝 提交计划（共 N 个 commit）：

【Commit 1】功能点：<功能点名称>
文件:
  - <impl_file1>
  - <test_file1>
消息:
  <type>(<scope>): <description>

  ## What & Why
  <简述>

  ## Requirements
  - FR-1: ...
  - AC-1: ...

---

【Commit 2】功能点：<功能点名称>
文件:
  - <impl_file2>
  - <test_file2>
消息:
  <type>(<scope>): <description>

  ## What & Why
  <简述>

  ## Requirements
  - FR-1: ...
  - NFR-1: ...
  - AC-1: ...
```

### 5. 确认后执行

**询问用户确认**，然后逐个执行：

```bash
cd <仓库根目录>
git add <具体文件1> <具体文件2>
# 不要加 --author 或任何 trailer，署名由 git config user.name/user.email 决定
git commit -m "$(cat <<'EOF'
<type>(<scope>): <description>

## What & Why
<简述>

## Requirements
- FR-1: ...
- AC-1: ...
EOF
)"
```

---

## 与 `/codeview` 的联动

commit 中的 Requirements 块是 `/codeview --spec` 的天然输入源。用法：

```bash
# 审查最近一次 commit 的代码，用 commit message 本身作为需求规格
/codeview --working --spec="$(git log -1 --format='%b')"

# 审查某个 commit 的改动
/codeview <commit_sha> --spec="$(git log <commit_sha> -1 --format='%b')"
```

需求追溯链路：
```
proposal.md（整体方案）
  └── commit body（功能点级需求）← 你在这里
        └── /codeview --spec（审查对齐）
```

---

## 使用示例

```bash
# 提交特定目录的变更（完整模式，含 Requirements）
/commit @agenticx/sandbox

# 提交多个目录的变更
/commit @agenticx/sandbox @tests/sandbox

# 轻量模式（只要标题行）
/commit --lite

# 从 proposal 文档提取需求写入 commit
/commit --spec=research/codedeepresearch/openclaw/openclaw_proposal.md

# 同时提交代码与多个 plan/spec 文件（推荐）
/commit @agenticx @tests --spec=.cursor/plans/openclaw_phase3_codegen_9ffd663d.plan.md,.cursor/plans/phase_3_plan_update_07406215.plan.md

# 兼容历史写法（@path1@path2）
/commit @agenticx @tests --spec=@.cursor/plans/a.plan.md@.cursor/plans/b.plan.md

# 提交整个工作区的变更（不带参数）
/commit
```

---

## 注意事项

1. **路径是相对于仓库根目录**：`@sandbox` 对应 `agenticx/sandbox/` 或项目中实际存在的路径
2. **始终在仓库根目录执行 Git 命令**：不要 cd 到子目录
3. **使用 `--` 分隔路径参数**：`git diff -- path/to/dir/`
4. **新增文件（??）需要先 add 才能 diff**：或直接查看文件内容
5. **Requirements 块不是 PRD**：写的是这次 commit 级别的意图和验收条件，不是完整需求文档。粒度太粗（"实现身份认证"）或太细（"第 42 行加了 if 判断"）都不对
6. **FR/NFR/AC 不强求都有**：简单改动可能只有 FR + AC；纯重构可能只有 FR（行为等价）+ AC（测试仍通过）
7. **commit body 使用 HEREDOC**：多行 commit message 必须用 HEREDOC 语法，避免引号嵌套问题
8. **署名只用 git config**：提交前先读取 `git config user.name` 和 `git config user.email`，commit 命令不加 `--author` 或任何 trailer；绝对不能附加 `Made-with: Cursor`、`Co-authored-by: Cursor` 等 AI 工具标记
9. **`--spec` 文件默认要随代码一起提交（若在仓库内）**：防止“引用了 spec 但漏提交 plan 文档”

---

**指定路径**: $ARGUMENTS