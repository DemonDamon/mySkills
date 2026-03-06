#!/usr/bin/env python3
"""
检查GitHub API状态和配额

用途：
1. 检查GitHub API是否可用
2. 查看API速率限制（rate limit）
3. 验证Token是否有效
"""

import os
import sys
from coze_workload_identity import requests


def check_github_api():
    """
    检查GitHub API状态
    """
    # 获取凭证
    skill_id = "7613777400777867298"
    token = os.getenv("COZE_GITHUB_API_7613777400777867298")
    
    headers = {
        "User-Agent": "AI-Project-Hunter"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
        print(f"✅ 已配置GitHub API Token")
    else:
        print(f"⚠️  未配置GitHub API Token")
        print(f"💡 将使用匿名访问（限制：60次/小时）")
    
    print(f"\n{'='*60}")
    print(f"检查GitHub API状态...")
    print(f"{'='*60}\n")
    
    # 检查API端点
    try:
        response = requests.get("https://api.github.com", headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"✅ GitHub API 可访问")
        else:
            print(f"❌ GitHub API 状态异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到GitHub API: {str(e)}")
        return False
    
    # 检查速率限制
    try:
        response = requests.get("https://api.github.com/rate_limit", headers=headers, timeout=10)
        if response.status_code == 200:
            rate_data = response.json()
            
            print(f"\n📊 API速率限制:")
            print(f"{'='*60}")
            
            # Core API限制
            core = rate_data.get("resources", {}).get("core", {})
            print(f"Core API:")
            print(f"  - 限制: {core.get('limit', 'N/A')} 次/小时")
            print(f"  - 剩余: {core.get('remaining', 'N/A')} 次")
            print(f"  - 重置时间: {core.get('reset', 'N/A')}")
            
            # Search API限制
            search = rate_data.get("resources", {}).get("search", {})
            print(f"\nSearch API:")
            print(f"  - 限制: {search.get('limit', 'N/A')} 次/分钟")
            print(f"  - 剩余: {search.get('remaining', 'N/A')} 次")
            print(f"  - 重置时间: {search.get('reset', 'N/A')}")
            
            # 警告
            if core.get('remaining', 0) < 100:
                print(f"\n⚠️  警告: Core API剩余配额不足（<100次）")
            if search.get('remaining', 0) < 10:
                print(f"⚠️  警告: Search API剩余配额不足（<10次）")
            
        else:
            print(f"❌ 无法获取速率限制信息: {response.status_code}")
    except Exception as e:
        print(f"❌ 检查速率限制失败: {str(e)}")
    
    # 测试搜索API
    print(f"\n{'='*60}")
    print(f"测试搜索API...")
    print(f"{'='*60}\n")
    
    try:
        search_url = "https://api.github.com/search/repositories"
        params = {
            "q": "stars:>1000 language:python",
            "per_page": 1
        }
        response = requests.get(search_url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            total_count = data.get("total_count", 0)
            print(f"✅ 搜索API正常工作")
            print(f"📝 测试搜索 'stars:>1000 language:python' 找到 {total_count} 个仓库")
        elif response.status_code == 403:
            print(f"❌ 搜索API被限制（速率限制或IP限制）")
        else:
            print(f"❌ 搜索API错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 测试搜索API失败: {str(e)}")
    
    # 检查用户信息（如果有Token）
    if token:
        print(f"\n{'='*60}")
        print(f"检查Token信息...")
        print(f"{'='*60}\n")
        
        try:
            response = requests.get("https://api.github.com/user", headers=headers, timeout=10)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Token有效")
                print(f"👤 用户: {user_data.get('login', 'N/A')}")
                print(f"📧 Email: {user_data.get('email', 'N/A') or '未公开'}")
                print(f"🏢 组织: {', '.join([org['login'] for org in user_data.get('organizations', [])[:3]])}")
            elif response.status_code == 401:
                print(f"❌ Token无效或已过期")
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 检查Token失败: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"检查完成")
    print(f"{'='*60}\n")
    
    return True


if __name__ == "__main__":
    check_github_api()
