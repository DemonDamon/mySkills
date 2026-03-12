#!/usr/bin/env python3
"""
github-hunter - GitHub Trending 分析器

一键分析 GitHub Trending 热门项目，生成日报和博客文章。

用法:
    python github-hunter.py --since daily --limit 15
    python github-hunter.py --language python --capture
    python github-hunter.py --help
"""

import sys
from pathlib import Path

# 确保能找到 scripts 模块
skill_root = Path(__file__).parent
if str(skill_root) not in sys.path:
    sys.path.insert(0, str(skill_root))

from scripts.run_workflow import main

if __name__ == "__main__":
    main()
