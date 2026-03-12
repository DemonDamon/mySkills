#!/usr/bin/env python3
"""
爬取GitHub Trending页面，获取热门仓库列表

用途：
1. 爬取 https://github.com/trending 页面
2. 支持按编程语言和时间范围过滤
3. 提取仓库名称、描述、Stars、Forks等信息
"""

import argparse
import json
import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from datetime import datetime

# 自动设置路径：将技能根目录添加到 sys.path
skill_root = Path(__file__).parent.parent
if str(skill_root) not in sys.path:
    sys.path.insert(0, str(skill_root))


async def scrape_github_trending(language: str = "", since: str = "daily", limit: int = 10):
    """
    爬取GitHub Trending页面
    
    Args:
        language: 编程语言过滤（python、javascript、go等）
        since: 时间范围（daily、weekly、monthly）
        limit: 返回数量限制
    
    Returns:
        list: 仓库列表
    """
    print(f"🔍 开始爬取GitHub Trending...")
    print(f"📁 语言: {language if language else '全部'}")
    print(f"⏰ 时间范围: {since}")
    print(f"📊 数量限制: {limit}")
    
    # 构建URL
    base_url = "https://github.com/trending"
    params = []
    if language:
        params.append(f"l={language}")
    if since:
        params.append(f"since={since}")
    
    url = f"{base_url}?{'&'.join(params)}" if params else base_url
    print(f"🔗 URL: {url}\n")
    
    repos = []
    
    async with async_playwright() as p:
        # 启动浏览器
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            # 访问页面
            print("⏳ 正在加载页面...")
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # 等待仓库列表加载
            await page.wait_for_selector('article', timeout=10000)
            
            print("✅ 页面加载完成\n")
            
            # 获取所有仓库article元素
            articles = await page.query_selector_all('article')
            print(f"📝 找到 {len(articles)} 个仓库\n")
            
            # 解析每个仓库
            for idx, article in enumerate(articles[:limit], 1):
                try:
                    # 提取仓库名称
                    repo_element = await article.query_selector('h2 a')
                    repo_name = await repo_element.inner_text() if repo_element else "Unknown"
                    repo_url = await repo_element.get_attribute('href') if repo_element else ""
                    if repo_url:
                        repo_url = f"https://github.com{repo_url}"
                    
                    # 提取描述
                    desc_element = await article.query_selector('p')
                    description = await desc_element.inner_text() if desc_element else ""
                    description = description.strip()
                    
                    # 提取编程语言
                    lang_element = await article.query_selector('span[itemprop="programmingLanguage"]')
                    language_name = await lang_element.inner_text() if lang_element else ""
                    
                    # 提取Stars
                    stars_element = await article.query_selector('a[href*="/stargazers"]')
                    stars_text = await stars_element.inner_text() if stars_element else "0"
                    # 解析Stars数字
                    stars = parse_number(stars_text)
                    
                    # 提取Forks
                    forks_element = await article.query_selector('a[href*="/forks"]')
                    forks_text = await forks_element.inner_text() if forks_element else "0"
                    forks = parse_number(forks_text)
                    
                    # 提取Today的Stars（在stars旁边）
                    today_stars = 0
                    try:
                        # 查找包含"stars today"文本的元素
                        all_text = await article.inner_text()
                        if "stars today" in all_text:
                            # 尝试解析今天的stars
                            import re
                            match = re.search(r'([\d,]+)\s+stars today', all_text)
                            if match:
                                today_stars = parse_number(match.group(1))
                    except:
                        pass
                    
                    # 提取颜色标签（如果存在）
                    color_element = await article.query_selector('span.d-inline-block')
                    color_code = ""
                    if color_element:
                        style = await color_element.get_attribute('style') or ""
                        if 'background-color:' in style:
                            import re
                            match = re.search(r'background-color:\s*#([0-9a-fA-F]+)', style)
                            if match:
                                color_code = f"#{match.group(1)}"
                    
                    repo = {
                        "rank": idx,
                        "name": repo_name.replace('\n', '').replace(' ', ''),
                        "url": repo_url,
                        "description": description,
                        "language": language_name,
                        "stars": stars,
                        "forks": forks,
                        "stars_today": today_stars,
                        "color": color_code,
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    repos.append(repo)
                    
                    print(f"{idx}. {repo['name']}")
                    print(f"   ⭐ {stars} stars | 📈 +{today_stars} today | 🍴 {forks} forks")
                    print(f"   📝 {description[:80]}...")
                    print(f"   🔗 {repo_url}\n")
                    
                except Exception as e:
                    print(f"⚠️  解析仓库 {idx} 失败: {str(e)}")
                    continue
            
        except Exception as e:
            print(f"❌ 爬取失败: {str(e)}")
            raise
        finally:
            await browser.close()
    
    print(f"\n✅ 成功爬取 {len(repos)} 个仓库")
    return repos


def parse_number(text: str) -> int:
    """
    解析数字文本（如 "1.2k", "123"）为整数
    
    Args:
        text: 数字文本
    
    Returns:
        int: 解析后的整数
    """
    import re
    # 移除逗号
    text = text.replace(',', '')
    
    # 处理k（千）
    if 'k' in text.lower():
        match = re.search(r'([\d.]+)k', text.lower())
        if match:
            return int(float(match.group(1)) * 1000)
    
    # 处理纯数字
    match = re.search(r'([\d]+)', text)
    if match:
        return int(match.group(1))
    
    return 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="爬取GitHub Trending页面")
    parser.add_argument("--language", type=str, default="", help="编程语言过滤（python、javascript、go等）")
    parser.add_argument("--since", type=str, default="daily", 
                        choices=["daily", "weekly", "monthly"], help="时间范围")
    parser.add_argument("--limit", type=int, default=10, help="返回数量限制")
    parser.add_argument("--output", type=str, default="trending.json", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    # 运行爬取
    repos = asyncio.run(scrape_github_trending(
        language=args.language,
        since=args.since,
        limit=args.limit
    ))
    
    # 保存到JSON文件
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(repos, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 数据已保存到: {args.output}")


if __name__ == "__main__":
    main()
