# 快速开始指南

## 一句话生成GitHub Trending博客

### 最简单的方式（推荐）

```
帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍
```

智能体会自动：
1. 爬取今日GitHub Trending
2. 分析Top 3-5个项目
3. 截取GitHub页面
4. 运行代码体验
5. 生成图文并茂的博客文章

---

## 更多提问方式

### 指定编程语言
```
帮我分析今天GitHub Trending上的热门JavaScript项目，生成一个图文并茂的博客介绍
```

### 指定时间范围
```
帮我分析本周GitHub Trending上的热门AI项目，生成一个图文并茂的博客介绍
```

### 深度分析（含代码运行）
```
帮我深度分析今天GitHub Trending上的热门项目，包括运行代码体验，生成一个图文并茂的博客介绍
```

### 指定项目列表
```
帮我分析这几个项目：langchain-ai/langchain、openai/transformers、huggingface/peft，生成一个图文并茂的博客介绍
```

---

## 生成的博客文章结构

智能体会按照以下结构生成：

```markdown
# [标题] - GitHub Trending热门项目推荐

## 导语
简要介绍今天的主题

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
```

---

## 输出示例

### 输入
```
帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍
```

### 输出
智能体会生成类似这样的博客文章：

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

**推荐理由**：
这是一个非常有前景的多智能体框架，特别适合需要构建复杂AI应用的场景...

## 2. langchain-ai/langchain ⭐ 78,000

![GitHub页面](output/langchain-ai-langchain/github-page.png)

...（更多项目）

## 总结
今天的GitHub Trending展示了一些非常有趣的趋势...
```

---

## 常见使用场景

### 场景1：技术博主写文章
```
帮我分析本周GitHub Trending上的热门AI项目，生成一个图文并茂的博客介绍
```

### 场景2：准备技术分享
```
帮我深度分析今天GitHub Trending上的热门机器学习项目，生成一个图文并茂的技术分享文档
```

### 场景3：学习新技术
```
帮我分析今天GitHub Trending上的热门Python项目，生成一个学习指南
```

### 场景4：发现新工具
```
帮我分析今天GitHub Trending上的热门开发者工具，生成一个推荐列表
```

---

## 高级功能

### 1. 指定博客风格
```
帮我分析今天GitHub Trending上的热门项目，生成一个图文并茂的博客介绍，风格要专业一点，包含技术细节和架构分析
```

### 2. 生成HTML格式
```
帮我分析今天GitHub Trending上的热门项目，生成一个图文并茂的HTML格式博客
```

### 3. 批量生成
```
帮我分析今天GitHub Trending上的热门Python、JavaScript、Go项目，分别生成三篇博客文章
```

---

## 注意事项

### 网络访问限制
- 如果无法访问GitHub，会自动使用离线模式（模拟数据）
- 生成的博客会标注"演示模式"

### 代码运行耗时
- 使用代码运行功能时，每个项目需要3-5分钟
- 建议限制数量为1-2个项目

### 截图质量
- 使用Playwright截取全页面截图
- 等待页面完全加载
- 自动处理动态内容

---

## 下一步

- 详细使用指南：查看 `references/blog-generation-guide.md`
- 完整文档：查看 `SKILL.md`
- 代码运行规则：查看 `references/code-run-patterns.md`

---

## 立即开始

只需一句话：

```
帮我分析今天GitHub Trending上的热门Python项目，生成一个图文并茂的博客介绍
```

就这么简单！🎉
