#!/usr/bin/env python3
"""
克隆并运行GitHub项目代码

依赖: gitpython
安全注意: 此脚本会执行远程代码，仅用于可信项目！

使用前必须征得用户明确同意
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
from git import Repo
import re


# 危险命令黑名单（禁止执行）
DANGEROUS_COMMANDS = [
    "rm -rf /",
    "dd if=",
    ":(){:|:&};:",
    "mkfs.",
    "chmod 777 /",
    "chown root",
    "wget http",
    "curl http",
]


def is_command_safe(command: str) -> bool:
    """
    检查命令是否安全
    
    Args:
        command: 要执行的命令
    
    Returns:
        bool: 是否安全
    """
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command.lower():
            return False
    return True


def clone_repo(repo_url: str, workdir: str):
    """
    克隆GitHub仓库
    
    Args:
        repo_url: 仓库URL
        workdir: 工作目录
    
    Returns:
        str: 仓库本地路径
    """
    # 解析仓库信息
    if not repo_url.startswith("https://github.com/"):
        raise ValueError("仅支持GitHub仓库")
    
    repo_name = repo_url.rstrip('/').split('/')[-1]
    repo_path = os.path.join(workdir, repo_name)
    
    # 如果已存在，先删除
    if os.path.exists(repo_path):
        print(f"⚠️  仓库已存在，正在删除: {repo_path}")
        shutil.rmtree(repo_path)
    
    # 克隆仓库
    print(f"正在克隆仓库: {repo_url}")
    print(f"目标路径: {repo_path}")
    
    try:
        Repo.clone_from(repo_url, repo_path)
        print(f"✅ 克隆成功")
        return repo_path
    except Exception as e:
        raise Exception(f"克隆失败: {str(e)}")


def extract_install_commands(readme_path: str) -> list:
    """
    从README中提取安装命令
    
    Args:
        readme_path: README文件路径
    
    Returns:
        list: 安装命令列表
    """
    commands = []
    
    if not os.path.exists(readme_path):
        return commands
    
    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 常见安装命令模式
    patterns = [
        r'```bash\s*\n(.*?)```',  # bash代码块
        r'```sh\s*\n(.*?)```',    # sh代码块
        r'```shell\s*\n(.*?)```', # shell代码块
        r'```\s*\n(.*?pip install.*?)```',  # pip install
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for match in matches:
            lines = match.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('$'):
                    # 检查是否是安装命令
                    if any(keyword in line for keyword in ['pip install', 'npm install', 'yarn add', 'conda install']):
                        commands.append(line)
    
    return commands[:5]  # 限制数量


def extract_run_commands(readme_path: str) -> list:
    """
    从README中提取运行命令
    
    Args:
        readme_path: README文件路径
    
    Returns:
        list: 运行命令列表
    """
    commands = []
    
    if not os.path.exists(readme_path):
        return commands
    
    with open(readme_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 查找包含"Usage"、"Run"、"Example"、"Demo"的代码块
    usage_section = re.search(
        r'(?:##|#) .*?(?:Usage|Run|Example|Demo|Quick Start).*?\n(.*?)(?=\n##|#)',
        content,
        re.IGNORECASE | re.DOTALL
    )
    
    if usage_section:
        section_content = usage_section.group(1)
        code_blocks = re.findall(r'```(?:bash|sh|shell|python)?\s*\n(.*?)```', section_content, re.DOTALL)
        
        for block in code_blocks:
            lines = block.strip().split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('$'):
                    commands.append(line)
    
    return commands[:3]  # 限制数量


def run_command(command: str, workdir: str, timeout: int = 60):
    """
    执行命令并捕获输出
    
    Args:
        command: 要执行的命令
        workdir: 工作目录
        timeout: 超时时间（秒）
    
    Returns:
        dict: 包含stdout、stderr、return_code
    """
    if not is_command_safe(command):
        raise Exception(f"⚠️  命令可能不安全，已拒绝执行: {command}")
    
    print(f"\n执行命令: {command}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        output = {
            "command": command,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        }
        
        if result.returncode == 0:
            print(f"✅ 执行成功")
        else:
            print(f"❌ 执行失败 (退出码: {result.returncode})")
        
        return output
        
    except subprocess.TimeoutExpired:
        raise Exception(f"⏱️  命令执行超时: {command}")
    except Exception as e:
        raise Exception(f"❌ 命令执行失败: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="克隆并运行GitHub项目代码")
    parser.add_argument("--repo", "-r", required=True, help="仓库URL（如 https://github.com/owner/repo）")
    parser.add_argument("--workdir", "-w", default="./temp_repos", help="工作目录（默认：./temp_repos）")
    parser.add_argument("--run-demo", action="store_true", help="运行示例代码")
    parser.add_argument("--install", action="store_true", help="自动安装依赖")
    parser.add_argument("--yes", "-y", action="store_true", help="跳过确认（仅用于可信项目）")
    
    args = parser.parse_args()
    
    # 安全警告
    if not args.yes:
        print("\n" + "="*80)
        print("⚠️  安全警告")
        print("="*80)
        print(f"即将执行来自 {args.repo} 的代码")
        print("这可能会带来安全风险！")
        print("\n请确保:")
        print("  1. 你信任这个仓库")
        print("  2. 仓库来自可信的作者")
        print("  3. 你了解将要执行的命令")
        print("\n继续执行吗？(yes/no): ", end="")
        
        response = input().strip().lower()
        if response not in ['yes', 'y']:
            print("❌ 已取消操作")
            sys.exit(0)
    
    try:
        # 创建工作目录
        os.makedirs(args.workdir, exist_ok=True)
        
        # 克隆仓库
        repo_path = clone_repo(args.repo, args.workdir)
        
        # 查找README
        readme_path = None
        for filename in ['README.md', 'README.rst', 'readme.md']:
            potential_path = os.path.join(repo_path, filename)
            if os.path.exists(potential_path):
                readme_path = potential_path
                break
        
        if not readme_path:
            print("⚠️  未找到README文件")
        else:
            print(f"✅ 找到README: {readme_path}")
            
            # 提取安装命令
            install_commands = extract_install_commands(readme_path)
            if install_commands:
                print(f"\n📦 检测到 {len(install_commands)} 个安装命令:")
                for cmd in install_commands:
                    print(f"   - {cmd}")
                
                if args.install or args.yes:
                    for cmd in install_commands:
                        result = run_command(cmd, repo_path)
                        if not result['success']:
                            print(f"⚠️  安装命令执行失败，继续...")
            
            # 提取运行命令
            run_commands = extract_run_commands(readme_path)
            if run_commands:
                print(f"\n🚀 检测到 {len(run_commands)} 个运行命令:")
                for cmd in run_commands:
                    print(f"   - {cmd}")
                
                if args.run_demo:
                    for cmd in run_commands:
                        result = run_command(cmd, repo_path, timeout=120)
                        print(f"\n输出:\n{result['stdout']}")
                        if result['stderr']:
                            print(f"错误:\n{result['stderr']}")
        
        print(f"\n✅ 仓库已克隆到: {repo_path}")
        print(f"💡 你可以手动进入目录探索: cd {repo_path}")
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
