# GitHub Trending博客生成指南

本文档说明如何使用github-hunter Skill生成图文并茂的GitHub Trending介绍博客。

## 完整流程

### 第一步：分析GitHub Trending热门项目

**推荐提问方式**：

```
帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍
```

**系统会自动执行**：
1. 爬取今日GitHub Trending（Python语言）
2. 对Top 3-5个项目进行深度分析：
   - 截取GitHub页面
   - 克隆代码并运行示例
   - 提取技术栈和架构信息
3. 保存所有截图和数据到磁盘

### 第二步：生成图文并茂的博客文章

**推荐提问方式**：

```
基于刚才分析的结果，帮我写一篇图文并茂的博客文章，介绍今天GitHub Trending上的热门Python项目
```

**智能体会生成**：
- 📝 完整的Markdown格式博客文章
- 🖼️ 插入所有GitHub页面截图
- 🚀 插入代码运行结果截图
- 🔬 深度技术分析
- ⭐ 推荐理由和使用场景

---

## 推荐提问模板

### 模板1：今日热门项目（最推荐）
```
帮我分析今天GitHub Trending上的热门AI项目，生成一个图文并茂的博客介绍
```

### 模板2：指定编程语言
```
帮我分析今天GitHub Trending上的热门Python机器学习项目，生成一个图文并茂的博客介绍
```

### 模板3：本周热门项目
```
帮我分析本周GitHub Trending上的热门项目，生成一个图文并茂的博客介绍
```

### 模板4：深度分析（含代码运行）
```
帮我深度分析今天GitHub Trending上的热门项目，包括运行代码体验，生成一个图文并茂的博客介绍
```

### 模板5：指定仓库列表
```
帮我分析这几个项目：langchain-ai/langchain、openai/transformers，生成一个图文并茂的博客介绍
```

---

## 完整对话示例

### 示例1：最简单的方式

**用户**：
```
帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍
```

**智能体执行流程**：
1. 调用 `scripts/deep_analyze.py --scrape --language python --since daily --limit 5 --output-dir ./output`
2. 等待分析完成（约2-3分钟）
3. 读取 `output/summary.json` 和各个仓库的分析结果
4. 生成博客文章，包含：
   - 项目介绍
   - 技术特点
   - GitHub页面截图
   - 代码运行结果
   - 推荐理由

**输出**：
```markdown
# 今日GitHub Trending热门Python项目推荐

今天GitHub Trending上有几个非常有趣的Python项目，让我们一起来看看吧！

## 1. modelscope/agentscope ⭐ 17,000

![GitHub页面](output/modelscope-agentscope/github-page.png)

**项目简介**：
An innovative framework for building multi-agent applications with ease, featuring open-source LLMs and tool-use capabilities.

**技术特点**：
- 🤖 支持多智能体协作
- 🔧 集成多种LLM模型
- 🛠️ 丰富的工具调用能力

**代码体验**：
```bash
$ python examples/demo.py
Demo output: Hello from agentscope!
Multi-agent system initialized successfully.
```

**推荐理由**：...
```

---

### 示例2：分步执行（更灵活）

**第一步：分析项目**
```
帮我分析今天GitHub Trending上的热门AI项目
```

**智能体执行**：
- 调用 `scripts/deep_analyze.py --scrape --since daily --limit 5`
- 保存所有数据到 `./output/` 目录

**第二步：生成博客**
```
基于刚才的分析结果，帮我写一篇图文并茂的博客文章
```

**智能体执行**：
- 读取 `output/summary.json`
- 读取各个仓库的截图和分析结果
- 生成完整的博客文章

---

## 博客文章结构

智能体会按照以下结构生成博客：

```markdown
# [标题] - GitHub Trending热门项目推荐

## 导语
简要介绍今天的主题（如：AI、Python、机器学习等）

## 项目列表

### 1. 项目名称 ⭐ Stars数
![GitHub页面截图](output/repo-name/github-page.png)

**项目简介**：...

**技术特点**：
- 特点1
- 特点2

**代码体验**（如果运行了代码）：
```bash
运行结果输出...
```

**推荐理由**：...

### 2. 项目名称 ⭐ Stars数
...（重复上述结构）

## 总结
总结今天的发现和趋势

## 参考链接
- GitHub Trending: https://github.com/trending
```

---

## 输出文件说明

执行后会生成以下文件：

```
output/
├── repo-name-1/
│   ├── github-page.png          # GitHub页面截图
│   ├── demo-page.png            # Demo页面截图（如果有）
│   └── analysis.json            # 完整分析结果
├── repo-name-2/
│   ├── github-page.png
│   └── analysis.json
└── summary.json                 # 所有仓库的总览
```

**智能体使用的数据**：
- `summary.json` - 获取所有仓库的概览信息
- `repo-name/analysis.json` - 获取单个仓库的详细信息
- `repo-name/github-page.png` - 插入到博客文章中作为图片

---

## 注意事项

### 1. 网络访问限制
如果当前环境无法访问GitHub，智能体会：
- 自动使用离线模式（模拟数据）
- 生成演示版本的博客文章
- 在文章中标注"演示模式"

### 2. 代码运行耗时
如果使用 `--run-code` 参数：
- 每个项目需要3-5分钟（克隆+安装+运行）
- 建议限制数量为1-2个项目
- 可以分批分析

### 3. 截图质量
- 使用Playwright截取全页面截图
- 等待页面完全加载
- 自动处理动态内容

### 4. 文件路径
- 所有路径都是相对路径
- 博客文章中的图片路径：`output/repo-name/github-page.png`
- 可以直接在Markdown编辑器中预览

---

## 快速开始

### 最简单的一句话（推荐）
```
帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍
```

### 想要更详细的分析
```
帮我深度分析今天GitHub Trending上的热门AI项目，包括运行代码体验，生成一个图文并茂的博客介绍
```

### 想要分析本周热门
```
帮我分析本周GitHub Trending上的热门项目，生成一个图文并茂的博客介绍
```

---

## 高级用法

### 指定项目列表
```
帮我分析这几个项目：langchain-ai/langchain、openai/transformers、huggingface/peft，生成一个图文并茂的博客介绍
```

### 自定义博客风格
```
帮我分析今天GitHub Trending上的热门项目，生成一个图文并茂的博客介绍，风格要专业一点，包含技术细节和架构分析
```

### 生成HTML格式
```
帮我分析今天GitHub Trending上的热门项目，生成一个图文并茂的HTML格式博客
```

---

## 常见问题

### Q: 能否分析非Trending的项目？
A: 可以，直接提供仓库列表或URL即可。

### Q: 能否运行代码并截图？
A: 可以，智能体会在分析时自动运行示例代码并记录输出。

### Q: 生成的博客可以发布到哪里？
A: 支持Markdown格式，可以发布到：
- GitHub Pages
- 个人博客（Hugo、Jekyll等）
- 技术社区（掘金、CSDN等）
- 知乎专栏

### Q: 能否批量分析多个时间范围？
A: 可以，分别运行daily、weekly、monthly的分析，然后合并生成博客。

---

## 总结

使用github-hunter Skill生成GitHub Trending博客的步骤：

1. **提问**：描述你的需求（如"分析今天GitHub Trending热门Python项目"）
2. **等待**：智能体自动分析、截图、运行代码（2-5分钟）
3. **生成**：智能体基于分析结果生成图文并茂的博客文章
4. **发布**：直接使用生成的Markdown文章

就这么简单！🎉
