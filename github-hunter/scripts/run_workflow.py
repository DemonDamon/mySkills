#!/usr/bin/env python3
"""
GitHub Trending完整工作流

一键生成：
1. 爬取GitHub Trending
2. 分析趋势
3. 生成日报/博客
4. 截取页面（可选）
5. 运行代码（可选）
"""

import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime

# 导入各个模块
from scripts.scrape_trending import scrape_github_trending
from scripts.analyze_trends import analyze_trends, print_analysis
from scripts.generate_report import generate_daily_report, generate_detailed_blog


async def full_workflow(
    language: str = "",
    since: str = "daily",
    limit: int = 15,
    output_dir: str = "./output",
    capture_screenshots: bool = False,
    run_code: bool = False
):
    """
    完整工作流程
    
    Args:
        language: 编程语言过滤
        since: 时间范围
        limit: 数量限制
        output_dir: 输出目录
        capture_screenshots: 是否截取页面
        run_code: 是否运行代码
    """
    print(f"\n{'='*80}")
    print(f"🚀 GitHub Trending 完整工作流")
    print(f"{'='*80}\n")
    
    start_time = datetime.now()
    
    # 步骤1: 爬取GitHub Trending
    print(f"📥 步骤1/5: 爬取GitHub Trending...\n")
    repos = await scrape_github_trending(
        language=language,
        since=since,
        limit=limit
    )
    
    if not repos:
        print("❌ 爬取失败，终止流程")
        return
    
    # 保存Trending数据
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    trending_file = output_path / "trending.json"
    with open(trending_file, 'w', encoding='utf-8') as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Trending数据已保存: {trending_file}\n")
    
    # 步骤2: 分析趋势
    print(f"📊 步骤2/5: 分析趋势...\n")
    analysis = analyze_trends(repos)
    print_analysis(analysis)
    
    # 保存趋势分析
    trends_file = output_path / "trends.json"
    with open(trends_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"💾 趋势分析已保存: {trends_file}\n")
    
    # 步骤3: 生成日报
    print(f"📝 步骤3/5: 生成日报...")
    daily_report_file = output_path / "daily_report.md"
    generate_daily_report(repos, analysis, str(daily_report_file))
    
    # 步骤4: 截取页面（可选）
    if capture_screenshots:
        print(f"\n📸 步骤4/5: 截取GitHub页面...")
        from scripts.capture_page import capture_screenshot
        
        for idx, repo in enumerate(repos[:5], 1):  # 只截取前5个
            print(f"\n[{idx}/5] 截取 {repo['name']}...")
            
            repo_dir = output_path / repo["name"].replace("/", "-")
            repo_dir.mkdir(parents=True, exist_ok=True)
            
            screenshot_file = repo_dir / "github-page.png"
            
            try:
                await capture_screenshot(
                    url=repo["url"],
                    output_path=str(screenshot_file),
                    wait_time=2000
                )
            except Exception as e:
                print(f"❌ 截图失败: {str(e)}")
        
        # 生成详细博客（含截图）
        print(f"\n📝 步骤5/5: 生成详细博客...")
        detailed_blog_file = output_path / "detailed_blog.md"
        generate_detailed_blog(repos, analysis, output_dir)
    
    else:
        print(f"\n⏭️  步骤4/5: 跳过截图（使用 --capture 参数启用）")
        print(f"⏭️  步骤5/5: 跳过详细博客（需要截图支持）")
    
    # 统计耗时
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # 输出总结
    print(f"\n{'='*80}")
    print(f"✅ 工作流完成")
    print(f"{'='*80}\n")
    
    print(f"📊 统计信息：")
    print(f"   - 项目数量: {len(repos)}")
    print(f"   - 总耗时: {duration:.1f}秒")
    print(f"   - 输出目录: {output_dir}/")
    
    print(f"\n📁 生成的文件：")
    print(f"   - trending.json (原始数据)")
    print(f"   - trends.json (趋势分析)")
    print(f"   - daily_report.md (日报)")
    
    if capture_screenshots:
        print(f"   - detailed_blog.md (详细博客)")
        print(f"   - */github-page.png (页面截图)")
    
    print(f"\n💡 使用建议：")
    print(f"   - 查看日报: cat {output_dir}/daily_report.md")
    print(f"   - 发布博客: 复制 daily_report.md 到博客平台")
    print(f"   - 数据分析: 查看 {output_dir}/trending.json")
    
    print(f"\n{'='*80}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="GitHub Trending完整工作流")
    
    # 基础参数
    parser.add_argument("--language", type=str, default="", help="编程语言过滤（python、javascript等）")
    parser.add_argument("--since", type=str, default="daily", choices=["daily", "weekly", "monthly"], help="时间范围")
    parser.add_argument("--limit", type=int, default=15, help="项目数量限制")
    parser.add_argument("--output-dir", type=str, default="./output", help="输出目录")
    
    # 高级功能
    parser.add_argument("--capture", action="store_true", help="截取GitHub页面截图")
    parser.add_argument("--run-code", action="store_true", help="运行代码示例（暂未实现）")
    
    args = parser.parse_args()
    
    # 运行工作流
    asyncio.run(full_workflow(
        language=args.language,
        since=args.since,
        limit=args.limit,
        output_dir=args.output_dir,
        capture_screenshots=args.capture,
        run_code=args.run_code
    ))


if __name__ == "__main__":
    main()
