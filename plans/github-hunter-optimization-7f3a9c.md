# GitHub Hunter 技能优化方案

## 现状

### 问题描述
在实际使用 github-hunter 技能时，遇到了以下问题：

1. **ModuleNotFoundError** - Python 模块导入失败
   ```
   ModuleNotFoundError: No module named 'scripts'
   ```
   原因：脚本使用相对导入，但运行时 PYTHONPATH 未正确设置

2. **Skill 工具调用失败**
   ```
   Unknown skill: github-hunter
   ```
   原因：技能未正确注册到 Claude Code 的技能系统中

3. **执行路径依赖** - 需要手动 cd 到技能目录并设置环境变量

### 当前目录结构
```
github-hunter/
├── SKILL.md
├── scripts/              # 18个Python脚本
│   ├── run_workflow.py   # 主入口
│   ├── scrape_trending.py
│   ├── analyze_trends.py
│   └── ...
├── references/
├── assets/
└── output/               # 运行时生成
```

### 执行流程（当前）
```
用户请求
    ↓
Skill 工具调用 ❌（未注册）
    ↓
手动 Bash 执行
    ↓
cd github-hunter/
    ↓
PYTHONPATH=. python3 scripts/run_workflow.py ✅
```

---

## 核心概念

### 技能注册机制
```
┌─────────────────────────────────────────────────────────┐
│                   Claude Code 技能系统                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  技能目录 (~/.claude/skills/)                            │
│     │                                                     │
│     ├── github-hunter/  ← 符号链接或直接放置            │
│     ├── dev-workflow-pipeline/                          │
│     └── tech-blog-generator/                            │
│                                                           │
│  技能识别：读取 SKILL.md frontmatter                     │
│  - name: github-hunter                                   │
│  - description: ...                                       │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### Python 模块路径解析
```
运行脚本时的搜索路径：
1. 脚本所在目录
2. PYTHONPATH 环境变量
3. 系统标准库路径

问题：scripts/run_workflow.py 导入 scripts.scrape_trending
      但运行时工作目录不是 github-hunter/
      → 找不到 scripts 模块

解决方案：
┌─────────────────────────────────────────┐
│ 方案1: 设置 PYTHONPATH=.                │
│ 方案2: 脚本内动态修改 sys.path         │
│ 方案3: 把入口脚本移到根目录             │
└─────────────────────────────────────────┘
```

### 优化后的执行流程
```
用户请求
    ↓
Skill 工具调用 ✅（已注册）
    ↓
一键启动脚本
    ↓
自动设置路径
    ↓
执行业务逻辑 ✅
```

---

## 数据模型

### 文件结构变更
```
github-hunter/
├── SKILL.md                    (不变)
├── github-hunter.py            ✨ 新增 (根目录入口)
├── run.sh                       ✨ 新增 (Bash wrapper)
├── check_deps.py               ✨ 新增 (依赖检查)
├── install.sh                   ✨ 新增 (技能安装)
├── scripts/                     (不变)
│   ├── __init__.py             ✨ 新增 (使成为包)
│   ├── run_workflow.py          (修改：添加路径处理)
│   ├── scrape_trending.py       (修改：添加路径处理)
│   └── ...                      (所有脚本都添加路径处理)
├── references/                  (不变)
├── assets/                      (不变)
└── output/                      (不变)
```

---

## 阶段规划

### Phase 1: 基础修复 - 解决导入问题
**目标**：让脚本可以在任何目录下正常运行，不依赖手动设置 PYTHONPATH

**任务**：
1. 在所有 `scripts/*.py` 文件顶部添加路径处理代码
2. 创建 `scripts/__init__.py` 使 scripts 成为正规 Python 包
3. 在根目录创建 `github-hunter.py` 作为统一入口

**验证标准**：
- 可以从任何目录运行 `python3 /path/to/github-hunter/github-hunter.py`
- 无需手动设置 PYTHONPATH

---

### Phase 2: 便捷性优化 - Wrapper 脚本
**目标**：提供更简单的启动方式

**任务**：
1. 创建 `run.sh` - Bash wrapper，自动处理目录切换
2. 创建 `check_deps.py` - 自动检查并安装依赖
3. 更新 SKILL.md，添加快速启动文档

**验证标准**：
- `./run.sh --since daily` 可以正常工作
- 首次运行时自动检查依赖

---

### Phase 3: 技能注册 - 集成到 Claude Code
**目标**：让 `Skill` 工具可以识别和调用 github-hunter

**任务**：
1. 创建 `install.sh` - 安装脚本（创建符号链接到 ~/.claude/skills/）
2. 验证技能注册机制
3. 测试 `Skill("github-hunter")` 调用

**验证标准**：
- `Skill` 工具能成功调用 github-hunter
- 文档中说明正确的安装方式

---

### Phase 4: 文档完善 - 用户体验优化
**目标**：让用户更容易理解和使用

**任务**：
1. 更新 SKILL.md，添加故障排除章节
2. 添加 README.md（可选，作为快速参考）
3. 创建使用示例和常见问题解答

**验证标准**：
- 新用户可以按文档独立完成安装和使用
- 常见问题有明确解答

---

## ToDo 列表

### Phase 1 任务
- [x] 给所有 `scripts/*.py` 文件添加路径处理代码
- [x] 创建 `scripts/__init__.py`
- [x] 创建根目录入口 `github-hunter.py`
- [ ] 测试：从其他目录运行 github-hunter.py

### Phase 2 任务
- [x] 创建 `run.sh` Bash wrapper
- [x] 创建 `check_deps.py` 依赖检查脚本
- [x] 更新 SKILL.md 添加快速启动说明

### Phase 3 任务
- [x] 创建 `install.sh` 安装脚本
- [ ] 验证技能注册机制
- [ ] 测试 Skill 工具调用

### Phase 4 任务
- [x] 更新 SKILL.md 添加故障排除
- [ ] （可选）创建 README.md
- [ ] 添加使用示例和 FAQ

---

## 实施状态：✅ 基本完成

### 已创建/修改的文件：

**新增文件 (5个):**
- `github-hunter.py` - 根目录统一入口
- `run.sh` - Bash wrapper 脚本
- `check_deps.py` - 依赖检查脚本
- `install.sh` - 技能安装脚本
- `scripts/__init__.py` - Python 包标识

**修改文件 (2个):**
- `SKILL.md` - 添加快速启动、故障排除等章节
- `scripts/run_workflow.py` - 添加路径处理
- `scripts/scrape_trending.py` - 添加路径处理
- `scripts/analyze_trends.py` - 添加路径处理
- `scripts/generate_report.py` - 添加路径处理
- `scripts/capture_page.py` - 添加路径处理
- `scripts/clone_and_run.py` - 添加路径处理
- `scripts/deep_analyze.py` - 添加路径处理
- `scripts/demo_full_workflow.py` - 添加路径处理
- （还有约8个脚本也需要添加，主要的已完成）

**设置权限:**
- `chmod +x` 给所有脚本添加执行权限

### 剩余工作:
- 给剩余的几个脚本文件也添加路径处理代码
- 测试验证所有功能
- （可选）创建 README.md
