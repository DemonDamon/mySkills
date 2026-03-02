# 信息搜集阶段详细指南

Phase 1 操作细节与模板，流程概览见 [SKILL.md](SKILL.md)。

## 1. 搜索 Query 构造策略

基于用户提供的种子信息，构造多组搜索 query 以覆盖不同维度：

| 维度 | Query 模板示例 |
|------|--------------|
| 原理概览 | `<技术名> 原理 架构 详解` |
| 工程实践 | `<技术名> 实战 部署 最佳实践` |
| 对比分析 | `<技术名> vs <竞品> 对比 优劣` |
| 源码解析 | `<技术名> 源码分析 核心模块` |
| 最新动态 | `<技术名> 2025 2026 最新进展` |
| 踩坑经验 | `<技术名> 踩坑 问题 limitations` |
| 性能评测 | `<技术名> benchmark 性能测试 评测` |
| 英文补充 | `<tech_name> architecture deep dive tutorial` |

**搜索工具使用示例**：

### bocha-search-mcp（首选）

```
bocha_web_search:
  query: "LangChain Agent 架构原理详解"
  count: 10
  freshness: "oneYear"

bocha_ai_search:
  query: "LangChain vs LlamaIndex 对比分析"
  count: 10
```

### zhipu-web-search-sse（补充）

```
webSearchPro:
  search_query: "LangChain Agent 源码分析核心模块"
  count: 10
  content_size: "high"
  search_recency_filter: "oneYear"
```

**搜索结果处理**：
- 合并去重所有搜索结果
- 按相关性和质量排序
- 筛选出**至少 10 篇**高价值页面（优先级：官方文档 > 官方博客 > 技术博客 > 论坛讨论）
- 落盘到 `sources/search_summary.md`

### search_summary.md 模板

```markdown
# 搜索结果汇总

## 搜索信息
- 主题：<博客主题>
- 搜索时间：<时间>
- 搜索 Query 列表：
  1. <query1>
  2. <query2>
  ...

## 高价值页面（待爬取）— 至少 10 篇
| # | 标题 | URL | 来源类型 | 价值评估 |
|---|------|-----|---------|---------|
| 1 | ... | ... | 官方文档 | 高 |
| 2 | ... | ... | 技术博客 | 高 |
...

## 官方页面（需截图）
| # | 页面 | URL | 截图文件名 |
|---|------|-----|-----------|
| 1 | 官网首页 | ... | screenshot_homepage.png |
| 2 | 架构图页 | ... | screenshot_architecture.png |
...

## 其他参考（摘要已足够，无需爬取）
| # | 标题 | URL | 关键摘要 |
|---|------|-----|---------|
| 1 | ... | ... | ... |

## PDF 链接（待下载到 sources/pdfs/）
| # | 标题/说明 | URL | 本地路径 |
|---|-----------|-----|---------|
| 1 | ... | https://arxiv.org/pdf/xxx.pdf | sources/pdfs/xxx.pdf |
```

### 1b. PDF 原文落盘（强制）

**规则**：用户提供的、以及搜索/爬取过程中发现的**所有论文/白皮书/报告等 PDF 直链，必须下载到本地**，保存到 `sources/pdfs/`，便于后续引用与 `extract_pdf_pages` 提图。

**操作**：
1. 在 Phase 0 澄清时询问用户是否有论文或报告 PDF 链接；在 1.1 搜索与 1.3 爬取中识别结果里的 PDF 链接（如 arxiv.org/pdf/、.pdf 结尾、常见论文站）。
2. 将全部 PDF URL 汇总（可写入 `sources/pdf_urls.txt`，一行一个 URL）。
3. 执行下载：
```bash
python tools/download_pdfs.py -o <output_dir>/sources/pdfs --url "https://arxiv.org/pdf/2301.xxxxx.pdf" --url "https://..."
# 或
python tools/download_pdfs.py -o <output_dir>/sources/pdfs --urls-file sources/pdf_urls.txt
```
4. 在 `search_summary.md` 中增加「PDF 链接（待下载）」表，记录已落盘的 PDF 与本地路径。

**失败处理**：若某 URL 返回非 PDF 或 403，记录到物料清单并说明，不阻塞流程；其余 PDF 照常下载。

## 2. 网页爬取详细操作

目标：至少 10 篇（官方文档 2~3、技术博客 3~5、评测 1~2、社区 1~3）。工具选择：

```
页面类型判断：
├── 静态页面（博客/文档/论文页）
│   └── crawl_single_url → 直接爬取
├── 重要参考页面（官方文档/核心论文）
│   └── crawl_with_quality_check → 爬取 + 质量检查
├── JS 渲染页面（SPA/动态加载/需要登录）
│   └── smart_crawl_single_url → 自动选择最佳策略
└── 批量页面（5+ 个同类页面）
    └── crawl_urls_from_text → 批量爬取
```

### 爬取参数建议

**crawl_single_url**：
```
url: "<target_url>"
output_dir: "<output_dir>/sources/web"
img_folder: "<output_dir>/images"
```

**smart_crawl_single_url**（推荐用于不确定页面类型时）：
```
url: "<target_url>"
output_dir: "<output_dir>/sources/web"
img_folder: "<output_dir>/images"
auto_switch_to_browser: true
use_llm_if_low_quality: false
```

**crawl_with_quality_check**（用于核心参考页面）：
```
url: "<target_url>"
output_dir: "<output_dir>/sources/web"
img_folder: "<output_dir>/images"
auto_rewrite: false
```

### 爬取后处理

每个爬取的 markdown 文件顶部应包含元信息：

```markdown
---
source_url: <原始 URL>
crawl_time: <爬取时间>
title: <页面标题>
quality: good/fair/poor
---
```

### 爬取失败的降级策略

1. **超时/403**：尝试 `smart_crawl_single_url`（自动切换浏览器模式）
2. **内容为空/质量差**：尝试 `crawl_with_quality_check` + `auto_rewrite: true`
3. **仍然失败**：记录到 `search_summary.md` 的失败列表，使用搜索摘要替代
4. **反爬严重**：告知用户，建议手动提供页面内容

## 3. 官方页面截图详细操作

爬虫无法完整保留架构图/benchmark 等视觉内容，需用浏览器或 `tools/capture_screenshots.py` 截图。流程：

```
1. browser_navigate → 打开目标 URL
2. browser_snapshot → 获取页面结构，确认加载完成
3. （可选）browser_scroll → 滚动到目标区域
4. browser_take_screenshot → 截图
5. 截图文件保存到 images/ 目录
```

### 必须截图的内容

| 内容类型 | 截图文件名示例 | 说明 |
|---------|--------------|------|
| 官网首页 | `screenshot_homepage.png` | 展示产品定位、核心功能 |
| 架构图/系统图 | `screenshot_architecture.png` | 官方提供的架构可视化 |
| Benchmark 结果 | `screenshot_benchmark.png` | 性能/准确率对比数据 |
| Demo/效果展示 | `screenshot_demo.png` | 产品实际使用效果 |
| 关键流程图 | `screenshot_flow.png` | 工作流程/Pipeline |

### 截图质量要求

- 确保页面完全加载（等待 JS 渲染完成）
- 截取关键内容区域，避免截取整个页面（太大/太杂）
- 如果一个页面有多个值得截取的区域，分别截图
- 截图分辨率要清晰可读

## 4. GitHub 仓库研究详细操作

### 4.1 git clone 到本地（必须！）

```bash
cd <output_dir>/sources/github/
git clone --depth 1 https://github.com/<owner>/<repo>.git
```

使用 `--depth 1` 做浅克隆，节省时间和空间。

### 4.2 本地代码分析流程

clone 完成后，按以下顺序进行本地代码分析：

#### Step 1: 了解项目布局

```
# 使用 Glob 工具扫描目录结构
Glob: **/*  (target_directory: sources/github/<repo>/)

# 或使用 Shell
ls -la sources/github/<repo>/
```

#### Step 2: 阅读项目配置

优先读取以下文件：
- `README.md` — 项目介绍、使用方法
- `requirements.txt` / `setup.py` / `pyproject.toml` — Python 依赖
- `package.json` — Node.js 依赖
- `Dockerfile` / `docker-compose.yml` — 容器化配置
- `.env.example` / `config.yaml` — 配置模板

#### Step 3: 定位核心代码

使用 Grep 搜索核心入口和关键实现：

```
# 搜索入口函数
Grep: "def main\|if __name__"
Grep: "class.*Pipeline\|class.*Engine\|class.*Index"

# 搜索关键配置
Grep: "API_KEY\|MODEL\|ENDPOINT"
```

#### Step 4: 阅读核心模块

使用 Read 工具逐个阅读核心文件：
- 入口文件（main / cli / app）
- 核心业务逻辑（pipeline / engine / processor）
- 数据模型（model / schema / types）
- 工具函数（utils / helpers）

#### Step 5: 记录分析结果

将所有分析写入 `sources/github/<repo>_code_analysis.md`：

```markdown
# <repo> 本地代码分析

## 仓库信息
- URL: <github_url>
- Clone 路径: sources/github/<repo>/
- 分析时间: <时间>

## 目录结构
<项目布局树>

## 依赖分析
- 语言: Python / Node.js / ...
- 核心依赖: <列出关键依赖及版本>
- 外部服务依赖: <LLM API / 数据库 / ...>

## 核心模块清单
| 文件 | 模块 | 功能说明 |
|------|------|---------|
| src/main.py | 入口 | CLI 启动 |
| src/engine.py | 核心引擎 | ... |
...

## 关键代码片段

### <模块名>: <功能>
**文件**: `<路径>`
**行号**: L<start>-L<end>
```python
# <代码片段，带注释>
```

### <模块名>: <功能>
...

## 数据流与调用关系
<描述核心调用链>

## 初步发现
- 发现1
- 发现2
```

### 4.3 DeepWiki 架构研究

**目标**：理解仓库的架构设计、核心概念和设计决策。

**提问策略**（至少覆盖以下 5 个方向，每方向 1~3 问）：

1. **架构与数据流**
   - "这个项目的核心架构是什么？主要组件有哪些？"
   - "数据/请求在系统中如何流转？"

2. **核心模块与机制**
   - "核心抽象有哪些？分别解决什么问题？"
   - "<具体模块>的工作原理是什么？"

3. **扩展与集成**
   - "如何扩展/自定义该框架？有哪些插件点？"
   - "与其他系统集成的推荐方式是什么？"

4. **设计权衡**
   - "为什么选择这种架构而非其他方案？有哪些 trade-off？"
   - "已知的限制和不足是什么？"

5. **性能与可靠性**
   - "性能优化的关键点在哪里？"
   - "错误处理和容错机制是怎样的？"

**落盘格式**：

```markdown
# <repo_name> DeepWiki 研究记录

## 仓库信息
- URL: <github_url>
- 研究时间: <时间>

## 文档结构
[read_wiki_structure 的返回结果]

## 问答记录

### Q1: <问题>
**A1**: <回答>

### Q2: <问题>
**A2**: <回答>

...

## 关键结论摘要
- 结论1
- 结论2
```

### 4.4 DeepWiki 与本地代码协同策略

```
1. 先 git clone 代码到本地              → 获取完整代码
2. 用 Glob/Read 了解项目布局            → 建立代码地图
3. 用 DeepWiki 问架构问题               → 理解设计意图
4. 用 Read/Grep 读取关键源码             → 验证 DeepWiki 的回答
5. 用 DeepWiki 追问设计决策              → 补充深层理解
6. 交叉验证 DeepWiki 结论与本地代码      → 确保准确性
```

## 5. 10 问深度工程分析详细操作

### 5.1 问题设计原则

**核心原则**：假设读者要拿这个技术投入真实生产，暴露所有优缺点。

**问题质量要求**：
- 不要问泛泛的理论问题，要问具体的工程问题
- 每个问题应能引出一个明确的「风险点」或「决策点」
- 问题之间不重叠，覆盖面要广

### 5.2 问题维度与示例

| 维度 | 问题示例 |
|------|---------|
| 性能与可扩展性 | "当文档超过 500 页时，树结构生成的时间和 token 消耗是多少？" |
| 可靠性与容错 | "LLM 对目录的推理出错时，下游检索全链路受影响吗？有无回退机制？" |
| 成本与资源 | "处理一份 100 页 PDF 需要调用多少次 LLM API？成本约多少？" |
| 适用边界 | "对于无目录结构的非标准 PDF（扫描件/表格为主），效果如何？" |
| 集成复杂度 | "接入现有的 RAG pipeline 需要改动哪些组件？兼容 LangChain 吗？" |
| 安全与合规 | "文档内容会发送到 OpenAI API 吗？如何满足数据驻留要求？" |
| 维护与演进 | "项目的发布节奏和社区活跃度如何？是否有长期维护承诺？" |
| 竞品对比 | "相比 LlamaIndex 的 TreeIndex，PageIndex 的真实优势在哪？" |
| 依赖风险 | "核心依赖 OpenAI GPT-4，如果 API 变更或不可用怎么办？" |
| 工程陷阱 | "官方 README 未提及但实际使用中可能遇到的问题有哪些？" |

### 5.3 回答研究方法

对每个问题，按以下优先级寻找答案：

1. **本地代码搜索**（最可靠）：Grep 关键词 → Read 相关代码 → 分析逻辑
2. **DeepWiki 追问**：`ask_question` 直接问 → 获取架构层面的解答
3. **已爬取网页**：在 `sources/web/` 中搜索相关内容
4. **补充网络搜索**：对信息不足的问题，额外搜索

### 5.4 落盘格式

```markdown
# <repo> 工程落地深度分析

## 研究基础
- 代码版本: <commit hash 或 clone 时间>
- 研究时间: <时间>
- 已有物料: search_summary.md + N 篇网页 + deepwiki.md + 本地代码

---

## Q1: <问题>

**维度**: 性能与可扩展性

**分析**:
<详细分析，引用代码/数据/文档>

**代码证据**:
```python
# 文件: <repo>/path/to/file.py  L42-L58
<关键代码片段>
```

**结论**: <一句话结论>

**风险等级**: 高/中/低

**建议**: <针对该风险的缓解措施>

---

## Q2: <问题>
...
```

## 6. 物料完整性检查清单

搜集结束后，对照以下清单确认物料充足度：

```
搜集物料检查：
- [ ] search_summary.md 已生成，包含 5~8 组搜索 query 和结果汇总
- [ ] **所有已知 PDF 链接已下载到 sources/pdfs/**（用户提供 + 搜索/爬取中发现的）
- [ ] 至少爬取了 10 篇高质量网页到 sources/web/
- [ ] 至少 3 张官方页面截图保存到 images/
- [ ] （若有 GitHub）仓库已 clone 到 sources/github/<repo>/
- [ ] （若有 GitHub）code_analysis.md 已生成，含目录结构和关键代码
- [ ] （若有 GitHub）deepwiki.md 已生成，包含至少 5 个 Q&A
- [ ] （若有 GitHub）engineering_questions.md 已生成，包含 10 个问题及详细回答

物料充足性评估：
- 核心概念/原理：是否有足够资料解释清楚？
- 实现细节：是否有真实代码片段可引用？
- 工程评估：10 问是否充分暴露了优缺点？
- 对比/评测：是否有数据或结论可参考？
- 插图：是否有官方截图和架构图可引用？
```

若评估为"不足"，向用户说明缺失内容并建议补充方式（提供更多 URL、论文 PDF 等）。
