#!/usr/bin/env python3
"""
截取GitHub仓库统计图表

依赖: playwright
安装: pip install playwright && playwright install chromium

功能：截取仓库的活跃度图表、Stars曲线、贡献者分布等统计信息
"""

import os
import argparse
import sys
import asyncio
from playwright.async_api import async_playwright


async def capture_github_stats(repo_url: str, output_dir: str):
    """
    截取GitHub仓库的统计图表
    
    Args:
        repo_url: 仓库URL（如 https://github.com/owner/repo）
        output_dir: 输出目录
    
    Returns:
        dict: 包含所有截图路径的字典
    """
    screenshots = {}
    repo_name = repo_url.rstrip('/').split('/')[-1]
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            
            # 1. 截取活跃度图表（Stargazers页面）
            print(f"\n[1/4] 截取Stars增长曲线...")
            stars_url = f"{repo_url}/stargazers"
            await page.goto(stars_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            # 滚动到图表位置
            await page.evaluate("window.scrollTo(0, 300)")
            await asyncio.sleep(1)
            
            stars_chart_path = os.path.join(output_dir, f"{repo_name}-stars-chart.png")
            # 截取图表区域（裁剪掉导航栏）
            chart_element = await page.query_selector(".activity-overview-graph")
            if chart_element:
                await chart_element.screenshot(path=stars_chart_path)
                screenshots["stars_chart"] = stars_chart_path
            else:
                # 备选：截取整个Stargazers页面
                await page.screenshot(path=stars_chart_path, full_page=False)
                screenshots["stars_chart"] = stars_chart_path
            
            # 2. 截取活跃度图表（Activity页面）
            print(f"[2/4] 截取提交活跃度图表...")
            activity_url = f"{repo_url}/pulse"
            await page.goto(activity_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            activity_chart_path = os.path.join(output_dir, f"{repo_name}-activity-chart.png")
            await page.screenshot(path=activity_chart_path, full_page=False)
            screenshots["activity_chart"] = activity_chart_path
            
            # 3. 截取贡献者统计（Graphs/Contributors页面）
            print(f"[3/4] 截取贡献者统计...")
            contributors_url = f"{repo_url}/graphs/contributors"
            await page.goto(contributors_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            contributors_path = os.path.join(output_dir, f"{repo_name}-contributors.png")
            await page.screenshot(path=contributors_path, full_page=False)
            screenshots["contributors"] = contributors_path
            
            # 4. 截取提交频率（Graphs/Commit-activity页面）
            print(f"[4/4] 截取提交频率图表...")
            commits_url = f"{repo_url}/graphs/commit-activity"
            await page.goto(commits_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            commits_chart_path = os.path.join(output_dir, f"{repo_name}-commits-chart.png")
            await page.screenshot(path=commits_chart_path, full_page=False)
            screenshots["commits_chart"] = commits_chart_path
            
            # 5. 额外：截取代码频率（Graphs/Code-frequency页面）
            print(f"[5/5] 截取代码变更频率...")
            code_freq_url = f"{repo_url}/graphs/code-frequency"
            await page.goto(code_freq_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            code_freq_path = os.path.join(output_dir, f"{repo_name}-code-frequency.png")
            await page.screenshot(path=code_freq_path, full_page=False)
            screenshots["code_frequency"] = code_freq_path
            
            await browser.close()
            
            return screenshots
            
    except Exception as e:
        print(f"❌ 截图失败: {str(e)}", file=sys.stderr)
        return screenshots


async def capture_repo_overview(repo_url: str, output_dir: str):
    """
    截取仓库概览（包含README和统计信息）
    
    Args:
        repo_url: 仓库URL
        output_dir: 输出目录
    
    Returns:
        str: 概览截图路径
    """
    repo_name = repo_url.rstrip('/').split('/')[-1]
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 2000},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = await context.new_page()
            print(f"\n截取仓库概览...")
            await page.goto(repo_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(3)
            
            overview_path = os.path.join(output_dir, f"{repo_name}-overview.png")
            await page.screenshot(path=overview_path, full_page=True)
            
            await browser.close()
            
            return overview_path
            
    except Exception as e:
        print(f"❌ 概览截图失败: {str(e)}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="截取GitHub仓库统计图表")
    parser.add_argument("--repo", "-r", required=True, help="仓库URL（如 https://github.com/owner/repo）")
    parser.add_argument("--output", "-o", default="./github_stats", help="输出目录（默认：./github_stats）")
    parser.add_argument("--overview-only", action="store_true", help="只截取概览")
    
    args = parser.parse_args()
    
    async def run():
        if args.overview_only:
            overview = await capture_repo_overview(args.repo, args.output)
            if overview:
                print(f"\n✅ 概览已保存: {overview}")
        else:
            screenshots = await capture_github_stats(args.repo, args.output)
            print(f"\n✅ 成功截取 {len(screenshots)} 张统计图表")
            for name, path in screenshots.items():
                print(f"   - {name}: {path}")
    
    asyncio.run(run())


if __name__ == "__main__":
    main()
