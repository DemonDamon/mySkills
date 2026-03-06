---
name: github-hunter
description: 深度分析GitHub Trending热门项目，自动截图、运行代码、落盘保存；当用户需要挖掘热门项目、体验代码效果、准备技术分享时使用
dependency:
  python:
    - playwright>=1.40.0
    - gitpython>=3.1.40
  system:
    - "git"
    - "playwright install chromium"
---

# AI项目猎手（深度分析版）

## 任务目标
- 本 Skill 用于：深度分析GitHub Trending热门项目，实现"截图、使用、落盘"的完整流程
- 能力包含：爬取Trending页面、逐个打开仓库、截取页面、克隆代码、运行示例、保存所有数据
- 触发条件：用户询问"分析GitHub Trending"、"体验热门项目代码"、"深度评测开源项目"等

## 核心价值
🎯 **截图**：自动打开GitHub页面和Demo页面，截取全页面截图  
🚀 **使用**：克隆仓库到本地，安装依赖，运行示例代码  
💾 **落盘**：保存所有截图、代码输出、分析结果到磁盘  

## 前置准备
- 依赖安装：
  ```bash
  pip install playwright gitpython
  playwright install chromium
  ```
- 系统依赖：确保已安装git和chromium浏览器

## 快速开始
**一句话生成GitHub Trending博客**：
```
帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍
```

**更多提问方式**：
- 指定语言：`帮我分析今天GitHub Trending上的热门JavaScript项目，生成一个图文并茂的博客介绍`
- 指定时间：`帮我分析本周GitHub Trending上的热门AI项目，生成一个图文并茂的博客介绍`
- 深度分析：`帮我深度分析今天GitHub Trending上的热门项目，包括运行代码体验，生成一个图文并茂的博客介绍`

详细指南：见 [references/quickstart.md](references/quickstart.md)

## 操作步骤
- 标准流程（5步走）：
  
  **步骤1: 爬取GitHub Trending**
  - 调用 `scripts/deep_analyze.py --scrape --limit 3`
  - 自动打开 https://github.com/trending
  - 提取热门仓库列表（名称、描述、Stars、Forks等）
  - 支持编程语言过滤：`--language python`
  - 支持时间范围过滤：`--since daily/weekly/monthly`
  
  **步骤2: 深度分析单个仓库**
  - 对每个仓库执行完整分析流程：
    - 📸 打开GitHub页面 → 截图全页面
    - 📋 提取README、技术栈、元数据
    - 🔗 如果有Demo链接 → 打开并截图
    - 📥 克隆仓库到本地
  
  **步骤3: 运行代码体验**
  - 智能检测编程语言（Python/JavaScript/Go/Rust）
  - 自动安装依赖（pip/npm/go mod/cargo）
  - 查找示例代码（examples/、demo/、tests/目录）
  - 运行示例并记录输出
  - ⚠️ 需要添加 `--run-code` 参数
  
  **步骤4: 数据落盘保存**
  - 为每个仓库创建独立目录：`output/<repo-name>/`
  - 保存内容：
    - `github-page.png` - GitHub页面截图
    - `demo-page.png` - Demo页面截图（如果有）
    - `analysis.json` - 完整分析结果
    - `code-run-result.json` - 代码运行结果（如果运行了）
  - 保存总览：`output/summary.json`
  
  **步骤5: 生成分析报告**
  - 智能体基于分析结果撰写专业评测
  - 包含技术架构、代码体验、生产建议
  - 引用实际截图和运行输出

- 简化流程（仅截图，不运行代码）：
  - 调用 `scripts/deep_analyze.py --scrape --limit 3 --output-dir ./output`
  - 执行步骤1、2、4、5，跳过步骤3
  - 适用于：快速浏览、准备素材

- 完整流程（含代码运行）：
  - 调用 `scripts/deep_analyze.py --scrape --limit 3 --run-code --output-dir ./output`
  - 执行全部5个步骤
  - 适用于：深度评测、技术分享

## 资源索引
- 核心脚本：
  - [scripts/deep_analyze.py](scripts/deep_analyze.py) （主脚本：协调整个流程）
    - 参数：`--scrape`（爬取Trending）、`--repos-file`（从文件加载）、`--language`（语言过滤）、`--since`（时间范围）、`--limit`（数量限制）、`--run-code`（运行代码）
  - [scripts/scrape_trending.py](scripts/scrape_trending.py) （爬取Trending页面）
  - [scripts/capture_page.py](scripts/capture_page.py) （页面截图）
  - [scripts/clone_and_run.py](scripts/clone_and_run.py) （克隆并运行代码）
- 领域参考：
  - [references/code-run-patterns.md](references/code-run-patterns.md) （何时读取：了解代码运行规则）

## 数据输出结构

### 单个仓库输出目录
```
output/
├── owner-repo/              # 每个仓库一个目录
│   ├── github-page.png      # GitHub页面全页面截图
│   ├── demo-page.png        # Demo页面截图（如果有）
│   ├── analysis.json        # 完整分析结果
│   └── code-run-result.json # 代码运行结果（如果运行了）
└── summary.json             # 所有仓库的总览
```

### analysis.json 格式
```json
{
  "repo": {
    "name": "owner/repo",
    "url": "https://github.com/owner/repo",
    "description": "...",
    "language": "Python",
    "stars": 12345,
    "forks": 456
  },
  "screenshots": {
    "github_page": "output/owner-repo/github-page.png",
    "demo_page": "output/owner-repo/demo-page.png"
  },
  "code_run": {
    "cloned": true,
    "language": {"detected": true, "language": "Python"},
    "dependencies_installed": true,
    "examples_found": ["examples/demo.py"],
    "examples_run": [...]
  },
  "output_dir": "output/owner-repo"
}
```

## 注意事项
- **代码运行需要时间**：克隆、安装、运行可能需要几分钟，建议先用 `--limit 1` 测试
- **网络要求**：需要访问GitHub和可能的包管理器（PyPI、npm等）
- **磁盘空间**：每个仓库约占用10-100MB（代码+依赖）
- **安全考虑**：代码运行在隔离环境中，避免运行有风险的代码
- **超时控制**：单个示例运行超时30秒，避免无限等待
- **错误处理**：依赖安装失败或示例运行失败会记录错误，不影响其他仓库

## 使用示例

### 示例1：快速浏览GitHub Trending（仅截图）
- 功能说明：爬取今日Trending，截图保存，不运行代码
- 执行方式：简化流程
- 命令：
  ```bash
  python scripts/deep_analyze.py --scrape --since daily --limit 5 --output-dir ./output
  ```
- 输出：每个仓库的GitHub页面截图 + 分析结果

### 示例2：深度分析Python项目（含代码运行）
- 功能说明：爬取Python Trending，深度分析并运行示例代码
- 执行方式：完整流程
- 命令：
  ```bash
  python scripts/deep_analyze.py --scrape --language python --since weekly --limit 3 --run-code --output-dir ./output
  ```
- 输出：GitHub截图 + 代码运行输出 + 完整分析结果

### 示例3：从已有仓库列表分析
- 功能说明：分析指定的仓库列表（不爬取Trending）
- 执行方式：完整流程
- 命令：
  ```bash
  python scripts/deep_analyze.py --repos-file trending-repos.json --run-code --output-dir ./output
  ```
- 输入：`trending-repos.json`（仓库列表JSON文件）
- 输出：所有仓库的完整分析结果

### 示例4：仅截图指定URL
- 功能说明：对单个仓库URL进行截图
- 执行方式：独立截图
- 命令：
  ```bash
  python scripts/capture_page.py --url https://github.com/owner/repo --output repo-screenshot.png
  ```
- 输出：`repo-screenshot.png`

### 示例5：仅运行指定仓库代码
- 功能说明：克隆并运行指定仓库的示例代码
- 执行方式：独立运行
- 命令：
  ```bash
  python scripts/clone_and_run.py --repo https://github.com/owner/repo --output run-result.json
  ```
- 输出：`run-result.json`（包含代码运行输出）

### 示例6：生成图文并茂的博客文章（智能体主导）
- 功能说明：基于深度分析结果，生成Markdown格式的博客文章
- 执行方式：智能体分析→撰写文章
- 提问示例：
  - "帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍"
  - "帮我分析本周GitHub Trending上的热门AI项目，生成一个图文并茂的博客文章"
- 智能体会自动：
  1. 调用 `deep_analyze.py` 分析项目（截图、运行代码）
  2. 读取 `summary.json` 和各个仓库的 `analysis.json`
  3. 生成包含图片的Markdown文章
  4. 插入GitHub页面截图和代码运行结果
- 输出：完整的Markdown博客文章（可发布到GitHub Pages、个人博客、技术社区）

## 工作流程对比

| 流程类型 | 命令参数 | 执行步骤 | 耗时 | 适用场景 |
|---------|---------|---------|------|---------|
| **简化流程** | 默认（无--run-code） | 爬取→截图→保存 | 1-2分钟 | 快速浏览、准备素材 |
| **完整流程** | 添加 `--run-code` | 爬取→截图→克隆→运行→保存 | 5-10分钟 | 深度评测、技术分享 |
| **单仓库分析** | `--repos-file` | 从文件加载→深度分析 | 视仓库大小而定 | 分析特定项目 |
| **博客生成** | 智能体自动调用 | 分析→截图→撰写→生成 | 5-15分钟 | 生成图文并茂的博客文章 |
