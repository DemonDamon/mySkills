#!/usr/bin/env python3
"""
GitHub Trending趋势分析器

用途：
1. 分析Trending项目的趋势特征
2. 识别热点主题、技术栈、公司分布
3. 生成趋势判断和洞察
"""

import json
from collections import Counter
from datetime import datetime


# 热点主题关键词映射
HOT_TOPICS = {
    "Agent": ["agent", "autonomous", "multi-agent", "ai agent", "llm agent"],
    "LLM": ["llm", "gpt", "chatgpt", "language model", "transformer"],
    "RAG": ["rag", "retrieval", "vector", "embedding", "knowledge base"],
    "AI安全": ["security", "red team", "pentest", "vulnerability", "safety"],
    "工具链": ["tool", "framework", "sdk", "library", "toolkit"],
    "多模态": ["multimodal", "vision", "image", "video", "audio"],
    "低代码": ["no-code", "low-code", "visual", "drag", "workflow"],
    "数据科学": ["data", "analytics", "visualization", "jupyter", "notebook"],
    "区块链": ["blockchain", "web3", "crypto", "defi", "nft"],
    "DevOps": ["devops", "ci/cd", "kubernetes", "docker", "deployment"],
}

# 公司/组织标识
COMPANIES = {
    "🇨🇳 中国": ["alibaba", "bytedance", "tencent", "baidu", "modelscope", "volcengine", "thudga"],
    "🇺🇸 美国": ["google", "microsoft", "meta", "openai", "anthropic", "nvidia"],
    "🇧🇷 巴西": ["sepinf"],
    "🇩🇪 德国": ["huggingface"],
}

# 大佬标识
INFLUENCERS = {
    "karpathy": "Karpathy（前Tesla AI总监）",
    "sama": "Sam Altman（OpenAI CEO）",
    "gdb": "Grady Booch",
}


def analyze_trends(repos: list) -> dict:
    """
    分析GitHub Trending趋势
    
    Args:
        repos: 仓库列表
    
    Returns:
        dict: 趋势分析结果
    """
    analysis = {
        "total_count": len(repos),
        "languages": {},
        "topics": {},
        "companies": {},
        "influencers": [],
        "total_stars_today": 0,
        "avg_stars_today": 0,
        "insights": [],
        "hot_themes": [],
    }
    
    # 统计编程语言
    languages = [repo.get("language", "Unknown") for repo in repos if repo.get("language")]
    analysis["languages"] = dict(Counter(languages).most_common(5))
    
    # 统计今日总Stars
    stars_today = [repo.get("stars_today", 0) for repo in repos]
    analysis["total_stars_today"] = sum(stars_today)
    analysis["avg_stars_today"] = round(sum(stars_today) / len(stars_today), 1) if stars_today else 0
    
    # 识别热点主题
    for topic, keywords in HOT_TOPICS.items():
        count = 0
        for repo in repos:
            desc = (repo.get("description", "") + " " + repo.get("name", "")).lower()
            if any(kw in desc for kw in keywords):
                count += 1
        
        if count > 0:
            analysis["topics"][topic] = count
    
    # 排序主题
    analysis["hot_themes"] = sorted(analysis["topics"].items(), key=lambda x: x[1], reverse=True)[:3]
    
    # 识别公司/国家
    for region, companies in COMPANIES.items():
        count = 0
        for repo in repos:
            owner = repo.get("name", "").split("/")[0].lower()
            if any(company in owner for company in companies):
                count += 1
        
        if count > 0:
            analysis["companies"][region] = count
    
    # 识别大佬
    for repo in repos:
        owner = repo.get("name", "").split("/")[0].lower()
        for influencer_id, influencer_name in INFLUENCERS.items():
            if influencer_id in owner:
                analysis["influencers"].append({
                    "name": repo.get("name"),
                    "influencer": influencer_name
                })
    
    # 生成洞察
    analysis["insights"] = generate_insights(analysis, repos)
    
    return analysis


def generate_insights(analysis: dict, repos: list) -> list:
    """
    生成趋势洞察
    
    Args:
        analysis: 分析结果
        repos: 仓库列表
    
    Returns:
        list: 洞察列表
    """
    insights = []
    
    # 主题洞察
    if analysis["hot_themes"]:
        top_theme, count = analysis["hot_themes"][0]
        percentage = round(count / analysis["total_count"] * 100, 1)
        if percentage > 30:
            insights.append(f"🔥 **{top_theme}爆发** — {count}个项目（{percentage}%）都在做{top_theme}相关，这是当前的绝对热点")
    
    # 中国力量洞察
    if "🇨🇳 中国" in analysis["companies"]:
        china_count = analysis["companies"]["🇨🇳 中国"]
        if china_count >= 3:
            companies_list = []
            for repo in repos:
                owner = repo.get("name", "").split("/")[0].lower()
                if any(c in owner for c in COMPANIES["🇨🇳 中国"]):
                    companies_list.append(repo.get("name", "").split("/")[0])
            
            unique_companies = list(set(companies_list))[:3]
            insights.append(f"🇨🇳 **中国力量崛起** — {china_count}个项目上榜，{', '.join(unique_companies)}等大厂集体发力")
    
    # 大佬洞察
    if analysis["influencers"]:
        for item in analysis["influencers"]:
            insights.append(f"⭐ **大佬效应** — {item['influencer']}出品：{item['name']}，标杆级项目")
    
    # 语言洞察
    if analysis["languages"]:
        top_lang, lang_count = list(analysis["languages"].items())[0]
        if lang_count >= 3:
            insights.append(f"💻 **{top_lang}主导** — {lang_count}个项目使用{top_lang}，最受欢迎的技术栈")
    
    # Stars洞察
    if analysis["total_stars_today"] > 10000:
        insights.append(f"📈 **热度爆表** — 今日共新增 {analysis['total_stars_today']:,} stars，社区活跃度极高")
    
    # 安全洞察
    if "AI安全" in analysis["topics"] and analysis["topics"]["AI安全"] > 0:
        insights.append(f"🔒 **安全成刚需** — LLM安全和测试已成行业共识，测试工具需求旺盛")
    
    # 开源生态洞察
    if analysis["total_count"] >= 10:
        insights.append(f"🌐 **开源繁荣** — {analysis['total_count']}个高质量项目涌现，开源生态持续繁荣")
    
    return insights


def print_analysis(analysis: dict):
    """
    打印趋势分析
    
    Args:
        analysis: 分析结果
    """
    print(f"\n{'='*80}")
    print(f"📊 GitHub Trending 趋势分析")
    print(f"{'='*80}\n")
    
    print(f"📈 数据概览：")
    print(f"   - 项目总数: {analysis['total_count']}")
    print(f"   - 今日总Stars: {analysis['total_stars_today']:,}")
    print(f"   - 平均今日Stars: {analysis['avg_stars_today']}\n")
    
    print(f"💻 编程语言分布：")
    for lang, count in analysis["languages"].items():
        print(f"   - {lang}: {count}个")
    print()
    
    print(f"🔥 热点主题：")
    for topic, count in analysis["hot_themes"]:
        print(f"   - {topic}: {count}个项目")
    print()
    
    if analysis["companies"]:
        print(f"🌍 地区/公司分布：")
        for region, count in analysis["companies"].items():
            print(f"   - {region}: {count}个项目")
        print()
    
    if analysis["influencers"]:
        print(f"⭐ 大佬项目：")
        for item in analysis["influencers"]:
            print(f"   - {item['name']} ({item['influencer']})")
        print()
    
    print(f"💡 趋势洞察：")
    for idx, insight in enumerate(analysis["insights"], 1):
        print(f"   {idx}. {insight}")
    
    print(f"\n{'='*80}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GitHub Trending趋势分析")
    parser.add_argument("--input", type=str, default="trending.json", help="输入JSON文件（Trending数据）")
    parser.add_argument("--output", type=str, default="trends.json", help="输出JSON文件")
    
    args = parser.parse_args()
    
    # 读取Trending数据
    with open(args.input, 'r', encoding='utf-8') as f:
        repos = json.load(f)
    
    # 分析趋势
    analysis = analyze_trends(repos)
    
    # 打印分析
    print_analysis(analysis)
    
    # 保存分析结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)
    
    print(f"💾 分析结果已保存: {args.output}")


if __name__ == "__main__":
    main()
