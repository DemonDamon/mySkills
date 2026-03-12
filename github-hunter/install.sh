#!/bin/bash
# github-hunter 技能安装脚本
#
# 将 github-hunter 安装到 Claude Code 的技能目录
#
# 用法:
#   ./install.sh
#   ./install.sh --dry-run
#   ./install.sh --help

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="github-hunter"
SKILL_DIR="$SCRIPT_DIR"

# Claude Code 技能目录
CLAUDE_SKILLS_DIR="$HOME/.claude/skills"

DRY_RUN=0
VERBOSE=0

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat <<EOF
github-hunter 技能安装脚本

将 github-hunter 安装到 Claude Code 的技能目录

用法:
    $0 [选项]

选项:
    --dry-run    预览操作，不实际修改文件
    -v, --verbose  显示详细输出
    -h, --help     显示此帮助信息

示例:
    $0                    # 安装技能
    $0 --dry-run         # 预览安装
    $0 --help            # 显示帮助
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --dry-run)
                DRY_RUN=1
                shift
                ;;
            -v|--verbose)
                VERBOSE=1
                shift
                ;;
            -h|--help)
                show_help
                exit 0
                ;;
            *)
                log_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

run_cmd() {
    if [[ $DRY_RUN -eq 1 ]]; then
        log_info "[DRY-RUN] $*"
    else
        if [[ $VERBOSE -eq 1 ]]; then
            log_info "执行: $*"
        fi
        "$@"
    fi
}

check_skill_file() {
    if [[ ! -f "$SKILL_DIR/SKILL.md" ]]; then
        log_error "找不到 SKILL.md 文件"
        log_error "请确认在正确的目录中运行此脚本"
        exit 1
    fi
}

create_skills_dir() {
    if [[ ! -d "$CLAUDE_SKILLS_DIR" ]]; then
        log_info "创建 Claude Code 技能目录: $CLAUDE_SKILLS_DIR"
        run_cmd mkdir -p "$CLAUDE_SKILLS_DIR"
    fi
}

install_skill() {
    local target_path="$CLAUDE_SKILLS_DIR/$SKILL_NAME"

    log_info "技能源目录: $SKILL_DIR"
    log_info "安装目标: $target_path"

    # 检查是否已存在
    if [[ -e "$target_path" ]]; then
        if [[ -L "$target_path" ]]; then
            local current_link=$(readlink "$target_path")
            if [[ "$current_link" == "$SKILL_DIR" ]]; then
                log_success "技能已正确安装"
                return 0
            else
                log_warning "技能已存在但指向不同位置"
                log_info "   当前: $current_link"
                log_info "   新位置: $SKILL_DIR"
            fi
        else
            log_warning "目标位置已存在且不是符号链接"
        fi

        log_warning "将替换现有安装"
        if [[ $DRY_RUN -eq 0 ]]; then
            read -p "继续? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log_info "已取消安装"
                exit 0
            fi
        fi
        run_cmd rm -rf "$target_path"
    fi

    # 创建符号链接
    log_info "创建符号链接..."
    run_cmd ln -sf "$SKILL_DIR" "$target_path"

    log_success "技能安装成功!"
}

print_summary() {
    echo
    echo "=" * 80
    log_success "安装完成!"
    echo "=" * 80
    echo
    echo "📂 安装位置: $CLAUDE_SKILLS_DIR/$SKILL_NAME"
    echo
    echo "💡 下一步:"
    echo "   1. 重启 Claude Code"
    echo "   2. 使用技能:"
    echo "      Skill(\"github-hunter\")"
    echo
    echo "🧪 测试（无需重启）:"
    echo "   cd $SKILL_DIR"
    echo "   python check_deps.py"
    echo "   ./run.sh --since daily --limit 5"
    echo
}

main() {
    parse_args "$@"

    echo "=" * 80
    echo "🚀 github-hunter 技能安装"
    echo "=" * 80
    echo

    if [[ $DRY_RUN -eq 1 ]]; then
        log_warning "预览模式 - 不会实际修改文件"
        echo
    fi

    check_skill_file
    create_skills_dir
    install_skill
    print_summary
}

main "$@"
