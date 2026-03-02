#!/usr/bin/env bash
set -euo pipefail

if [ "${1:-}" = "" ]; then
  echo "Usage: $0 <SKILL_SOURCE> [--platforms=all] [--dry-run|--apply] [--yes] [--backup] [--delete]"
  exit 1
fi

SKILL_SOURCE="$1"
shift || true

PLATFORMS="all"
DRY_RUN=1
ASSUME_YES=0
ENABLE_BACKUP=0
ENABLE_DELETE=0

for arg in "$@"; do
  case "$arg" in
    --platforms=*) PLATFORMS="${arg#*=}" ;;
    --dry-run) DRY_RUN=1 ;;
    --apply) DRY_RUN=0 ;;
    --yes) ASSUME_YES=1 ;;
    --backup) ENABLE_BACKUP=1 ;;
    --delete) ENABLE_DELETE=1 ;;
    *)
      echo "Unknown option: $arg"
      exit 1
      ;;
  esac
done

if [ ! -d "$SKILL_SOURCE" ] || [ ! -f "$SKILL_SOURCE/SKILL.md" ]; then
  echo "Error: SKILL_SOURCE 不存在或缺少 SKILL.md -> $SKILL_SOURCE"
  exit 1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "Error: rsync 未安装。macOS 可执行: brew install rsync"
  exit 1
fi

SKILL_NAME="$(basename "$SKILL_SOURCE")"
FRONT_NAME="$(awk '/^---/{p=!p;next} p && /^name:/{sub(/^name:[[:space:]]*/, ""); print; exit}' "$SKILL_SOURCE/SKILL.md" 2>/dev/null || true)"
if [ -n "$FRONT_NAME" ]; then
  SKILL_NAME="$FRONT_NAME"
fi

OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
HOME_DIR="${HOME}"
USER_NAME="$(id -un)"

# 候选路径（按平台返回两类：配置文件候选、skills 根目录候选）
platform_config_candidates() {
  case "$1" in
    cursor)
      cat <<EOF
$HOME_DIR/.cursor/settings.json
$HOME_DIR/.cursor/User/settings.json
$HOME_DIR/.config/Cursor/User/settings.json
$HOME_DIR/Library/Application Support/Cursor/User/settings.json
/mnt/c/Users/$USER_NAME/AppData/Roaming/Cursor/User/settings.json
EOF
      ;;
    claude)
      cat <<EOF
$HOME_DIR/.claude/settings.json
$HOME_DIR/.claude/config.json
$HOME_DIR/.config/claude/config.json
$HOME_DIR/Library/Application Support/Claude/config.json
/mnt/c/Users/$USER_NAME/AppData/Roaming/Claude/config.json
EOF
      ;;
    trae)
      cat <<EOF
$HOME_DIR/.trae/config.json
$HOME_DIR/.trae/settings.json
$HOME_DIR/.config/trae/config.json
$HOME_DIR/Library/Application Support/Trae/config.json
/mnt/c/Users/$USER_NAME/AppData/Roaming/Trae/config.json
EOF
      ;;
    openclaw)
      cat <<EOF
$HOME_DIR/.openclaw/config.toml
$HOME_DIR/.openclaw/config.json
$HOME_DIR/.config/openclaw/config.toml
$HOME_DIR/.config/openclaw/config.json
$HOME_DIR/Library/Application Support/OpenClaw/config.toml
/mnt/c/Users/$USER_NAME/AppData/Roaming/OpenClaw/config.toml
EOF
      ;;
    codex)
      cat <<EOF
$HOME_DIR/.codex/config.toml
$HOME_DIR/.codex/config.json
$HOME_DIR/.config/codex/config.toml
$HOME_DIR/Library/Application Support/Codex/config.toml
/mnt/c/Users/$USER_NAME/AppData/Roaming/Codex/config.toml
EOF
      ;;
    agents)
      cat <<EOF
$HOME_DIR/.agents/config.json
$HOME_DIR/.agents/settings.json
$HOME_DIR/.config/agents/config.json
EOF
      ;;
  esac
}

platform_skills_candidates() {
  case "$1" in
    cursor) cat <<EOF
$HOME_DIR/.cursor/skills
EOF
      ;;
    claude) cat <<EOF
$HOME_DIR/.claude/skills
EOF
      ;;
    trae) cat <<EOF
$HOME_DIR/.trae/skills
$HOME_DIR/.config/trae/skills
EOF
      ;;
    openclaw) cat <<EOF
$HOME_DIR/.openclaw/skills
$HOME_DIR/.config/openclaw/skills
EOF
      ;;
    codex) cat <<EOF
$HOME_DIR/.codex/skills
EOF
      ;;
    agents) cat <<EOF
$HOME_DIR/.agents/skills
EOF
      ;;
  esac
}

# 从配置文件中提取 skills 路径（简化匹配）
extract_skills_path_from_config() {
  cfg="$1"
  if [ ! -f "$cfg" ]; then
    return 0
  fi
  sed -nE 's/.*"skills"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/p' "$cfg" | head -n 1
  sed -nE "s/.*skills[[:space:]]*=[[:space:]]*\"([^\"]+)\".*/\\1/p" "$cfg" | head -n 1
}

# 解析平台列表
if [ "$PLATFORMS" = "all" ] || [ -z "$PLATFORMS" ]; then
  SELECTED="cursor,claude,trae,openclaw,codex,agents"
else
  SELECTED="$PLATFORMS"
fi

RSYNC_EXCLUDES=(
  "--exclude=.DS_Store"
  "--exclude=__pycache__"
  "--exclude=.git"
)

if [ "$ENABLE_DELETE" -eq 1 ]; then
  RSYNC_DELETE="--delete"
else
  RSYNC_DELETE=""
fi

echo "=== install-skill-to-all v2 ==="
echo "OS: $OS"
echo "Skill source: $SKILL_SOURCE"
echo "Skill name: $SKILL_NAME"
echo "Selected platforms: $SELECTED"
echo "Mode: $( [ "$DRY_RUN" -eq 1 ] && echo "dry-run" || echo "apply" )"
echo ""

IFS=',' read -r -a PLAT_ARR <<< "$SELECTED"

for plat in "${PLAT_ARR[@]}"; do
  plat="$(echo "$plat" | xargs)"
  [ -z "$plat" ] && continue

  case "$plat" in
    cursor|claude|trae|openclaw|codex|agents) ;;
    *)
      echo "⚠ 跳过未知平台: $plat"
      echo ""
      continue
      ;;
  esac

  found_cfg=""
  while IFS= read -r c; do
    [ -z "$c" ] && continue
    if [ -f "$c" ]; then
      found_cfg="$c"
      break
    fi
  done <<EOF
$(platform_config_candidates "$plat")
EOF

  skills_root=""
  if [ -n "$found_cfg" ]; then
    while IFS= read -r p; do
      [ -n "$p" ] && skills_root="$p"
    done <<EOF
$(extract_skills_path_from_config "$found_cfg")
EOF
  fi

  if [ -z "$skills_root" ]; then
    while IFS= read -r d; do
      [ -z "$d" ] && continue
      # 目录已存在优先；否则记第一个候选作为默认路径
      if [ -d "$d" ]; then
        skills_root="$d"
        break
      fi
      if [ -z "$skills_root" ]; then
        skills_root="$d"
      fi
    done <<EOF
$(platform_skills_candidates "$plat")
EOF
  fi

  if [ -z "$skills_root" ]; then
    echo "❌ [$plat] 未找到可用 skills 根路径，跳过"
    echo ""
    continue
  fi

  target="$skills_root/$SKILL_NAME"

  echo "[$plat]"
  echo "  config: ${found_cfg:-<not found>}"
  echo "  skills: $skills_root"
  echo "  target: $target"

  mode="新装"
  if [ -d "$target" ]; then
    mode="更新"
  fi

  # 先展示预览
  echo "  preview:"
  rsync -avn $RSYNC_DELETE "${RSYNC_EXCLUDES[@]}" "$SKILL_SOURCE/" "$target/" || true

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "  ✅ dry-run 完成"
    echo ""
    continue
  fi

  if [ "$ASSUME_YES" -ne 1 ]; then
    printf "  Confirm apply to [%s] (%s)? [y/N] " "$plat" "$mode"
    read -r ans
    case "$ans" in
      y|Y|yes|YES) ;;
      *)
        echo "  ⏭ 已跳过"
        echo ""
        continue
        ;;
    esac
  fi

  if [ "$ENABLE_BACKUP" -eq 1 ] && [ -d "$target" ]; then
    ts="$(date +%Y%m%d%H%M%S)"
    cp -R "$target" "${target}.bak.${ts}"
    echo "  backup: ${target}.bak.${ts}"
  fi

  mkdir -p "$target"
  rsync -av $RSYNC_DELETE "${RSYNC_EXCLUDES[@]}" "$SKILL_SOURCE/" "$target/"

  if [ -f "$target/SKILL.md" ]; then
    echo "  ✅ apply 成功 ($mode)"
  else
    echo "  ❌ apply 后验证失败：$target/SKILL.md 不存在"
  fi
  echo ""
done
