# codedeepresearch

把一个开源仓库（必选）及可选的网页资料（推文/博客/公众号等）进行“深度研究 + 可落地内化”，并输出可复用的技术方案与落盘资料，帮助把优秀思想/代码能力逐步沉淀进 AgenticX（以 SDK 为主，优化方向：智能体自动挖掘）。

## 参数（输入格式）
在聊天中使用：
- `/codedeepresearch <github_repo_url> [extra_urls...]`

约束：
- `github_repo_url` **必选**，形如 `https://github.com/<owner>/<repo>`
- `extra_urls...` **可选**，可填 0 个或多个网页 URL（空格分隔）

## MCP 工具策略（重要）

本命令协同使用两类 MCP 工具，各有侧重：

| 工具 | 适用场景 | 典型输出 |
|------|---------|---------|
| **DeepWiki MCP** | 理解架构、学习概念、问原理 | 概念解释、架构图、代码示例（文档级） |
| **ZRead MCP** | 读代码、查结构、找 Issue/PR | 完整代码文件、目录树、Issue 记录 |

### 协同使用原则
```
1. 理解架构阶段  →  优先 DeepWiki MCP（问答能力强）
2. 定位代码阶段  →  优先 ZRead MCP（结构清晰）
3. 阅读源码阶段  →  优先 ZRead MCP（可读完整文件）
4. 理解实现细节  →  DeepWiki MCP 辅助（获取设计背景）
5. 排查问题阶段  →  ZRead MCP（检索 Issue/PR）
```

### 可用性检查与降级方案
在使用前必须检查工具可用性：

1. **DeepWiki 不可用时**（仓库未被索引）：
   - 降级为本地 clone + 静态阅读
   - 结合网页搜索补充设计文档

2. **ZRead 不可用时**（未订阅或额度用尽）：
   - 降级为本地 clone 后用 IDE 工具阅读
   - 使用 GitHub Web API / 直接浏览仓库

3. **两者都不可用时**：
   - 必须 clone 到本地，纯静态分析
   - 在产物中标注"未使用 MCP 辅助，结论完整性受限"

## 目标产物（必须落盘）
把所有产物写入工作区（AgenticX 仓库）下的一个固定目录，便于版本管理与长期积累：
- 根目录：`research/codedeepresearch/<repo_name>/`

文件命名规范（必须遵守）：
- DeepWiki 原始问答落盘：`<repo_name>_deepwiki.md`（架构理解、概念问答）
- ZRead 代码检索落盘：`<repo_name>_zread.md`（目录结构、关键代码、Issue/PR）
- 网页爬取原文落盘：`sources/` 目录下按域名/标题或时间戳命名的 `*.md`
- 源码阅读与结构抽取：`<repo_name>_source_notes.md`
- AgenticX 对比分析报告：`<repo_name>_agenticx_gap_analysis.md`
- 最终技术方案（可落地改造方案）：`<repo_name>_proposal.md`
- 可选：评测/任务集草案：`<repo_name>_eval_plan.md`

> 注意：若工作区不是 AgenticX 仓库，请先询问我是否切换到 AgenticX 工作区后再继续。

## 工作流程（SOP，严格按顺序执行）

### 0) 澄清与环境确认（必须）
在开始前先用 3~6 个简短问题确认关键信息（若我已在对话中给出则跳过）：
- 我希望内化到 AgenticX 的优先方向是哪些？（可列出优先模块：planner/tool/memory/runtime/obs 等）
- 期望输出的“落地粒度”：PoC / MVP / 可合并到主分支的完整实现
- 技术约束：是否允许新增依赖、是否可引入外部服务、兼容的 Python 版本范围
- 我关心的指标优先级：成功率/成本/token/延迟/可解释/可控/可维护

然后检查当前工作区状态：
- 确认这是 AgenticX 仓库根目录（存在 `agenticx/` 等关键目录）
- **核心前置：读取并内化当前 AgenticX 的最新模块结论与能力现状**。
  - 读取 `conclusions/` 目录下的所有相关 `*.md`（特别是 `core_module_conclusion.md` 和 `tools_module_summary.md`）。
  - **强制性同步**：在输出 Gap 分析和技术方案前，必须明确指出目标框架与 AgenticX 现有高级能力（如：12-Factor Agents, Unified Tool V2, Compiled Context, Hooks/Flow 系统）的差异，禁止提出已经被 AgenticX 解决或超越的技术方案。
- 读取当前 AgenticX 相关模块代码（只读，不要大范围改动）：tool 系统、runtime、memory、planner（如果存在）

**MCP 工具可用性检查**（必须）：
- 使用 DeepWiki MCP 的 `read_wiki_structure` 工具测试目标仓库是否被索引
  - 若返回 `fetch failed` 或无结果：标记 `deepwiki_available = false`
- 使用 ZRead MCP 测试目标仓库是否可访问
  - 若返回授权失败或额度不足：标记 `zread_available = false`
- 将检查结果记录到 `meta.md`，并据此调整后续步骤的工具选择策略

### 1) 拉取目标仓库源码（必须）
将目标 GitHub 仓库克隆到本地工作区的研究目录下（不要污染 AgenticX 代码结构）：
- 目标路径：`research/codedeepresearch/<repo_name>/upstream/`
- 要求：尽量浅克隆（如可行）并记录 commit SHA / tag

并生成一份简短元信息记录到 `research/codedeepresearch/<repo_name>/meta.md`：
- repo URL、默认分支、当前 commit SHA、license、主要语言、是否 monorepo

### 2) 源码快速跑通与关键路径定位（必须）
目标不是“读完”，而是拿到 **可验证的 source-of-truth**：

**步骤 2.1：获取仓库结构**
- 若 `zread_available = true`：使用 ZRead MCP 获取仓库目录结构，快速定位核心模块
- 若不可用：从本地 clone 的 `upstream/` 目录使用 IDE 工具遍历

**步骤 2.2：运行最小示例**
- 寻找并运行最小示例（README / examples / quickstart）
- 如果无法运行：至少把入口调用链和核心模块边界梳理清楚（用静态阅读 + 搜索）

输出到 `<repo_name>_source_notes.md`，必须包含：
- “它解决了什么问题（边界/非目标）”
- 关键抽象（3~7 个名词）及对应源码位置（文件/类/函数）
- 关键调用链（入口 → 核心执行点）
- 失败模式与错误处理策略（超时、重试、幂等、降级）
- 扩展点（插件/registry/hook/interface）

### 2.5) ZRead 代码级检索并落盘（若 ZRead 可用）
若 `zread_available = true`，使用 ZRead MCP 进行深度代码检索，落盘到 `<repo_name>_zread.md`：

**必做检索项**：
- 仓库目录结构（定位核心模块边界）
- 关键入口文件的完整代码（如 `__init__.py`、`main.py`、`index.ts`）
- 核心抽象类/接口的完整定义

**按需检索项**：
- 相关 Issue/PR 历史（了解设计演进、已知问题）
- 特定功能的实现文件（根据步骤 2 定位的关键路径）

**落盘格式**：
```markdown
## 目录结构
[ZRead 返回的目录树]

## 关键代码文件
### 文件：path/to/file.py
[完整代码内容]

## 相关 Issue/PR
- #123: [标题] - [摘要]
```

> **重要**：ZRead 返回的是完整源码，可作为后续源码校验的 ground truth；DeepWiki 返回的代码示例来自文档而非源码，需交叉验证。

### 3) DeepWiki 深问并落盘（架构理解为主）
使用 DeepWiki MCP 工具对目标仓库进行“深度提问”，**侧重于架构理解和概念解释**，并把回答完整保存到 `<repo_name>_deepwiki.md`。

> **工具定位说明**：DeepWiki 擅长回答“为什么这样设计”、“架构原理是什么”等概念性问题，其代码示例来自文档而非源码。如需验证具体代码实现，应使用 ZRead MCP 或本地源码。

提问策略（必须覆盖以下主题；每个主题至少 1~3 问，必要时追问）：
- 架构与数据流：核心组件、执行链、状态如何流转
- 扩展机制：插件点、如何新增能力、有哪些稳定接口
- 可靠性：错误/重试/超时/并发/幂等/可观测性
- 性能/成本：缓存、批处理、token 成本控制（若为 LLM 框架）
- 设计权衡：为什么这样设计、替代方案是什么、已知限制
- 与 AgenticX 映射：哪些点可直接迁移，哪些不适配

落盘要求：
- 每个问题编号（Q1/Q2…），答案编号（A1/A2…）
- 对关键结论必须加“我自己的源码校验备注”：写出可定位到的源码证据（文件/符号/路径）；若无法在源码中验证，标注“未证实”
- **新增**：对于 DeepWiki 返回的代码示例，标注“来源：文档”；对于 ZRead 返回的代码，标注“来源：源码”

### 4) 可选网页资料爬取与落盘（若提供 extra_urls）
如果我提供了额外网页 URL：
- 逐个爬取并保存为 Markdown 到 `research/codedeepresearch/<repo_name>/sources/`
- 对于 JS 渲染/反爬页面：优先使用浏览器工具提取正文后再保存
- 每篇资料生成一个“可信度小结”（放在文件顶部）：
  - 作者/机构（如可获得）
  - 是否有源码引用/数据/图表
  - 与源码是否一致（如果能校验）

### 5) 交叉校验：博客/DeepWiki vs 源码（必须）
输出到 `<repo_name>_source_notes.md` 或单独追加一个章节，形成“校验表”：
- 结论 → 证据（源码位置/commit/issue）→ 是否属实（是/否/部分）→ 修正表述

门槛：
- 若关键机制无法被源码证实，必须降低其权重，并在最终方案中显式标注风险。

### 6) 与 AgenticX 的差距分析（必须）
结合 AgenticX 当前代码（以 SDK 形态、面向“智能体自动挖掘”优化）输出 `<repo_name>_agenticx_gap_analysis.md`，必须包含：
- AgenticX 现状（与本议题相关的模块/能力清单）
- 对方框架的优势点清单（按“机制/抽象/工程化/评测/生态”分类）
- AgenticX 更优点清单（如果存在，给出理由与证据）
- 差距列表（Gap）与优先级（P0/P1/P2）
- 风险与约束（依赖、复杂度、侵入性、维护成本）

判定规则（必须遵守）：
- 若 AgenticX 已具备同等能力且更简洁/可维护/可控：输出“无需引入，仅建议对齐文档/测试/接口”的解释报告
- 若对方在某方面明显领先：必须提出“可在 AgenticX 内化的最小机制”，而不是照搬整套框架

### 7) 最终技术方案报告（必须）
输出 `<repo_name>_proposal.md`，结构固定如下（必须按此结构写）：
1. 背景与问题定义（含边界/非目标）
2. 上游框架的关键思想（可验证结论 + 源码证据）
3. 可迁移的最小机制（Principles + Invariants）
4. AgenticX 方案设计
   - API/接口草案（SDK 视角）
   - 模块划分与数据流
   - 关键算法/策略（例如自动挖掘：候选生成/打分/探索-利用/停止条件）
   - 错误处理与可观测性（trace/log/metrics）
5. 集成计划（分阶段：PoC → MVP → 稳定化）
6. 评测计划（任务集、指标、回归门禁）
7. 风险与回滚策略
8. 后续工作（社区跟进点：issue/PR/roadmap）

### 8) 给出“下一步规划调整”（必须）
在最后，用简短清单输出“我建议你接下来怎么做”，要求：
- 明确下一步要改哪些 AgenticX 模块（文件/目录级别即可）
- 哪些先做（1~2 周内可落地），哪些后做
- 如果需要新增抽象/接口，先写 ADR（架构决策记录）再实现

## 执行约束（很重要）
- 全程以“源码可验证”为第一准则：任何关键结论都要能追溯到源码/issue/PR
- 产物必须落盘到 `research/codedeepresearch/<repo_name>/`，不要只停留在聊天里
- 默认**不直接改动 AgenticX 代码**：先产出差距分析与技术方案；若我明确要求落地实现，再进入编码阶段
- 如遇到网络/权限/反爬导致无法抓取：必须说明原因，并给出替代策略（例如浏览器提取/手动提供内容）

---

**用法示例**
- 仅研究仓库：
  - `/codedeepresearch https://github.com/owner/repo`
- 仓库 + 资料：
  - `/codedeepresearch https://github.com/owner/repo https://mp.weixin.qq.com/s/xxxxx https://some.blog/post`

---

**GitHub 仓库（必选）与可选资料**：$ARGUMENTS
