#!/usr/bin/env python3
"""
使用Playwright截取项目页面截图

依赖: playwright
安装: pip install playwright && playwright install chromium
"""

import os
import argparse
import sys
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright


async def capture_screenshot(url: str, output_path: str, 
                             viewport: dict = None, 
                             full_page: bool = False,
                             wait_for_selector: str = None,
                             dark_mode: bool = False):
    """
    使用Playwright截取网页截图
    
    Args:
        url: 目标URL
        output_path: 输出图片路径
        viewport: 视口尺寸，格式 {"width": 1920, "height": 1080}
        full_page: 是否截取整个页面
        wait_for_selector: 等待特定选择器出现后再截图
        dark_mode: 是否使用深色模式
    
    Returns:
        bool: 截图是否成功
    """
    # 默认视口尺寸
    if viewport is None:
        viewport = {"width": 1920, "height": 1080}
    
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    try:
        async with async_playwright() as p:
            # 启动Chromium浏览器
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                ]
            )
            
            # 创建上下文
            context = await browser.new_context(
                viewport=viewport,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            # 创建页面
            page = await context.new_page()
            
            # 启用深色模式（如果需要）
            if dark_mode:
                await page.emulate_media(media='dark')
            
            # 访问目标URL
            print(f"正在访问: {url}")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 等待特定元素（如果指定）
            if wait_for_selector:
                print(f"等待元素: {wait_for_selector}")
                await page.wait_for_selector(wait_for_selector, timeout=10000)
            
            # 额外等待确保页面完全加载
            await asyncio.sleep(2)
            
            # 截图
            print(f"截取截图: {output_path}")
            await page.screenshot(
                path=output_path,
                full_page=full_page,
                type="png"
            )
            
            # 关闭浏览器
            await browser.close()
            
            return True
            
    except Exception as e:
        print(f"❌ 截图失败: {str(e)}", file=sys.stderr)
        return False


async def capture_repo_screenshots(repo_url: str, output_dir: str):
    """
    截取GitHub仓库的多个页面
    
    Args:
        repo_url: 仓库URL（如 https://github.com/owner/repo）
        output_dir: 输出目录
    
    Returns:
        list: 截图文件路径列表
    """
    screenshots = []
    repo_name = repo_url.rstrip('/').split('/')[-1]
    
    # 截图1: 主页
    print(f"\n[1/4] 截取仓库主页")
    main_page_path = os.path.join(output_dir, f"{repo_name}-main.png")
    success = await capture_screenshot(
        url=repo_url,
        output_path=main_page_path,
        viewport={"width": 1920, "height": 1080},
        full_page=True,
        wait_for_selector="article.markdown-body"  # 等待README加载
    )
    if success:
        screenshots.append(main_page_path)
    
    # 截图2: 代码页面（截取前500行）
    print(f"\n[2/4] 截取代码页面")
    code_page_path = os.path.join(output_dir, f"{repo_name}-code.png")
    success = await capture_screenshot(
        url=f"{repo_url}/blob/main/README.md",
        output_path=code_page_path,
        viewport={"width": 1920, "height": 1080},
        full_page=False
    )
    if success:
        screenshots.append(code_page_path)
    
    # 截图3: Issues页面（查看社区活跃度）
    print(f"\n[3/4] 截取Issues页面")
    issues_page_path = os.path.join(output_dir, f"{repo_name}-issues.png")
    success = await capture_screenshot(
        url=f"{repo_url}/issues",
        output_path=issues_page_path,
        viewport={"width": 1920, "height": 1080},
        full_page=False
    )
    if success:
        screenshots.append(issues_page_path)
    
    # 截图4: 深色模式主页（用于对比）
    print(f"\n[4/4] 截取深色模式主页")
    dark_page_path = os.path.join(output_dir, f"{repo_name}-dark.png")
    success = await capture_screenshot(
        url=repo_url,
        output_path=dark_page_path,
        viewport={"width": 1920, "height": 1080},
        full_page=True,
        dark_mode=True
    )
    if success:
        screenshots.append(dark_page_path)
    
    return screenshots


def main():
    parser = argparse.ArgumentParser(description="使用Playwright截取网页截图")
    parser.add_argument("--url", "-u", required=True, help="目标URL")
    parser.add_argument("--output", "-o", required=True, help="输出图片路径")
    parser.add_argument("--viewport", help="视口尺寸，格式: 1920x1080")
    parser.add_argument("--full-page", action="store_true", help="截取整个页面")
    parser.add_argument("--wait-for", help="等待特定选择器出现")
    parser.add_argument("--dark-mode", action="store_true", help="使用深色模式")
    parser.add_argument("--repo-mode", action="store_true", 
                        help="仓库模式：自动截取多个相关页面")
    
    args = parser.parse_args()
    
    # 解析视口尺寸
    viewport = None
    if args.viewport:
        width, height = map(int, args.viewport.split('x'))
        viewport = {"width": width, "height": height}
    
    async def run():
        if args.repo_mode:
            # 仓库模式：截取多个页面
            screenshots = await capture_repo_screenshots(args.url, args.output)
            print(f"\n✅ 成功截取 {len(screenshots)} 张图片")
            for path in screenshots:
                print(f"   - {path}")
        else:
            # 单页模式
            success = await capture_screenshot(
                url=args.url,
                output_path=args.output,
                viewport=viewport,
                full_page=args.full_page,
                wait_for_selector=args.wait_for,
                dark_mode=args.dark_mode
            )
            if success:
                print(f"✅ 截图已保存: {args.output}")
            else:
                sys.exit(1)
    
    # 运行异步任务
    asyncio.run(run())


if __name__ == "__main__":
    main()
