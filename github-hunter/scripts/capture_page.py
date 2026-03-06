#!/usr/bin/env python3
"""
打开URL并截取全页面截图

用途：
1. 打开指定的URL
2. 等待页面完全加载
3. 截取全页面截图
4. 保存到指定路径
"""

import argparse
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path


async def capture_screenshot(
    url: str, 
    output_path: str, 
    wait_selector: str = None,
    wait_time: int = 3000,
    width: int = 1920,
    height: int = 1080
):
    """
    截取网页截图
    
    Args:
        url: 目标URL
        output_path: 输出图片路径
        wait_selector: 等待特定选择器加载
        wait_time: 额外等待时间（毫秒）
        width: 视口宽度
        height: 视口高度
    
    Returns:
        str: 截图保存路径
    """
    print(f"📸 正在截图: {url}")
    
    # 确保输出目录存在
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': width, 'height': height},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # 访问页面
            print(f"⏳ 正在加载页面...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 等待特定元素
            if wait_selector:
                print(f"⏳ 等待元素: {wait_selector}")
                await page.wait_for_selector(wait_selector, timeout=15000)
            
            # 额外等待时间
            if wait_time > 0:
                print(f"⏳ 等待 {wait_time}ms...")
                await asyncio.sleep(wait_time / 1000)
            
            # 截取全页面
            print(f"📸 正在截图...")
            await page.screenshot(
                path=str(output_path),
                full_page=True,
                type='png'
            )
            
            print(f"✅ 截图已保存: {output_path}")
            return str(output_path)
            
        except Exception as e:
            print(f"❌ 截图失败: {str(e)}")
            raise
        finally:
            await browser.close()


async def capture_screenshots_batch(urls: list, output_dir: str, prefix: str = ""):
    """
    批量截图
    
    Args:
        urls: URL列表
        output_dir: 输出目录
        prefix: 文件名前缀
    
    Returns:
        list: 截图路径列表
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results = []
    
    for idx, url in enumerate(urls, 1):
        try:
            # 生成文件名
            if prefix:
                filename = f"{prefix}_{idx}.png"
            else:
                filename = f"screenshot_{idx}.png"
            
            output_path = output_dir / filename
            
            # 截图
            result = await capture_screenshot(url, str(output_path))
            results.append(result)
            
            # 避免请求过快
            await asyncio.sleep(1)
            
        except Exception as e:
            print(f"⚠️  截图失败: {url} - {str(e)}")
            continue
    
    return results


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="打开URL并截取全页面截图")
    parser.add_argument("--url", type=str, help="目标URL")
    parser.add_argument("--urls", type=str, nargs="*", help="批量URL列表")
    parser.add_argument("--output", type=str, required=True, help="输出图片路径（或目录）")
    parser.add_argument("--wait-selector", type=str, help="等待特定选择器加载")
    parser.add_argument("--wait-time", type=int, default=3000, help="额外等待时间（毫秒）")
    parser.add_argument("--width", type=int, default=1920, help="视口宽度")
    parser.add_argument("--height", type=int, default=1080, help="视口高度")
    
    args = parser.parse_args()
    
    # 单个URL
    if args.url:
        asyncio.run(capture_screenshot(
            url=args.url,
            output_path=args.output,
            wait_selector=args.wait_selector,
            wait_time=args.wait_time,
            width=args.width,
            height=args.height
        ))
    
    # 批量URL
    elif args.urls:
        asyncio.run(capture_screenshots_batch(
            urls=args.urls,
            output_dir=args.output
        ))
    
    else:
        print("❌ 请提供 --url 或 --urls 参数")
        parser.print_help()


if __name__ == "__main__":
    main()
