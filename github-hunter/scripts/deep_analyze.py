#!/usr/bin/env python3
"""
深度分析GitHub仓库：截图、提取、运行、落盘

核心流程：
1. 爬取GitHub Trending或接收仓库列表
2. 对每个仓库：
   - 打开GitHub页面并截图
   - 提取README和元数据
   - 如果有Demo，打开并截图
   - 克隆仓库到本地
   - 安装依赖并运行示例代码
   - 记录所有输出
3. 保存所有数据到磁盘（JSON + 图片）
"""

import argparse
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from scripts.scrape_trending import scrape_github_trending
from scripts.capture_page import capture_screenshot
from scripts.clone_and_run import clone_and_run


async def analyze_repo(repo_data: dict, output_dir: str, run_code: bool = False) -> dict:
    """
    深度分析单个仓库
    
    Args:
        repo_data: 仓库数据（包含name, url等）
        output_dir: 输出目录
        run_code: 是否运行代码
    
    Returns:
        dict: 完整的分析结果
    """
    repo_name = repo_data["name"].replace("/", "-")
    repo_url = repo_data["url"]
    
    print(f"\n{'='*80}")
    print(f"🔍 深度分析仓库: {repo_data['name']}")
    print(f"{'='*80}\n")
    
    # 创建输出目录
    repo_output_dir = Path(output_dir) / repo_name
    repo_output_dir.mkdir(parents=True, exist_ok=True)
    
    # 分析结果
    analysis = {
        "repo": repo_data,
        "timestamp": datetime.now().isoformat(),
        "screenshots": {},
        "metadata": {},
        "code_run": None,
        "output_dir": str(repo_output_dir)
    }
    
    # 1. 截取GitHub页面
    print(f"📸 步骤1/5: 截取GitHub页面...")
    try:
        github_screenshot = repo_output_dir / "github-page.png"
        await capture_screenshot(
            url=repo_url,
            output_path=str(github_screenshot),
            wait_time=3000
        )
        analysis["screenshots"]["github_page"] = str(github_screenshot)
    except Exception as e:
        print(f"❌ 截图失败: {str(e)}")
    
    # 2. 提取元数据（如果有homepage）
    print(f"\n📋 步骤2/5: 提取元数据...")
    if repo_data.get("description"):
        analysis["metadata"]["description"] = repo_data["description"]
    if repo_data.get("language"):
        analysis["metadata"]["language"] = repo_data["language"]
    if repo_data.get("stars"):
        analysis["metadata"]["stars"] = repo_data["stars"]
    
    # 3. 截取Demo页面（如果有homepage）
    print(f"\n📸 步骤3/5: 检查Demo页面...")
    # 这里需要从GitHub页面提取homepage链接
    # 简化处理：如果有homepage，尝试截图
    # TODO: 从GitHub页面解析homepage
    
    # 4. 克隆并运行代码
    if run_code:
        print(f"\n🚀 步骤4/5: 克隆并运行代码...")
        try:
            work_dir = Path(output_dir) / "repos"
            code_result = clone_and_run(
                repo_url=repo_url,
                work_dir=str(work_dir),
                max_examples=1
            )
            analysis["code_run"] = code_result
            
            # 保存代码运行结果
            result_file = repo_output_dir / "code-run-result.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(code_result, f, ensure_ascii=False, indent=2)
            print(f"💾 代码运行结果已保存: {result_file}")
            
        except Exception as e:
            print(f"❌ 代码运行失败: {str(e)}")
    
    # 5. 保存分析结果
    print(f"\n💾 步骤5/5: 保存分析结果...")
    analysis_file = repo_output_dir / "analysis.json"
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    print(f"✅ 分析结果已保存: {analysis_file}")
    
    print(f"\n{'='*80}")
    print(f"✅ {repo_data['name']} 分析完成")
    print(f"{'='*80}\n")
    
    return analysis


async def deep_analyze_batch(repos: list, output_dir: str = "./output", run_code: bool = False):
    """
    批量深度分析仓库
    
    Args:
        repos: 仓库列表
        output_dir: 输出目录
        run_code: 是否运行代码
    
    Returns:
        list: 所有仓库的分析结果
    """
    print(f"\n{'='*80}")
    print(f"🚀 开始批量深度分析 {len(repos)} 个仓库")
    print(f"{'='*80}\n")
    
    results = []
    
    for idx, repo in enumerate(repos, 1):
        print(f"\n📊 进度: {idx}/{len(repos)}")
        
        try:
            analysis = await analyze_repo(
                repo_data=repo,
                output_dir=output_dir,
                run_code=run_code
            )
            results.append(analysis)
        except Exception as e:
            print(f"❌ 分析失败: {repo['name']} - {str(e)}")
            continue
    
    # 保存总览
    summary_file = Path(output_dir) / "summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*80}")
    print(f"✅ 批量分析完成")
    print(f"📊 成功: {len(results)}/{len(repos)}")
    print(f"💾 总览已保存: {summary_file}")
    print(f"{'='*80}\n")
    
    return results


async def main_workflow(
    scrape: bool = True,
    language: str = "",
    since: str = "daily",
    limit: int = 3,
    repos_file: str = None,
    output_dir: str = "./output",
    run_code: bool = False
):
    """
    主工作流程
    
    Args:
        scrape: 是否爬取Trending
        language: 编程语言过滤
        since: 时间范围
        limit: 数量限制
        repos_file: 仓库列表JSON文件
        output_dir: 输出目录
        run_code: 是否运行代码
    """
    # 1. 获取仓库列表
    if scrape:
        print(f"\n{'='*80}")
        print(f"步骤1: 爬取GitHub Trending")
        print(f"{'='*80}\n")
        
        repos = await scrape_github_trending(
            language=language,
            since=since,
            limit=limit
        )
        
        # 保存仓库列表
        repos_file = Path(output_dir) / "trending-repos.json"
        repos_file.parent.mkdir(parents=True, exist_ok=True)
        with open(repos_file, 'w', encoding='utf-8') as f:
            json.dump(repos, f, ensure_ascii=False, indent=2)
        print(f"\n💾 仓库列表已保存: {repos_file}\n")
    
    elif repos_file:
        print(f"\n{'='*80}")
        print(f"步骤1: 加载仓库列表")
        print(f"{'='*80}\n")
        
        with open(repos_file, 'r', encoding='utf-8') as f:
            repos = json.load(f)
        
        print(f"✅ 加载 {len(repos)} 个仓库\n")
    
    else:
        print("❌ 请提供 --scrape 或 --repos-file 参数")
        return
    
    # 2. 深度分析
    print(f"\n{'='*80}")
    print(f"步骤2: 深度分析仓库")
    print(f"{'='*80}\n")
    
    await deep_analyze_batch(
        repos=repos,
        output_dir=output_dir,
        run_code=run_code
    )
    
    # 3. 生成报告
    print(f"\n{'='*80}")
    print(f"步骤3: 生成分析报告")
    print(f"{'='*80}\n")
    
    print("📊 分析完成！所有数据已保存到:")
    print(f"   - {output_dir}/")
    print(f"   - 每个仓库的目录: owner-repo/")
    print(f"     ├── github-page.png (GitHub页面截图)")
    print(f"     ├── analysis.json (分析结果)")
    print(f"     └── code-run-result.json (代码运行结果，如果运行了)")
    print(f"   - summary.json (总览)")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="深度分析GitHub仓库：截图、提取、运行、落盘")
    
    # 数据来源
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--scrape", action="store_true", help="爬取GitHub Trending")
    group.add_argument("--repos-file", type=str, help="从JSON文件加载仓库列表")
    
    # 爬取参数
    parser.add_argument("--language", type=str, default="", help="编程语言过滤")
    parser.add_argument("--since", type=str, default="daily", choices=["daily", "weekly", "monthly"], help="时间范围")
    parser.add_argument("--limit", type=int, default=3, help="数量限制")
    
    # 输出参数
    parser.add_argument("--output-dir", type=str, default="./output", help="输出目录")
    parser.add_argument("--run-code", action="store_true", help="是否运行代码（需要较长时间）")
    
    args = parser.parse_args()
    
    # 运行主流程
    asyncio.run(main_workflow(
        scrape=args.scrape,
        language=args.language,
        since=args.since,
        limit=args.limit,
        repos_file=args.repos_file,
        output_dir=args.output_dir,
        run_code=args.run_code
    ))


if __name__ == "__main__":
    main()
