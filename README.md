# mySkills

Agent skills collection for Cursor / Claude Code.

## Skills

### [tech-blog-generator](tech-blog-generator/)

基于种子信息（关键词、URL、GitHub 仓库等）进行网络检索与资料爬取，生成图文并茂的中文技术博客。包含信息搜集、图片智能处理（自动过滤+闭环生图）、三轮写作（大纲→初稿→自评修正）。

**适用场景**：研究技术主题并生成博客、撰写技术内容、深度调研某技术。

## install-skill-to-all 脚本

将指定 skill 目录安装或同步到多个 AI 工具目录。支持自动识别系统、探测配置与技能路径。

### 前置条件

- 系统已安装 `rsync`（macOS: `brew install rsync`）
- skill 源目录必须包含 `SKILL.md`

### 工作流

1. 默认先 dry-run（推荐）

```bash
./install-skill-to-all.sh <SKILL_SOURCE> --dry-run
```

2. 确认后执行

```bash
./install-skill-to-all.sh <SKILL_SOURCE> --apply [--yes] [--backup]
```

3. 可选：严格镜像（慎用）

```bash
./install-skill-to-all.sh <SKILL_SOURCE> --apply --yes --backup --delete
```

### 参数速查

| 参数 | 说明 |
|------|------|
| `SKILL_SOURCE` | 必选，skill 源目录（含 SKILL.md） |
| `--platforms=<list>` | 平台列表，逗号分隔，默认 `all` |
| `--dry-run` | 仅预览（默认） |
| `--apply` | 执行写入 |
| `--yes` | 跳过确认 |
| `--backup` | 更新前备份 |
| `--delete` | rsync --delete（慎用） |

### 支持平台

`cursor`、`claude`、`trae`、`openclaw`、`codex`、`agents`

### 使用示例

```bash
# 预览（推荐）
./install-skill-to-all.sh ./tech-blog-generator --platforms=all --dry-run

# 无交互 + 备份
./install-skill-to-all.sh ./tech-blog-generator --platforms=cursor,claude,trae,openclaw --apply --yes --backup

# 严格镜像（会删除目标多余文件）
./install-skill-to-all.sh ./tech-blog-generator --platforms=all --apply --yes --backup --delete
```
