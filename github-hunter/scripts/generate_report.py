#!/usr/bin/env python3
"""
GitHub Trending日报生成器

用途：
1. 基于Trending数据和趋势分析生成精美日报
2. 支持Markdown格式输出
3. 包含表格、趋势判断、一句话总结
"""

import json
from datetime import datetime
from pathlib import Path


def generate_one_liner(repo: dict) -> str:
    """
    为项目生成一句话总结
    
    Args:
        repo: 仓库数据
    
    Returns:
        str: 一句话总结
    """
    name = repo.get("name", "")
    desc = repo.get("description", "")
    language = repo.get("language", "")
    stars_today = repo.get("stars_today", 0)
    
    # 从描述中提取关键信息
    desc_lower = desc.lower()
    
    # 特殊模式识别
    if "agent" in desc_lower:
        return f"AI Agent框架，{desc[:50]}"
    elif "framework" in desc_lower or "sdk" in desc_lower:
        return f"{language}框架，{desc[:50]}"
    elif "tool" in desc_lower or "toolkit" in desc_lower:
        return f"{language}工具，{desc[:50]}"
    elif "api" in desc_lower:
        return f"API服务，{desc[:50]}"
    elif "chat" in desc_lower or "chatgpt" in desc_lower:
        return f"聊天AI，{desc[:50]}"
    elif "security" in desc_lower or "test" in desc_lower:
        return f"测试安全，{desc[:50]}"
    else:
        # 默认：取描述前60个字符
        return desc[:60] if desc else f"{language}项目"


def get_company_flag(repo: dict) -> str:
    """
    获取公司/国家标识
    
    Args:
        repo: 仓库数据
    
    Returns:
        str: 标识（如 🇨🇳、🇺🇸）
    """
    owner = repo.get("name", "").split("/")[0].lower()
    
    # 中国公司
    china_companies = ["alibaba", "bytedance", "tencent", "baidu", "modelscope", "volcengine", "thudga"]
    if any(c in owner for c in china_companies):
        return " 🇨🇳"
    
    # 其他国家
    if "sepinf" in owner:
        return " 🇧🇷"
    if "huggingface" in owner:
        return " 🇩🇪"
    
    return ""


def generate_daily_report(repos: list, analysis: dict, output_path: str = "daily_report.md") -> str:
    """
    生成日报Markdown
    
    Args:
        repos: 仓库列表
        analysis: 趋势分析结果
        output_path: 输出文件路径
    
    Returns:
        str: Markdown内容
    """
    today = datetime.now().strftime("%Y.%m.%d")
    
    md_lines = []
    
    # 标题
    md_lines.append(f"# 🔥 GitHub Trending 日报 — {today}")
    md_lines.append("")
    
    # 全站热榜
    md_lines.append("## 🏆 全站热榜 TOP 15")
    md_lines.append("")
    md_lines.append("| # | 项目 | 一句话 | Stars今日 |")
    md_lines.append("|---|------|--------|----------|")
    
    for idx, repo in enumerate(repos[:15], 1):
        name = repo.get("name", "")
        one_liner = generate_one_liner(repo)
        flag = get_company_flag(repo)
        stars_today = repo.get("stars_today", 0)
        language = repo.get("language", "")
        
        # 格式化项目名称
        project_name = f"[{name}]({repo.get('url', '#')}){flag}"
        
        # 格式化一句话
        one_liner_display = one_liner
        if language and len(one_liner_display) < 55:
            one_liner_display = f"{one_liner_display}。{language}"
        
        # 格式化Stars
        stars_display = f"⭐{stars_today}" if stars_today > 0 else "-"
        
        md_lines.append(f"| {idx} | {project_name} | {one_liner_display} | {stars_display} |")
    
    md_lines.append("")
    
    # 趋势判断
    md_lines.append("## 📊 今日趋势判断")
    md_lines.append("")
    
    for insight in analysis.get("insights", []):
        md_lines.append(f"- {insight}")
    
    md_lines.append("")
    
    # 编程语言分布
    if analysis.get("languages"):
        md_lines.append("### 💻 编程语言分布")
        md_lines.append("")
        for lang, count in analysis["languages"].items():
            md_lines.append(f"- **{lang}**: {count}个项目")
        md_lines.append("")
    
    # 热点主题
    if analysis.get("hot_themes"):
        md_lines.append("### 🔥 热点主题")
        md_lines.append("")
        for topic, count in analysis["hot_themes"]:
            md_lines.append(f"- **{topic}**: {count}个项目")
        md_lines.append("")
    
    # 地区/公司分布
    if analysis.get("companies"):
        md_lines.append("### 🌍 地区/公司分布")
        md_lines.append("")
        for region, count in analysis["companies"].items():
            md_lines.append(f"- {region}: {count}个项目")
        md_lines.append("")
    
    # 大佬项目
    if analysis.get("influencers"):
        md_lines.append("### ⭐ 大佬项目")
        md_lines.append("")
        for item in analysis["influencers"]:
            md_lines.append(f"- [{item['name']}](https://github.com/{item['name']}) — {item['influencer']}")
        md_lines.append("")
    
    # 加入Markdown内容
    md_content = "\n".join(md_lines)
    
    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ 日报已生成: {output_path}")
    
    return md_content


def generate_detailed_blog(repos: list, analysis: dict, output_dir: str = "./output") -> str:
    """
    生成详细博客文章（含截图引用）
    
    Args:
        repos: 仓库列表
        analysis: 趋势分析结果
        output_dir: 输出目录（包含截图）
    
    Returns:
        str: Markdown内容
    """
    today = datetime.now().strftime("%Y年%m月%d日")
    
    md_lines = []
    
    # 标题
    md_lines.append(f"# GitHub Trending 热门项目推荐 — {today}")
    md_lines.append("")
    
    # 导语
    md_lines.append("今天GitHub Trending上有几个非常有趣的项目，让我们一起来看看吧！")
    md_lines.append("")
    
    # 趋势概览
    md_lines.append("## 📊 今日趋势概览")
    md_lines.append("")
    for insight in analysis.get("insights", []):
        md_lines.append(f"{insight}")
    md_lines.append("")
    
    # 项目详情
    md_lines.append("## 🏆 热门项目推荐")
    md_lines.append("")
    
    output_dir = Path(output_dir)
    
    for idx, repo in enumerate(repos[:10], 1):
        name = repo.get("name", "")
        stars = repo.get("stars", 0)
        stars_today = repo.get("stars_today", 0)
        language = repo.get("language", "")
        desc = repo.get("description", "暂无描述")
        url = repo.get("url", "")
        flag = get_company_flag(repo)
        
        # 项目标题
        md_lines.append(f"### {idx}. [{name}]({url}){flag} ⭐{stars:,}")
        
        # 截图（如果存在）
        repo_dir_name = name.replace("/", "-")
        screenshot_path = output_dir / repo_dir_name / "github-page.png"
        
        if screenshot_path.exists():
            md_lines.append("")
            md_lines.append(f"![{name} GitHub页面]({screenshot_path})")
        
        md_lines.append("")
        
        # 项目简介
        md_lines.append(f"**项目简介**：{desc}")
        md_lines.append("")
        
        # 技术特点（基于描述生成）
        md_lines.append("**技术特点**：")
        features = extract_features(desc, language)
        for feature in features:
            md_lines.append(f"- {feature}")
        md_lines.append("")
        
        # 数据统计
        md_lines.append(f"**数据统计**：")
        md_lines.append(f"- ⭐ Stars: {stars:,} (今日 +{stars_today})")
        md_lines.append(f"- 🍴 Forks: {repo.get('forks', 0):,}")
        if language:
            md_lines.append(f"- 💻 语言: {language}")
        md_lines.append("")
        
        # 推荐理由
        one_liner = generate_one_liner(repo)
        md_lines.append(f"**推荐理由**：{one_liner}")
        md_lines.append("")
        
        md_lines.append("---")
        md_lines.append("")
    
    # 总结
    md_lines.append("## 📝 总结")
    md_lines.append("")
    md_lines.append("今天的GitHub Trending展示了一些非常有趣的趋势：")
    md_lines.append("")
    
    for insight in analysis.get("insights", [])[:3]:
        md_lines.append(f"- {insight}")
    
    md_lines.append("")
    md_lines.append("## 🔗 参考链接")
    md_lines.append("")
    md_lines.append("- [GitHub Trending](https://github.com/trending)")
    md_lines.append("")
    
    # 保存文件
    output_path = "detailed_blog.md"
    md_content = "\n".join(md_lines)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"✅ 详细博客已生成: {output_path}")
    
    return md_content


def extract_features(desc: str, language: str) -> list:
    """
    从描述中提取技术特点
    
    Args:
        desc: 项目描述
        language: 编程语言
    
    Returns:
        list: 特点列表
    """
    features = []
    desc_lower = desc.lower()
    
    # 识别关键特性
    if "agent" in desc_lower:
        features.append("🤖 AI Agent框架")
    if "autonomous" in desc_lower:
        features.append("🚀 支持自主决策")
    if "multi-agent" in desc_lower:
        features.append("👥 多智能体协作")
    if "llm" in desc_lower or "gpt" in desc_lower:
        features.append("🧠 支持LLM模型")
    if "framework" in desc_lower:
        features.append("🛠️ 完整框架支持")
    if "tool" in desc_lower:
        features.append("🔧 丰富工具集")
    if "api" in desc_lower:
        features.append("🌐 RESTful API")
    if "open source" in desc_lower:
        features.append("📖 开源免费")
    
    # 如果没有识别到，使用默认
    if not features:
        if language:
            features.append(f"💻 基于{language}开发")
        features.append("🎯 功能完善")
    
    return features[:3]  # 最多3个特点


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Trending日报生成器")
    parser.add_argument("--repos", type=str, default="trending.json", help="Trending数据JSON")
    parser.add_argument("--trends", type=str, default="trends.json", help="趋势分析JSON")
    parser.add_argument("--output-dir", type=str, default="./output", help="输出目录（含截图）")
    parser.add_argument("--format", type=str, default="both", choices=["daily", "detailed", "both"], help="输出格式")
    
    args = parser.parse_args()
    
    # 读取数据
    with open(args.repos, 'r', encoding='utf-8') as f:
        repos = json.load(f)
    
    with open(args.trends, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    # 生成报告
    if args.format in ["daily", "both"]:
        generate_daily_report(repos, analysis, "daily_report.md")
    
    if args.format in ["detailed", "both"]:
        generate_detailed_blog(repos, analysis, args.output_dir)


if __name__ == "__main__":
    main()
