#!/usr/bin/env python3
"""
提取GitHub仓库详细信息并进行深度分析（AI项目专用）

授权方式: ApiKey
凭证Key: COZE_GITHUB_API_7613777400777867298
"""

import os
import argparse
import json
import sys
import re
from datetime import datetime, timedelta, timezone
from coze_workload_identity import requests


def format_time(iso_time: str) -> str:
    """
    将ISO 8601时间格式转换为易读格式
    
    Args:
        iso_time: ISO 8601格式的时间字符串
    
    Returns:
        str: 格式化的时间字符串
    """
    try:
        # 解析ISO 8601时间（假设是UTC）
        dt = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ")
        # 转换为本地时区
        dt_local = dt.replace(tzinfo=timezone.utc).astimezone()
        # 格式化为中文习惯
        return dt_local.strftime("%Y年%m月%d日 %H:%M")
    except:
        return iso_time


def get_relative_time(iso_time: str) -> str:
    """
    计算相对时间（如"2天前"、"本周"等）
    
    Args:
        iso_time: ISO 8601格式的时间字符串
    
    Returns:
        str: 相对时间描述
    """
    try:
        # 解析时间
        dt = datetime.strptime(iso_time, "%Y-%m-%dT%H:%M:%SZ")
        dt = dt.replace(tzinfo=timezone.utc).astimezone()
        
        # 计算时间差
        now = datetime.now(timezone.utc).astimezone()
        delta = now - dt
        
        days = delta.days
        hours = delta.seconds // 3600
        
        # 小于1小时
        if days == 0 and hours < 1:
            minutes = delta.seconds // 60
            return f"{minutes}分钟前"
        # 小于1天
        elif days == 0:
            return f"{hours}小时前"
        # 1-7天
        elif days <= 7:
            if days == 1:
                return "昨天"
            elif days <= 3:
                return f"{days}天前"
            else:
                return "本周"
        # 8-30天
        elif days <= 30:
            weeks = days // 7
            if weeks == 1:
                return "上周"
            elif weeks <= 3:
                return f"{weeks}周前"
            else:
                return "本月"
        # 31-90天
        elif days <= 90:
            months = days // 30
            if months == 1:
                return "上个月"
            else:
                return f"{months}个月前"
        # 更久
        else:
            return dt.strftime("%Y-%m-%d")
    except:
        return iso_time


def extract_repo_info(repo_full_name: str):
    """
    提取仓库详细信息并进行深度分析
    
    Args:
        repo_full_name: 仓库全名（格式：owner/repo）
    
    Returns:
        dict: 包含仓库元数据和深度分析结果的字典
    """
    # 1. 获取凭证
    skill_id = "7613777400777867298"
    token = os.getenv("COZE_GITHUB_API_7613777400777867298")
    if not token:
        raise ValueError("缺少GitHub API Token配置，请检查凭证")
    
    # 2. 构建请求头
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "AI-Project-Hunter"
    }
    
    try:
        # 3. 获取仓库基本信息
        repo_url = f"https://api.github.com/repos/{repo_full_name}"
        response = requests.get(repo_url, headers=headers, timeout=30)
        
        if response.status_code >= 400:
            raise Exception(f"获取仓库信息失败: 状态码 {response.status_code}, 响应: {response.text}")
        
        repo_data = response.json()
        
        # 4. 获取README内容
        readme_url = f"https://api.github.com/repos/{repo_full_name}/readme"
        readme_response = requests.get(readme_url, headers=headers, timeout=30)
        
        readme_content = ""
        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            import base64
            readme_content = base64.b64decode(readme_data.get("content", "")).decode('utf-8', errors='ignore')
        
        # 5. 获取语言统计
        languages_url = f"https://api.github.com/repos/{repo_full_name}/languages"
        languages_response = requests.get(languages_url, headers=headers, timeout=30)
        languages_data = {}
        if languages_response.status_code == 200:
            languages_data = languages_response.json()
        
        # 6. 获取最近的提交（分析活跃度）
        commits_url = f"https://api.github.com/repos/{repo_full_name}/commits?per_page=5"
        commits_response = requests.get(commits_url, headers=headers, timeout=30)
        recent_commits = []
        if commits_response.status_code == 200:
            recent_commits = commits_response.json()
        
        # 7. 构建完整信息
        info = {
            "basic": {
                "name": repo_data.get("full_name"),
                "owner": repo_data.get("owner", {}).get("login"),
                "description": repo_data.get("description", "暂无描述"),
                "url": repo_data.get("html_url"),
                "stars": repo_data.get("stargazers_count", 0),
                "forks": repo_data.get("forks_count", 0),
                "watchers": repo_data.get("watchers_count", 0),
                "language": repo_data.get("language"),
                "languages": languages_data,
                "created_at": repo_data.get("created_at"),
                "updated_at": repo_data.get("updated_at"),
                "pushed_at": repo_data.get("pushed_at"),
                "open_issues": repo_data.get("open_issues_count", 0),
                "closed_issues": repo_data.get("open_issues_count", 0),  # 需要单独API
                "license": repo_data.get("license", {}).get("name") if repo_data.get("license") else None,
                "topics": repo_data.get("topics", []),
                "homepage": repo_data.get("homepage"),
                "size_kb": repo_data.get("size", 0),
                "archived": repo_data.get("archived", False)
            },
            "readme": {
                "raw": readme_content,
                "extracted": extract_readme_sections(readme_content),
                "has_quickstart": "Quick Start" in readme_content or "quickstart" in readme_content.lower(),
                "has_examples": "Example" in readme_content or "example" in readme_content.lower(),
                "has_api_docs": "API" in readme_content or "api" in readme_content.lower()
            },
            "activity": analyze_activity(recent_commits, repo_data.get("updated_at")),
            "quality": evaluate_quality(repo_data, readme_content, languages_data),
            "tech_stack": analyze_tech_stack(readme_content, languages_data),
            "production_readiness": evaluate_production_readiness(repo_data, readme_content)
        }
        
        return info
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"GitHub API调用失败: {str(e)}")


def extract_readme_sections(readme: str):
    """
    从README中提取关键章节
    """
    sections = {
        "features": "",
        "installation": "",
        "usage": "",
        "architecture": "",
        "api": "",
        "screenshots": [],
        "examples": "",
        "badges": [],
        "model_info": {}  # AI项目特有：模型信息
    }
    
    # 提取badges
    badge_pattern = r'!\[.*?\]\(https?://[^\)]+\)'
    badges = re.findall(badge_pattern, readme[:2000])
    sections["badges"] = badges[:10]
    
    # 提取模型信息（AI项目特有）
    model_patterns = [
        r'(?:model|Model).*?:\s*([A-Za-z0-9\-_]+)',
        r'pre-trained\s+model\s*:?\s*([A-Za-z0-9\-_]+)',
        r'base\s+model\s*:?\s*([A-Za-z0-9\-_]+)'
    ]
    for pattern in model_patterns:
        matches = re.findall(pattern, readme, re.IGNORECASE)
        if matches:
            sections["model_info"]["models"] = list(set(matches))
    
    # 提取架构图相关
    if "architecture" in readme.lower():
        arch_match = re.search(r'(?:##|#)\s*Architecture\s*\n(.*?)(?=\n##|#)', readme, re.IGNORECASE | re.DOTALL)
        if arch_match:
            sections["architecture"] = arch_match.group(1).strip()
    
    # 其他章节提取
    feature_patterns = [
        r'(?:##|#)\s*Features?\s*\n(.*?)(?=\n##|#)',
        r'(?:##|#)\s*特性\s*\n(.*?)(?=\n##|#)'
    ]
    for pattern in feature_patterns:
        match = re.search(pattern, readme, re.IGNORECASE | re.DOTALL)
        if match:
            sections["features"] = match.group(1).strip()
            break
    
    install_patterns = [
        r'(?:##|#)\s*Installation?\s*\n(.*?)(?=\n##|#)',
        r'(?:##|#)\s*Install\s*\n(.*?)(?=\n##|#)',
        r'(?:##|#)\s*Getting Started\s*\n(.*?)(?=\n##|#)'
    ]
    for pattern in install_patterns:
        match = re.search(pattern, readme, re.IGNORECASE | re.DOTALL)
        if match:
            sections["installation"] = match.group(1).strip()
            break
    
    # 提取截图
    screenshot_patterns = [
        r'!\[.*?screenshot.*?\]\((https?://[^\)]+)\)',
        r'!\[.*?demo.*?\]\((https?://[^\)]+\.(png|jpg|gif|webp))',
    ]
    screenshots = set()
    for pattern in screenshot_patterns:
        matches = re.findall(pattern, readme, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                screenshots.add(match[0])
            else:
                screenshots.add(match)
    sections["screenshots"] = list(screenshots)[:8]
    
    return sections


def analyze_activity(commits: list, updated_at: str):
    """
    分析项目活跃度
    """
    if not commits:
        return {"active": False, "score": 0}
    
    now = datetime.now()
    last_commit = datetime.strptime(commits[0]["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
    days_since_last = (now - last_commit).days
    
    # 计算活跃度评分
    score = 0
    if days_since_last <= 7:
        score += 40
    elif days_since_last <= 30:
        score += 30
    elif days_since_last <= 90:
        score += 20
    elif days_since_last <= 180:
        score += 10
    
    # 提交频率
    if len(commits) >= 5:
        score += 20
    elif len(commits) >= 3:
        score += 10
    
    return {
        "active": days_since_last <= 90,
        "days_since_last_commit": days_since_last,
        "recent_commits_count": len(commits),
        "activity_score": score
    }


def evaluate_quality(repo_data: dict, readme: str, languages: dict):
    """
    评估代码质量
    """
    score = 0
    factors = []
    
    # 1. 文档完整性（30分）
    doc_score = 0
    if readme and len(readme) > 500:
        doc_score += 10
        factors.append("有详细README")
    if "Installation" in readme or "install" in readme.lower():
        doc_score += 10
        factors.append("有安装说明")
    if "Example" in readme or "example" in readme.lower():
        doc_score += 10
        factors.append("有使用示例")
    score += doc_score
    
    # 2. 代码组织（20分）
    if languages and len(languages) >= 2:
        score += 10
        factors.append("多语言项目")
    if repo_data.get("license"):
        score += 10
        factors.append("有开源协议")
    
    # 3. 测试覆盖（20分）
    if "test" in readme.lower() or "Test" in readme:
        score += 10
        factors.append("提到测试")
    if "CI/CD" in readme or "workflow" in readme.lower():
        score += 10
        factors.append("有CI/CD配置")
    
    # 4. 社区质量（30分）
    issues = repo_data.get("open_issues_count", 0)
    if issues > 0 and issues < 50:
        score += 15
        factors.append("适中的Issue数量")
    elif issues >= 50:
        score += 5
        factors.append("Issue较多（可能说明活跃）")
    
    if repo_data.get("forks_count", 0) > repo_data.get("stargazers_count", 0) * 0.1:
        score += 15
        factors.append("有较多Fork")
    
    return {
        "score": score,
        "max_score": 100,
        "factors": factors,
        "grade": get_grade(score)
    }


def evaluate_production_readiness(repo_data: dict, readme: str):
    """
    评估生产就绪度
    """
    score = 0
    checks = []
    
    # 1. 稳定性指标（30分）
    stars = repo_data.get("stargazers_count", 0)
    if stars >= 10000:
        score += 30
        checks.append("高Stars数（>10k）")
    elif stars >= 5000:
        score += 25
        checks.append("较高Stars数（>5k）")
    elif stars >= 1000:
        score += 20
        checks.append("中等Stars数（>1k）")
    
    # 2. 维护活跃度（25分）
    updated_at = datetime.strptime(repo_data.get("updated_at"), "%Y-%m-%dT%H:%M:%SZ")
    days_since_update = (datetime.now() - updated_at).days
    if days_since_update <= 30:
        score += 25
        checks.append("近期活跃更新")
    elif days_since_update <= 90:
        score += 20
        checks.append("近三个月有更新")
    elif days_since_update <= 180:
        score += 10
        checks.append("半年内有更新")
    
    # 3. 文档完善度（25分）
    if "API" in readme or "api" in readme.lower():
        score += 10
        checks.append("有API文档")
    if "deployment" in readme.lower() or "deploy" in readme.lower():
        score += 10
        checks.append("有部署说明")
    if "production" in readme.lower():
        score += 5
        checks.append("提到生产环境")
    
    # 4. 测试和监控（20分）
    if "test" in readme.lower() and "coverage" in readme.lower():
        score += 10
        checks.append("有测试覆盖率")
    if "monitoring" in readme.lower() or "logging" in readme.lower():
        score += 10
        checks.append("有监控/日志说明")
    
    # 计算就绪度等级
    if score >= 80:
        level = "生产就绪"
    elif score >= 60:
        level = "接近就绪"
    elif score >= 40:
        level = "可用于测试"
    else:
        level = "仅用于研究"
    
    return {
        "score": score,
        "level": level,
        "checks": checks
    }


def analyze_tech_stack(readme: str, languages: dict):
    """
    分析技术栈
    """
    tech_stack = {
        "languages": languages,
        "frameworks": [],
        "libraries": [],
        "tools": []
    }
    
    # 常见框架和库关键词
    framework_patterns = {
        "pytorch": ["pytorch", "torch"],
        "tensorflow": ["tensorflow", "keras"],
        "fastapi": ["fastapi"],
        "flask": ["flask"],
        "django": ["django"],
        "react": ["react", "reactjs"],
        "vue": ["vue", "vuejs"],
        "transformers": ["transformers", "huggingface"],
        "langchain": ["langchain"],
    }
    
    readme_lower = readme.lower()
    for framework, keywords in framework_patterns.items():
        if any(keyword in readme_lower for keyword in keywords):
            tech_stack["frameworks"].append(framework)
    
    return tech_stack


def get_grade(score: int) -> str:
    """获取等级"""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    else:
        return "D"


def display_repo_info(info: dict):
    """
    格式化显示仓库深度分析信息
    """
    basic = info["basic"]
    readme = info["readme"]
    activity = info["activity"]
    quality = info["quality"]
    production = info["production_readiness"]
    
    print(f"\n{'='*80}")
    print(f"📦 仓库: {basic['name']}")
    print(f"{'='*80}\n")
    
    print(f"📝 描述: {basic['description']}")
    print(f"🔗 链接: {basic['url']}")
    if basic.get('homepage'):
        print(f"🌐 官网: {basic['homepage']}")
    
    print(f"\n📊 基本指标:")
    print(f"   ⭐ Stars: {basic['stars']:,}")
    print(f"   🍴 Forks: {basic['forks']:,}")
    print(f"   👀 Watchers: {basic['watchers']:,}")
    print(f"   🐛 Open Issues: {basic['open_issues']:,}")
    print(f"   💻 主要语言: {basic['language']}")
    if basic['license']:
        print(f"   📄 许可证: {basic['license']}")
    
    print(f"\n📅 时间信息:")
    print(f"   创建时间: {format_time(basic['created_at'])} ({get_relative_time(basic['created_at'])})")
    print(f"   最后更新: {format_time(basic['updated_at'])} ({get_relative_time(basic['updated_at'])})")
    print(f"   最后推送: {format_time(basic['pushed_at'])} ({get_relative_time(basic['pushed_at'])})")
    
    print(f"\n🎯 活跃度分析:")
    print(f"   活跃状态: {'✅ 活跃' if activity['active'] else '❌ 不活跃'}")
    print(f"   距离上次提交: {activity['days_since_last_commit']} 天")
    print(f"   近期提交数: {activity['recent_commits_count']}")
    print(f"   活跃度评分: {activity['activity_score']}/100")
    
    print(f"\n✨ 代码质量评估:")
    print(f"   质量评分: {quality['score']}/{quality['max_score']} ({quality['grade']})")
    print(f"   评估因素:")
    for factor in quality['factors']:
        print(f"      - {factor}")
    
    print(f"\n🚀 生产就绪度:")
    print(f"   评分: {production['score']}/100")
    print(f"   等级: {production['level']}")
    print(f"   检查项:")
    for check in production['checks']:
        print(f"      - {check}")
    
    print(f"\n💻 技术栈:")
    print(f"   语言: {', '.join(basic['languages'].keys()) if basic['languages'] else 'N/A'}")
    if info['tech_stack']['frameworks']:
        print(f"   框架: {', '.join(info['tech_stack']['frameworks'])}")
    
    if readme['extracted']['features']:
        print(f"\n🎯 核心功能:")
        print(f"   {readme['extracted']['features'][:500]}")
    
    if readme['extracted']['installation']:
        print(f"\n📦 安装方式:")
        print(f"   {readme['extracted']['installation'][:500]}")
    
    if readme['extracted']['screenshots']:
        print(f"\n🖼️  截图:")
        for url in readme['extracted']['screenshots'][:3]:
            print(f"   - {url}")
    
    print(f"\n{'='*80}\n")


def main():
    parser = argparse.ArgumentParser(description="提取GitHub仓库详细信息并进行深度分析")
    parser.add_argument("--repo", "-r", required=True, help="仓库全名（格式：owner/repo）")
    parser.add_argument("--output", "-o", help="输出到JSON文件")
    
    args = parser.parse_args()
    
    try:
        info = extract_repo_info(args.repo)
        
        display_repo_info(info)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到 {args.output}")
        
        return info
        
    except Exception as e:
        print(f"❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
