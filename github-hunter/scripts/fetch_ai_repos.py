#!/usr/bin/env python3
"""
获取AI领域生产级GitHub仓库（支持离线模式）

授权方式: ApiKey
凭证Key: COZE_GITHUB_API_7613777400777867298
"""

import os
import argparse
import json
import sys
from datetime import datetime, timedelta
from coze_workload_identity import requests


# AI领域关键词配置
AI_KEYWORDS = {
    "LLM": ["llm", "gpt", "language model", "text generation", "chatbot", "transformer", "bert"],
    "CV": ["computer vision", "image", "object detection", "segmentation", "yolo", "stable diffusion"],
    "NLP": ["nlp", "natural language", "text processing", "sentiment", "translation", "tokenization"],
    "ML": ["machine learning", "deep learning", "neural network", "pytorch", "tensorflow"],
    "Generative": ["generative", "diffusion", "gan", "vae", "image generation"],
    "RAG": ["rag", "retrieval", "vector database", "embedding", "semantic search"],
    "Agent": ["agent", "autonomous", "tool use", "function calling", "multi-agent"],
    "Audio": ["audio", "speech", "tts", "stt", "voice", "whisper"],
    "MultiModal": ["multimodal", "vision-language", "clip", "blip"],
}

QUALITY_THRESHOLDS = {
    "min_stars": 1000,
    "min_forks": 50,
    "recent_updates_days": 90,
    "has_description": True,
}

# 时间周期配置（天数）
PERIOD_DAYS = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "quarterly": 90
}


# 模拟数据（离线模式使用）
MOCK_REPOS = [
    {
        "name": "modelscope/agentscope",
        "owner": "modelscope",
        "description": "An innovative framework for building multi-agent applications with ease, featuring open-source LLMs and tool-use capabilities.",
        "stars": 17000,
        "forks": 1200,
        "language": "Python",
        "url": "https://github.com/modelscope/agentscope",
        "homepage": "https://modelscope.cn/agentscope",
        "created_at": "2023-09-01T00:00:00Z",
        "updated_at": "2024-02-20T00:00:00Z",
        "pushed_at": "2024-02-20T00:00:00Z",
        "topics": ["llm", "agent", "multi-agent", "tool-use", "python"],
        "open_issues": 85,
        "license": "Apache License 2.0",
        "days_since_creation": 180,
        "stars_per_day": 94.44,
        "quality_score": 95,
        "rising_score": 88,
        "is_mock": True
    },
    {
        "name": "openai/transformers",
        "owner": "openai",
        "description": "State-of-the-art machine learning for PyTorch and TensorFlow 2.0.",
        "stars": 125000,
        "forks": 25000,
        "language": "Python",
        "url": "https://github.com/openai/transformers",
        "homepage": "https://huggingface.co/",
        "created_at": "2018-10-01T00:00:00Z",
        "updated_at": "2024-02-25T00:00:00Z",
        "pushed_at": "2024-02-25T00:00:00Z",
        "topics": ["nlp", "transformer", "bert", "gpt", "pytorch"],
        "open_issues": 1200,
        "license": "Apache License 2.0",
        "days_since_creation": 2000,
        "stars_per_day": 62.5,
        "quality_score": 98,
        "rising_score": 75,
        "is_mock": True
    },
    {
        "name": "langchain-ai/langchain",
        "owner": "langchain-ai",
        "description": "Building applications with LLMs through composability.",
        "stars": 78000,
        "forks": 11000,
        "language": "Python",
        "url": "https://github.com/langchain-ai/langchain",
        "homepage": "https://langchain.com",
        "created_at": "2022-10-01T00:00:00Z",
        "pushed_at": "2024-02-25T00:00:00Z",
        "topics": ["llm", "agent", "rag", "python", "openai"],
        "open_issues": 800,
        "license": "MIT License",
        "days_since_creation": 500,
        "stars_per_day": 156.0,
        "quality_score": 96,
        "rising_score": 92,
        "is_mock": True
    },
    {
        "name": "microsoft/semantic-kernel",
        "owner": "microsoft",
        "description": "Integrate cutting-edge LLM technology quickly and easily into your apps.",
        "stars": 19000,
        "forks": 2000,
        "language": "C#",
        "url": "https://github.com/microsoft/semantic-kernel",
        "homepage": "https://learn.microsoft.com/semantic-kernel",
        "created_at": "2023-02-01T00:00:00Z",
        "pushed_at": "2024-02-24T00:00:00Z",
        "topics": ["llm", "agent", "microsoft", "csharp", "openai"],
        "open_issues": 150,
        "license": "MIT License",
        "days_since_creation": 400,
        "stars_per_day": 47.5,
        "quality_score": 94,
        "rising_score": 80,
        "is_mock": True
    },
    {
        "name": "deepset-ai/haystack",
        "owner": "deepset-ai",
        "description": "Haystack is an open source NLP framework that leverages transformer models to enable various NLP tasks.",
        "stars": 16000,
        "forks": 1800,
        "language": "Python",
        "url": "https://github.com/deepset-ai/haystack",
        "homepage": "https://haystack.deepset.ai",
        "created_at": "2020-03-01T00:00:00Z",
        "pushed_at": "2024-02-23T00:00:00Z",
        "topics": ["nlp", "rag", "retrieval", "elasticsearch", "transformer"],
        "open_issues": 300,
        "license": "Apache License 2.0",
        "days_since_creation": 1460,
        "stars_per_day": 10.96,
        "quality_score": 93,
        "rising_score": 70,
        "is_mock": True
    }
]


def calculate_quality_score(repo, min_stars):
    """
    计算仓库质量分数
    
    Args:
        repo: 仓库信息字典
        min_stars: 最小stars阈值
    
    Returns:
        int: 质量分数 (0-100)
    """
    score = 0
    
    # Stars评分 (40分)
    stars = repo.get("stars", 0)
    if stars >= min_stars * 10:
        score += 40
    elif stars >= min_stars * 5:
        score += 30
    elif stars >= min_stars:
        score += 20
    
    # Forks评分 (20分)
    forks = repo.get("forks", 0)
    fork_ratio = forks / stars if stars > 0 else 0
    if fork_ratio >= 0.3:
        score += 20
    elif fork_ratio >= 0.1:
        score += 10
    
    # 活跃度评分 (20分)
    updated_at_str = repo.get("updated_at", "")
    if updated_at_str:
        try:
            updated_at = datetime.strptime(updated_at_str, "%Y-%m-%dT%H:%M:%SZ")
            days_since_update = (datetime.now() - updated_at).days
            if days_since_update <= 7:
                score += 20
            elif days_since_update <= 30:
                score += 15
            elif days_since_update <= 90:
                score += 10
        except:
            pass
    
    # 文档完整性 (20分)
    description = repo.get("description", "")
    homepage = repo.get("homepage")
    topics = repo.get("topics", [])
    
    if description and len(description) > 20:
        score += 5
    if homepage:
        score += 5
    if len(topics) > 0:
        score += 5
    if repo.get("license"):
        score += 5
    
    return min(score, 100)


def calculate_rising_score(repo):
    """
    计算新星指数（增长速度）
    
    Args:
        repo: 仓库信息字典
    
    Returns:
        int: 新星分数 (0-100)
    """
    score = 0
    stars_per_day = repo.get("stars_per_day", 0)
    stars = repo.get("stars", 0)
    days = repo.get("days_since_creation", 1)
    
    # 日均增长评分 (50分)
    if stars_per_day >= 100:
        score += 50
    elif stars_per_day >= 50:
        score += 40
    elif stars_per_day >= 10:
        score += 30
    elif stars_per_day >= 5:
        score += 20
    
    # 总量平衡 (30分) - 新项目不能太冷门
    if stars >= 5000:
        score += 30
    elif stars >= 1000:
        score += 20
    elif stars >= 500:
        score += 10
    
    # 近期活跃度 (20分)
    pushed_at_str = repo.get("pushed_at", "")
    if pushed_at_str:
        try:
            pushed_at = datetime.strptime(pushed_at_str, "%Y-%m-%dT%H:%M:%SZ")
            days_since_push = (datetime.now() - pushed_at).days
            if days_since_push <= 7:
                score += 20
            elif days_since_push <= 30:
                score += 15
            elif days_since_push <= 90:
                score += 10
        except:
            pass
    
    return min(score, 100)


def search_ai_repos(focus_area: str = "", min_stars: int = 1000, limit: int = 10, 
                     period: str = "monthly", mode: str = "rising", 
                     include_repos: list = None, debug: bool = False,
                     offline: bool = False):
    """
    搜索AI领域的高质量仓库
    
    Args:
        focus_area: 聚焦领域（LLM/CV/NLP等），空字符串表示全部AI领域
        min_stars: 最小stars数
        limit: 返回数量限制
        period: 时间周期（daily/weekly/monthly/quarterly）
        mode: 模式（new=只显示新创建的，rising=显示增长最快的）
        include_repos: 强制包含的仓库列表（如 ["modelscope/agentscope"]）
        debug: 是否显示调试信息
        offline: 是否使用离线模式（使用模拟数据）
    
    Returns:
        list: 高质量AI仓库列表
    """
    
    # 检查是否使用离线模式
    if offline:
        print("⚠️  使用离线模式（模拟数据）")
        print(f"💡 要使用真实GitHub数据，请确保网络连接正常并配置API Token")
        
        repos = []
        for mock_repo in MOCK_REPOS:
            # 应用筛选条件
            if mock_repo["stars"] < min_stars:
                continue
            
            # 检查强制包含
            if include_repos and mock_repo["name"] not in include_repos:
                # 如果指定了强制包含，且当前仓库不在列表中，则跳过
                # 除非这是强制包含的仓库
                if not any([repo["name"] == mock_repo["name"] for repo in repos if repo["name"] in include_repos]):
                    pass
            
            repos.append(mock_repo)
        
        # 按模式排序
        if mode == "rising":
            repos.sort(key=lambda x: x["rising_score"], reverse=True)
        else:
            repos.sort(key=lambda x: x["stars"], reverse=True)
        
        # 限制数量
        repos = repos[:limit]
        
        if debug:
            print(f"[DEBUG] 离线模式返回 {len(repos)} 个仓库")
        
        return repos
    
    # 1. 获取凭证
    skill_id = "7613777400777867298"
    token = os.getenv("COZE_GITHUB_API_7613777400777867298")
    if not token:
        print("⚠️  未配置GitHub API Token，切换到离线模式")
        return search_ai_repos(focus_area, min_stars, limit, period, mode, include_repos, debug, offline=True)
    
    # 2. 确定时间筛选天数
    days = PERIOD_DAYS.get(period.lower(), 30)
    cutoff_date = datetime.now().date() - timedelta(days=days)
    
    if debug:
        print(f"[DEBUG] 时间范围: {cutoff_date} ~ {datetime.now().date()} ({days}天)")
        print(f"[DEBUG] 模式: {mode}")
        print(f"[DEBUG] 强制包含: {include_repos}")
    
    # 3. 构建搜索关键词（简化查询，避免422错误）
    # 只使用最核心的关键词，避免查询过长
    if focus_area and focus_area.upper() in AI_KEYWORDS:
        keywords = AI_KEYWORDS[focus_area.upper()][:2]  # 每个领域最多2个关键词
    else:
        # 使用最通用的AI关键词
        keywords = ["agent", "llm", "ai"]
    
    # 构建简化的查询字符串
    search_query = " OR ".join([f'"{kw}"' for kw in keywords])
    
    if debug:
        print(f"[DEBUG] 搜索查询: {search_query}")
    
    # 4. 构建搜索参数（避免422错误）
    search_url = "https://api.github.com/search/repositories"
    
    # 简化查询参数，避免过于复杂的搜索条件
    if mode == "new":
        # 新模式：只选择指定时间范围内创建的项目
        query_stars = max(min_stars, 100)
        params = {
            "q": f'{search_query} stars:>{query_stars} created:>{cutoff_date}',
            "sort": "stars",
            "order": "desc",
            "per_page": limit * 2
        }
    else:
        # 新星模式（默认）：简化查询，避免时间筛选导致422
        params = {
            "q": f'{search_query} stars:>{min_stars}',
            "sort": "stars",
            "order": "desc",
            "per_page": limit * 3
        }
    
    # 5. 构建请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI-Project-Hunter"
    }
    
    try:
        # 6. 发起请求
        response = requests.get(search_url, headers=headers, params=params, timeout=30)
        
        if response.status_code >= 400:
            error_msg = f"GitHub API请求失败: 状态码 {response.status_code}"
            try:
                error_data = response.json()
                error_msg += f", 消息: {error_data.get('message', '未知错误')}"
                
                # GitHub API常见的错误处理
                if response.status_code == 403:
                    if 'API rate limit' in error_data.get('message', ''):
                        error_msg += "\n💡 建议: API速率限制，请稍后再试或使用认证Token"
                    else:
                        error_msg += "\n💡 建议: 可能是网络访问受限，尝试使用 --offline 参数"
                elif response.status_code == 404:
                    error_msg += "\n💡 建议: 搜索查询格式可能有问题"
                elif response.status_code == 422:
                    error_msg += f"\n💡 建议: 查询参数验证失败 - {error_data}"
                    error_msg += "\n💡 尝试使用 --offline 参数测试功能流程"
            except:
                pass
            
            # 自动切换到离线模式
            print(f"⚠️  {error_msg}")
            print("💡 自动切换到离线模式...")
            return search_ai_repos(focus_area, min_stars, limit, period, mode, include_repos, debug, offline=True)
        
        data = response.json()
        
        # 检查是否返回了有效数据
        if not isinstance(data, dict):
            raise Exception(f"GitHub API返回了无效的数据格式: {type(data)}")
        
        if "items" not in data:
            if "message" in data:
                raise Exception(f"GitHub API返回错误: {data.get('message')}")
            else:
                raise Exception(f"GitHub API返回了意外的数据结构: {list(data.keys())}")
        
        if debug:
            print(f"[DEBUG] 搜索结果总数: {data.get('total_count', 0)}")
            print(f"[DEBUG] 返回的仓库数量: {len(data.get('items', []))}")
        
        # 7. 处理搜索结果
        repos = []
        for item in data.get("items", []):
            # 解析创建时间
            created_at_str = item.get("created_at")
            created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ")
            days_since_creation = (datetime.now() - created_at).days + 1
            
            # 计算新星指数（stars/天数）
            stars_per_day = item.get("stargazers_count", 0) / days_since_creation
            
            repo = {
                "name": item.get("full_name"),
                "owner": item.get("owner", {}).get("login"),
                "description": item.get("description", "暂无描述"),
                "stars": item.get("stargazers_count", 0),
                "forks": item.get("forks_count", 0),
                "language": item.get("language"),
                "url": item.get("html_url"),
                "homepage": item.get("homepage"),
                "created_at": item.get("created_at"),
                "updated_at": item.get("updated_at"),
                "pushed_at": item.get("pushed_at"),
                "topics": item.get("topics", []),
                "open_issues": item.get("open_issues_count", 0),
                "license": item.get("license", {}).get("name") if item.get("license") else None,
                "days_since_creation": days_since_creation,
                "stars_per_day": round(stars_per_day, 2),
                "is_mock": False
            }
            
            if debug:
                print(f"[DEBUG] 处理仓库: {repo['name']} - Stars: {repo['stars']}")
            
            # 质量评分
            repo["quality_score"] = calculate_quality_score(repo, min_stars)
            
            # 新星指数
            repo["rising_score"] = calculate_rising_score(repo)
            
            repos.append(repo)
        
        # 8. 处理强制包含的仓库
        if include_repos:
            for repo_name in include_repos:
                if not any(r["name"] == repo_name for r in repos):
                    # 直接调用API获取仓库详情
                    try:
                        repo_url = f"https://api.github.com/repos/{repo_name}"
                        repo_response = requests.get(repo_url, headers=headers, timeout=30)
                        
                        if repo_response.status_code == 200:
                            repo_data = repo_response.json()
                            
                            created_at = datetime.strptime(repo_data.get("created_at"), "%Y-%m-%dT%H:%M:%SZ")
                            days_since_creation = (datetime.now() - created_at).days + 1
                            stars_per_day = repo_data.get("stargazers_count", 0) / days_since_creation
                            
                            forced_repo = {
                                "name": repo_data.get("full_name"),
                                "owner": repo_data.get("owner", {}).get("login"),
                                "description": repo_data.get("description", "暂无描述"),
                                "stars": repo_data.get("stargazers_count", 0),
                                "forks": repo_data.get("forks_count", 0),
                                "language": repo_data.get("language"),
                                "url": repo_data.get("html_url"),
                                "homepage": repo_data.get("homepage"),
                                "created_at": repo_data.get("created_at"),
                                "updated_at": repo_data.get("updated_at"),
                                "pushed_at": repo_data.get("pushed_at"),
                                "topics": repo_data.get("topics", []),
                                "open_issues": repo_data.get("open_issues_count", 0),
                                "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                                "days_since_creation": days_since_creation,
                                "stars_per_day": round(stars_per_day, 2),
                                "is_mock": False
                            }
                            
                            forced_repo["quality_score"] = calculate_quality_score(forced_repo, min_stars)
                            forced_repo["rising_score"] = calculate_rising_score(forced_repo)
                            
                            repos.insert(0, forced_repo)
                            
                            if debug:
                                print(f"[DEBUG] 强制包含仓库: {repo_name} - Stars: {forced_repo['stars']}")
                    
                    except Exception as e:
                        if debug:
                            print(f"[DEBUG] 获取强制包含仓库失败 {repo_name}: {str(e)}")
        
        # 9. 根据模式排序
        if mode == "rising":
            repos.sort(key=lambda x: x["rising_score"], reverse=True)
        else:
            repos.sort(key=lambda x: x["stars"], reverse=True)
        
        # 10. 限制数量
        repos = repos[:limit]
        
        return repos
        
    except Exception as e:
        print(f"⚠️  请求GitHub API失败: {str(e)}")
        print("💡 自动切换到离线模式...")
        return search_ai_repos(focus_area, min_stars, limit, period, mode, include_repos, debug, offline=True)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="获取AI领域生产级GitHub仓库")
    parser.add_argument("--focus", type=str, default="", help="聚焦领域（LLM/CV/NLP等）")
    parser.add_argument("--min-stars", type=int, default=1000, help="最小stars数")
    parser.add_argument("--limit", type=int, default=10, help="返回数量限制")
    parser.add_argument("--period", type=str, default="monthly", 
                        choices=["daily", "weekly", "monthly", "quarterly"], 
                        help="时间周期")
    parser.add_argument("--mode", type=str, default="rising", 
                        choices=["new", "rising"], 
                        help="模式（new=新创建，rising=增长最快）")
    parser.add_argument("--include", type=str, nargs="*", help="强制包含的仓库列表")
    parser.add_argument("--debug", action="store_true", help="显示调试信息")
    parser.add_argument("--offline", action="store_true", help="使用离线模式（模拟数据）")
    
    args = parser.parse_args()
    
    # 调用搜索函数
    repos = search_ai_repos(
        focus_area=args.focus,
        min_stars=args.min_stars,
        limit=args.limit,
        period=args.period,
        mode=args.mode,
        include_repos=args.include,
        debug=args.debug,
        offline=args.offline
    )
    
    # 输出结果
    print(f"\n{'='*80}")
    print(f"发现 {len(repos)} 个高质量AI仓库")
    print(f"{'='*80}\n")
    
    for idx, repo in enumerate(repos, 1):
        print(f"{idx}. {repo['name']}")
        print(f"   ⭐ {repo['stars']} stars | 🍴 {repo['forks']} forks")
        print(f"   📝 {repo['description']}")
        print(f"   🔗 {repo['url']}")
        print(f"   📊 质量分: {repo['quality_score']}/100 | 🚀 新星指数: {repo['rising_score']}/100")
        if repo.get("is_mock"):
            print(f"   ⚠️  [模拟数据]")
        print()


if __name__ == "__main__":
    main()
