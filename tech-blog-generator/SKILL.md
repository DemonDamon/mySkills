---
name: tech-blog-generator
description: 基于种子信息（关键词、URL、GitHub 仓库等）进行网络检索与资料爬取，然后生成图文并茂的中文技术博客。包含信息搜集、图片智能处理（自动过滤+闭环生图）、三轮写作（大纲→初稿→自评修正）。Use when the user wants to research a technical topic and generate a blog post, or mentions writing a tech blog, creating technical content, or deep-diving into a technology topic.
---

# Tech Blog Generator

基于种子信息进行深度研究，搜集充足资料后生成一篇高质量中文技术博客。支持 Cursor 与 Claude Code，可自由迁移。

## 参数（用户输入）

- **种子信息**（必选）：主题关键词、技术名称、论文标题等
- **参考 URL 列表**（可选）：相关博客/推文/文档链接
- **PDF/论文 URL 列表**（可选）：论文、白皮书、报告等 PDF 直链；**若有则必须下载到本地**，落盘到 `sources/pdfs/`
- **GitHub 仓库地址**（可选）：`https://github.com/<owner>/<repo>`
- **输出目录**（可选）：默认 `~/tech-blog/<topic>/`

## 产物目录结构

```
<output_dir>/
├── progress.md                # 进度追踪（支持断点恢复）
├── outline.md                 # 大纲 + 图文配对方案
├── blog.md                    # 最终技术博客
├── sources/
│   ├── search_summary.md
│   ├── web/
│   ├── github/
│   └── pdfs/
├── images/
│   ├── image_audit.json       # 图片审计结果
│   ├── _noise/                # 被过滤的噪声图片
│   └── (screenshot_*.png | pdf_*.png | diagram_*.jpg)
└── visual-prompts/            # 视觉描述提示词（追溯用）
```

## 工作流程（严格按顺序执行）

### Phase 0: 澄清与确认

用不超过 5 个问题确认：主题、种子信息、侧重点、目标读者、输出路径。能默认就默认，能推断就推断。确认后创建目录结构并初始化 `progress.md`。

### Phase 1: 信息搜集（Research）

详细操作见 [research-guide.md](research-guide.md)。摘要：

1. **1.1 网络搜索**：使用 bocha-search-mcp / zhipu-web-search，5~8 组 query，结果汇总到 `sources/search_summary.md`，筛选至少 10 篇高价值页面；**从结果中识别并记录所有 PDF 链接**（论文、报告、白皮书等）。
2. **1.2 PDF 原文落盘**：用户提供的、以及搜索/爬取中发现的**所有 PDF 链接必须下载到本地**。运行 `python tools/download_pdfs.py -o <output_dir>/sources/pdfs --url "<url1>" --url "<url2>"`（或 `--urls-file pdf_urls.txt`），保存到 `sources/pdfs/`，供后续引用与 extract_pdf_pages 提图。
3. **1.3 网页爬取**：使用 basic-web-crawler（crawl_single_url / smart_crawl_single_url / crawl_urls_from_text），至少 10 篇，落盘到 `sources/web/`，图片到 `images/`。
4. **1.4 官方页面截图**：对官网/文档/Benchmark 页必须截图。方式 A：MCP 浏览器（browser_navigate → browser_take_screenshot）；方式 B：`python tools/capture_screenshots.py -o <output_dir>/images --tasks '[...]'`。支持 `selectors` + `selector_names` 做区域截图。
5. **1.5 GitHub 研究**（若有）：git clone 到 `sources/github/<repo>/`，DeepWiki（read_wiki_structure / ask_question）落盘 `*_deepwiki.md`，本地代码分析落盘 `*_code_analysis.md`。
6. **1.6 10 问工程落地分析**：提出 10 个复杂工程问题（性能、容错、成本、边界、集成、安全、维护、竞品、依赖、陷阱），落盘 `*_engineering_questions.md`。详见 research-guide。
7. **1.7 物料清单**：输出勾选清单（含 `sources/pdfs/` 下已下载 PDF），确认充足后进入 Phase 1.5。每完成一步更新 `progress.md`。

### Phase 1.5: 图片智能处理（自动执行，无需用户介入）

1. **过滤噪声**：`python tools/image_filter.py -i <output_dir>/images`。C 级移入 `images/_noise/`，审计结果写 `images/image_audit.json`。
2. **达标判定**：A 级 ≥ 3 张，可用总量（A+B）≥ 5 张。不达标则补救：
   - 缺官方/benchmark 图 → 浏览器截图（capture_screenshots.py 或 MCP browser）
   - 有 PDF 种子 → `python tools/extract_pdf_pages.py <pdf> -o <output_dir>/images --mapping '{...}'`
   - 仍缺自绘图 → 按 protocols/text-to-visual-prompt.md 生成视觉描述提示词，再 `python tools/generate_diagram.py --prompt-file visual-prompts/xx.txt -o images/xx.jpg --api gemini`（或 fallback 保存提示词，由用户/Lovart 生成）
3. **图表生成优先级**：Gemini API 闭环生图 > doubao/text_to_image MCP > 保存提示词到 visual-prompts；仅当都不可用时才用 mermaid 作为 fallback。
4. 补救后再次运行 image_filter 审计，达标后进入 Phase 2。

### Phase 2: 博客写作（三轮）

详细规范见 [writing-guide.md](writing-guide.md)。

- **Round 1 — 大纲 + 图文配对**：基于物料生成 `outline.md`，每个 H2/H3 标明核心论点与配图（来自 images/ 或待生成）。
- **Round 2 — 完整初稿**：按 outline 写作，严格执行图文引用，落盘 `blog.md`。
- **Round 3 — 自评与修正**：对 blog.md 执行自评 checklist（信息密度、数据支撑、图文一致、术语一致、10 问融入、篇幅等），对低于 8 分的项修正，再落盘。

**写作约束**：中文；资深技术人员风格；4000–6000 字；内容框架含背景、架构总览、核心模块、创新点、工程要点、实验/评测、生产落地评估、局限与展望。插图优先官方截图与 images/，自绘图优先 Gemini/闭环生图，其次 mermaid。代码引用本地 clone 真实片段，短且带注释。

### Phase 3: 交付

保存 `blog.md` 后回报：最终路径、大纲、引用图片列表、待生成视觉提示词列表（若有）、主要参考资料。不在聊天中贴全文。

## 执行约束

- 先搜集，后写作；必须完成 Phase 1 再进入 Phase 1.5，再 Phase 2。
- 所有中间产物与最终博客必须落盘；每阶段更新 `progress.md`。
- 涉及 GitHub 必须 git clone 到本地；**用户提供或搜索/爬取中发现的 PDF 链接必须下载到 sources/pdfs/**；网页不少于 10 篇；官方页必须截图；10 问必须完成。
- 进入写作前图片门禁：A 级 ≥ 3，可用 ≥ 5；不达标则执行 Phase 1.5 补救。
- 核心章节（架构、评测、产品界面）必须有配图，禁止纯文字。
- 自绘图优先 Gemini/闭环生图，mermaid 仅作 fallback。

## 附带工具

| 工具 | 用途 |
|------|------|
| [tools/download_pdfs.py](tools/download_pdfs.py) | 从 URL 下载 PDF 到 sources/pdfs/（论文/白皮书/报告原文落盘） |
| [tools/image_filter.py](tools/image_filter.py) | 图片质量过滤，生成 image_audit.json，C 级移入 _noise/ |
| [tools/capture_screenshots.py](tools/capture_screenshots.py) | Playwright 批量截图，支持 scrolls / full_page / selectors |
| [tools/extract_pdf_pages.py](tools/extract_pdf_pages.py) | PDF 指定页导出为 PNG |
| [tools/generate_diagram.py](tools/generate_diagram.py) | 从视觉描述提示词闭环生图（Gemini API 或 fallback 保存提示词） |

## 附带规约

| 文件 | 用途 |
|------|------|
| [protocols/text-to-visual-prompt.md](protocols/text-to-visual-prompt.md) | 文本/逻辑 → 中文视觉描述提示词 |
| [protocols/image-to-visual-prompt.md](protocols/image-to-visual-prompt.md) | 已有图 → 中文化重绘提示词 |

## 参考文档

- 信息搜集细节：[research-guide.md](research-guide.md)
- 写作规范与自评 checklist：[writing-guide.md](writing-guide.md)
