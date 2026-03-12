#!/usr/bin/env python3
"""
完整工作流演示（使用模拟Trending数据）

演示完整的流程：爬取→分析→生成报告
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 自动设置路径：将技能根目录添加到 sys.path
skill_root = Path(__file__).parent.parent
if str(skill_root) not in sys.path:
    sys.path.insert(0, str(skill_root))

from scripts.analyze_trends import analyze_trends, print_analysis
from scripts.generate_report import generate_daily_report, generate_detailed_blog


# 模拟的真实Trending数据（基于你看到的实际数据）
MOCK_TRENDING = [
    {
        "rank": 1,
        "name": "pbakaus/impeccable",
        "url": "https://github.com/pbakaus/impeccable",
        "description": "The design language that makes your AI harness better at design.",
        "language": "JavaScript",
        "stars": 3409,
        "forks": 124,
        "stars_today": 932,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 2,
        "name": "msitarzewski/agency-agents",
        "url": "https://github.com/msitarzewski/agency-agents",
        "description": "A complete AI agency at your fingertips - From frontend wizards to Reddit community ninjas",
        "language": "Shell",
        "stars": 21860,
        "forks": 3425,
        "stars_today": 6235,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 3,
        "name": "666ghj/MiroFish",
        "url": "https://github.com/666ghj/MiroFish",
        "description": "A Simple and Universal Swarm Intelligence Engine, Predicting Anything. 简洁通用的群体智能引擎，预测万物",
        "language": "Python",
        "stars": 13079,
        "forks": 1358,
        "stars_today": 4469,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 4,
        "name": "NousResearch/hermes-agent",
        "url": "https://github.com/NousResearch/hermes-agent",
        "description": "The agent that grows with you",
        "language": "Python",
        "stars": 3324,
        "forks": 436,
        "stars_today": 776,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 5,
        "name": "promptfoo/promptfoo",
        "url": "https://github.com/promptfoo/promptfoo",
        "description": "Test your prompts, agents, and RAGs. AI Red teaming, pentesting, and vulnerability scanning for LLMs.",
        "language": "TypeScript",
        "stars": 11577,
        "forks": 1061,
        "stars_today": 632,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 6,
        "name": "GoogleCloudPlatform/generative-ai",
        "url": "https://github.com/GoogleCloudPlatform/generative-ai",
        "description": "Sample code and notebooks for Generative AI on Google Cloud, with Gemini on Vertex AI",
        "language": "Jupyter Notebook",
        "stars": 15530,
        "forks": 3982,
        "stars_today": 534,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 7,
        "name": "virattt/ai-hedge-fund",
        "url": "https://github.com/virattt/ai-hedge-fund",
        "description": "An AI Hedge Fund Team",
        "language": "Python",
        "stars": 47279,
        "forks": 8234,
        "stars_today": 316,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 8,
        "name": "karpathy/nanochat",
        "url": "https://github.com/karpathy/nanochat",
        "description": "The best ChatGPT that $100 can buy.",
        "language": "Python",
        "stars": 45905,
        "forks": 6062,
        "stars_today": 709,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 9,
        "name": "obra/superpowers",
        "url": "https://github.com/obra/superpowers",
        "description": "An agentic skills framework & software development methodology that works.",
        "language": "Shell",
        "stars": 75931,
        "forks": 5875,
        "stars_today": 1387,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 10,
        "name": "alibaba/page-agent",
        "url": "https://github.com/alibaba/page-agent",
        "description": "JavaScript in-page GUI agent. Control web interfaces with natural language.",
        "language": "TypeScript",
        "stars": 3052,
        "forks": 239,
        "stars_today": 895,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 11,
        "name": "sepinf-inc/IPED",
        "url": "https://github.com/sepinf-inc/IPED",
        "description": "IPED Digital Forensic Tool. Open source software for digital evidence analysis.",
        "language": "Java",
        "stars": 2005,
        "forks": 379,
        "stars_today": 237,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 12,
        "name": "openclaw/openclaw",
        "url": "https://github.com/openclaw/openclaw",
        "description": "Your own personal AI assistant. Any OS. Any Platform. The lobster way. 🦞",
        "language": "TypeScript",
        "stars": 296044,
        "forks": 55946,
        "stars_today": 9074,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 13,
        "name": "bytedance/deer-flow",
        "url": "https://github.com/bytedance/deer-flow",
        "description": "An open-source SuperAgent harness that researches, codes, and creates.",
        "language": "Python",
        "stars": 27986,
        "forks": 3340,
        "stars_today": 0,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 14,
        "name": "modelscope/sirchmunk",
        "url": "https://github.com/modelscope/sirchmunk",
        "description": "Raw data to self-evolving intelligence",
        "language": "Python",
        "stars": 1200,
        "forks": 150,
        "stars_today": 250,
        "scraped_at": datetime.now().isoformat()
    },
    {
        "rank": 15,
        "name": "volcengine/OpenViking",
        "url": "https://github.com/volcengine/OpenViking",
        "description": "AI Agent context database",
        "language": "Go",
        "stars": 3500,
        "forks": 420,
        "stars_today": 380,
        "scraped_at": datetime.now().isoformat()
    }
]


def demo_full_workflow():
    """演示完整工作流"""
    print(f"\n{'='*80}")
    print(f"🚀 GitHub Trending 完整工作流演示")
    print(f"{'='*80}\n")
    
    # 创建输出目录
    output_dir = Path("./demo-output")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 步骤1: 保存Trending数据
    print(f"📥 步骤1/4: 保存Trending数据...")
    trending_file = output_dir / "trending.json"
    with open(trending_file, 'w', encoding='utf-8') as f:
        json.dump(MOCK_TRENDING, f, ensure_ascii=False, indent=2)
    print(f"✅ 已保存: {trending_file}\n")
    
    # 步骤2: 分析趋势
    print(f"📊 步骤2/4: 分析趋势...")
    analysis = analyze_trends(MOCK_TRENDING)
    print_analysis(analysis)
    
    trends_file = output_dir / "trends.json"
    with open(trends_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"💾 已保存: {trends_file}\n")
    
    # 步骤3: 生成日报
    print(f"📝 步骤3/4: 生成日报...")
    daily_report_file = output_dir / "daily_report.md"
    generate_daily_report(MOCK_TRENDING, analysis, str(daily_report_file))
    
    # 步骤4: 生成详细博客
    print(f"\n📝 步骤4/4: 生成详细博客...")
    detailed_blog_file = output_dir / "detailed_blog.md"
    generate_detailed_blog(MOCK_TRENDING, analysis, str(output_dir))
    
    # 输出总结
    print(f"\n{'='*80}")
    print(f"✅ 演示完成")
    print(f"{'='*80}\n")
    
    print(f"📁 生成的文件：")
    print(f"   - {trending_file}")
    print(f"   - {trends_file}")
    print(f"   - {daily_report_file}")
    print(f"   - {detailed_blog_file}")
    
    print(f"\n💡 查看日报：")
    print(f"   cat {daily_report_file}")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    demo_full_workflow()
