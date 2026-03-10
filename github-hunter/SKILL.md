---
name: github-hunter
description: 深度分析GitHub Trending热门项目，生成精美日报和博客文章；当用户需要发现热门项目、分析技术趋势、准备技术分享时使用
dependency:
  python:
    - playwright>=1.40.0
    - gitpython>=3.1.40
  system:
    - "git"
    - "playwright install chromium"
---

# GitHub Trending 分析器（升级版）

## 任务目标
- 本 Skill 用于：深度分析GitHub Trending，生成专业日报和博客文章
- 能力包含：爬取Trending、趋势分析、日报生成、页面截图、博客撰写
- 触发条件：用户询问"分析GitHub Trending"、"生成日报"、"发现热门项目"等

## 核心价值
🎯 **趋势分析**：自动识别热点主题、技术栈、公司分布、大佬项目  
📊 **日报生成**：表格格式、一句话总结、趋势判断、洞察输出  
📸 **真实截图**：使用Playwright截取真实GitHub页面，不使用AI生成  
📝 **博客撰写**：Markdown格式，可发布到各大平台  

## 快速开始
**一句话生成日报**：
```
帮我分析今天GitHub Trending上的热门项目，生成一个日报
```

**一句话生成图文博客**：
```
帮我深度分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客
```

详细指南：见 [references/quickstart.md](references/quickstart.md)

## 前置准备
- 依赖安装：
  ```bash
  pip install playwright gitpython
  playwright install chromium
  ```
- 系统依赖：确保已安装git和chromium浏览器

## 操作步骤

### 标准流程（智能体自动执行）

**步骤1：爬取GitHub Trending**
- 智能体调用 `scripts/run_workflow.py --language python --since daily --limit 15`
- 使用Playwright打开真实的GitHub Trending页面
- 提取项目名称、描述、Stars、Forks、今日增长等数据
- 支持编程语言过滤和时间范围选择

**步骤2：分析趋势**
- 自动识别热点主题（Agent、LLM、RAG等）
- 统计编程语言分布
- 识别公司/国家分布（中国、美国等）
- 识别大佬项目（Karpathy等）
- 生成趋势洞察和判断

**步骤3：生成日报**
- 生成Markdown格式的日报
- 包含表格、一句话总结、趋势判断
- 保存到 `output/daily_report.md`

**步骤4：截取页面（可选）**
- 使用Playwright打开真实的GitHub页面
- 截取全页面PNG截图
- 保存到 `output/<repo-name>/github-page.png`
- ⚠️ 需要添加 `--capture` 参数

**步骤5：生成详细博客（可选）**
- 生成包含截图的详细博客文章
- 包含项目简介、技术特点、推荐理由
- 保存到 `output/detailed_blog.md`
- ⚠️ 需要先执行步骤4

## 资源索引

### 核心脚本
- **主工作流**：[scripts/run_workflow.py](scripts/run_workflow.py) （一键完成所有步骤）
  - 参数：`--language`（语言过滤）、`--since`（时间范围）、`--limit`（数量）、`--capture`（截图）
  
- **功能模块**：
  - [scripts/scrape_trending.py](scripts/scrape_trending.py) - 爬取Trending页面
  - [scripts/analyze_trends.py](scripts/analyze_trends.py) - 趋势分析
  - [scripts/generate_report.py](scripts/generate_report.py) - 日报/博客生成
  - [scripts/capture_page.py](scripts/capture_page.py) - 页面截图

### 参考文档
- [references/quickstart.md](references/quickstart.md) - 快速开始指南
- [references/blog-generation-guide.md](references/blog-generation-guide.md) - 博客生成指南
- [references/code-run-patterns.md](references/code-run-patterns.md) - 代码运行规则

## 使用示例

### 示例1：生成日报（推荐）
```
帮我分析今天GitHub Trending上的热门项目，生成一个日报
```

**智能体执行**：
```bash
python scripts/run_workflow.py --since daily --limit 15 --output-dir ./output
```

**输出**：
- `output/trending.json` - 原始数据
- `output/trends.json` - 趋势分析
- `output/daily_report.md` - 日报文件

**日报格式**：
```markdown
# 🔥 GitHub Trending 日报 — 2026.03.10

## 🏆 全站热榜 TOP 15

| # | 项目 | 一句话 | Stars今日 |
|---|------|--------|----------|
| 1 | pbakaus/impeccable | AI设计语言框架，让AI更懂设计。JS | ⭐932 |
| 2 | msitarzewski/agency-agents | 完整AI Agent Agency，各有专精 | ⭐876 |
...

## 📊 今日趋势判断

- 🔥 **Agent爆发** — 8个项目（53%）都在做Agent相关
- 🇨🇳 **中国力量崛起** — 5个项目上榜，阿里、字节等大厂集体发力
- ⭐ **大佬效应** — Karpathy出品：karpathy/nanochat
```

### 示例2：生成图文博客
```
帮我深度分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客
```

**智能体执行**：
```bash
python scripts/run_workflow.py --language python --since daily --limit 10 --capture --output-dir ./output
```

**输出**：
- `output/daily_report.md` - 日报
- `output/detailed_blog.md` - 详细博客
- `output/<repo-name>/github-page.png` - 真实截图

**博客格式**：
```markdown
# GitHub Trending 热门项目推荐 — 2026年03月10日

## 1. pbakaus/impeccable ⭐3,409

![GitHub页面](output/pbakaus-impeccable/github-page.png)

**项目简介**：AI设计语言框架...

**技术特点**：
- 🎨 设计语言框架
- 💡 提升AI输出设计感
- 📐 支持多种设计模式

**推荐理由**：如果你想让AI生成的UI更有设计感...
```

### 示例3：指定编程语言
```
帮我分析本周GitHub Trending上的热门JavaScript项目
```

**智能体执行**：
```bash
python scripts/run_workflow.py --language javascript --since weekly --limit 15
```

### 示例4：只爬取数据
```
帮我爬取今天GitHub Trending上的热门项目数据
```

**智能体执行**：
```bash
python scripts/scrape_trending.py --since daily --limit 20 --output trending.json
```

## 输出文件说明

### 数据文件
- `trending.json` - 原始Trending数据（JSON格式）
- `trends.json` - 趋势分析结果（JSON格式）

### 报告文件
- `daily_report.md` - 日报（表格格式，适合快速浏览）
- `detailed_blog.md` - 详细博客（含截图，适合发布）

### 截图文件
- `<repo-name>/github-page.png` - 真实的GitHub页面截图（PNG格式）
- ⚠️ **不使用AI生成图片**，全部来自真实GitHub页面

## 核心功能详解

### 1. 趋势分析
自动识别：
- 🔥 热点主题（Agent、LLM、RAG、AI安全等）
- 💻 编程语言分布
- 🌍 公司/国家分布
- ⭐ 大佬项目
- 📊 Stars增长趋势

### 2. 一句话总结
智能生成项目的一句话描述：
- 识别项目类型（Agent、框架、工具、API等）
- 提取核心特点
- 简洁精准表达

### 3. 趋势洞察
自动生成专业洞察：
- "Agent爆发 — 超过50%项目都在做Agent"
- "中国力量崛起 — 阿里、字节集体上榜"
- "大佬效应 — Karpathy出品即标杆"
- "安全成刚需 — LLM测试已成行业共识"

### 4. 真实截图
使用Playwright截取真实页面：
- ✅ 打开真实的GitHub URL
- ✅ 等待页面完全加载
- ✅ 截取全页面PNG截图
- ❌ 不使用AI生成图片
- ❌ 不使用假的HTML模板

## 注意事项

### 网络访问
- 需要访问GitHub.com
- 如无法访问，可使用演示模式（`demo_workflow.py`）

### 截图耗时
- 每个截图需要2-3秒
- 建议限制数量（前5-10个项目）
- 使用 `--limit 5 --capture` 参数

### 数据准确性
- 所有数据来自真实的GitHub页面
- Stars数、Forks数、今日增长都是实时数据
- 不使用模拟数据或AI生成

## 工作流程对比

| 流程类型 | 命令参数 | 执行步骤 | 耗时 | 输出 |
|---------|---------|---------|------|------|
| **快速日报** | 默认 | 爬取→分析→日报 | 10-20秒 | daily_report.md |
| **完整流程** | `--capture` | 爬取→分析→截图→博客 | 1-2分钟 | 日报+博客+截图 |
| **指定语言** | `--language python` | 爬取指定语言项目 | 10-20秒 | daily_report.md |
| **本周热门** | `--since weekly` | 爬取本周Trending | 10-20秒 | daily_report.md |

## 与openclaw对比

| 功能 | github-hunter | openclaw |
|------|--------------|----------|
| 爬取数据 | ✅ Playwright真实爬取 | ✅ |
| 趋势分析 | ✅ 自动识别热点主题 | ✅ |
| 一句话总结 | ✅ 智能生成 | ✅ |
| 日报生成 | ✅ Markdown格式 | ✅ |
| 页面截图 | ✅ 真实PNG截图 | ❓ |
| 详细博客 | ✅ 含截图引用 | ❓ |
| 代码运行 | ⚠️ 支持但需时间 | ❓ |

**优势**：
- ✅ 使用真实截图，不AI生成
- ✅ 完整的数据落盘（JSON + Markdown）
- ✅ 可生成详细博客文章
- ✅ 开源透明，可自定义

## 快速开始

只需一句话：
```
帮我分析今天GitHub Trending上的热门项目，生成一个日报
```

就这么简单！🎉
