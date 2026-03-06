# 代码运行模式识别规则

本文档描述了如何智能识别不同编程语言的运行指令，用于 `clone_and_run.py` 脚本。

## 语言检测规则

### Python
**识别特征**：
- 存在 `requirements.txt`
- 存在 `setup.py`
- 存在 `pyproject.toml`

**安装命令**：
- `requirements.txt`: `pip install -r requirements.txt`
- `setup.py`: `pip install -e .`
- `pyproject.toml`: `pip install -e .`

**示例代码位置**：
- `examples/` 目录
- `demo/` 目录
- `tests/` 目录（包含 "example" 或 "demo" 关键词的文件）

**运行命令**：
- `python examples/demo.py`
- `python demo.py`
- `python tests/test_example.py`

### JavaScript/TypeScript
**识别特征**：
- 存在 `package.json`

**安装命令**：
- `npm install`
- `yarn install` (如果存在 `yarn.lock`)
- `pnpm install` (如果存在 `pnpm-lock.yaml`)

**示例代码位置**：
- `examples/` 目录
- `demo/` 目录
- `test/` 目录

**运行命令**：
- 查看 `package.json` 的 `scripts` 字段
- 常见命令：`npm start`, `npm run dev`, `npm run demo`

### Go
**识别特征**：
- 存在 `go.mod`

**安装命令**：
- `go mod download`
- `go mod tidy`

**示例代码位置**：
- `examples/` 目录
- `cmd/` 目录
- `_example/` 目录

**运行命令**：
- `go run examples/main.go`
- `go run cmd/main.go`

### Rust
**识别特征**：
- 存在 `Cargo.toml`

**安装命令**：
- `cargo build`

**示例代码位置**：
- `examples/` 目录

**运行命令**：
- `cargo run --example example_name`

## README 中的运行指令识别

### 常见关键词模式

**安装依赖**：
- "Install": `pip install`, `npm install`, `go get`
- "Setup": `python setup.py install`
- "Requirements": `pip install -r requirements.txt`

**运行示例**：
- "Example": `python examples/`, `npm run example`
- "Demo": `python demo.py`, `npm start`
- "Quick Start": `python main.py`
- "Usage": `python script.py`

### 代码块提取

从 README.md 中提取代码块的规则：

1. 查找 Markdown 代码块（```）
2. 识别代码块语言标记
3. 按优先级提取：
   - 包含 "install" 或 "setup" 的命令块
   - 包含 "example" 或 "demo" 的命令块
   - 包含 "quick start" 或 "usage" 的命令块

## 安全注意事项

### 不运行的情况

- 涉及网络请求的示例（可能访问外部API）
- 涉及文件系统操作的示例（可能修改系统文件）
- 涉及数据库连接的示例（需要配置）
- 需要额外配置的示例（API密钥、环境变量等）

### 超时控制

- 单个示例运行超时：30秒
- 整个仓库处理超时：5分钟

### 错误处理

- 依赖安装失败：跳过代码运行
- 示例运行失败：记录错误，继续尝试其他示例
- 运行超时：终止进程，记录超时错误

## 输出格式

代码运行结果包含：

```json
{
  "success": true,
  "output": "示例输出...",
  "error": "",
  "duration": 1.23,
  "file": "examples/demo.py"
}
```

## 示例场景

### 场景1: Python ML库

```
仓库: transformers/
检测: Python (requirements.txt存在)
安装: pip install -r requirements.txt
示例: examples/pytorch/text-classification/run_glue.py
运行: python examples/pytorch/text-classification/run_glue.py
```

### 场景2: Node.js Web框架

```
仓库: next.js/
检测: JavaScript (package.json存在)
安装: npm install
示例: examples/basic-app/
运行: npm run dev
```

### 场景3: Go工具

```
仓库: hugo/
检测: Go (go.mod存在)
安装: go mod download
示例: examples/basic-usage/
运行: go run examples/basic-usage/main.go
```
