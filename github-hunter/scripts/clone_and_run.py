#!/usr/bin/env python3
"""
克隆GitHub仓库并运行示例代码

用途：
1. 克隆GitHub仓库到本地
2. 智能识别编程语言和依赖
3. 安装依赖
4. 查找示例代码
5. 运行示例并记录输出
"""

import argparse
import os
import subprocess
import json
import shutil
import sys
from pathlib import Path
from datetime import datetime

# 自动设置路径：将技能根目录添加到 sys.path
skill_root = Path(__file__).parent.parent
if str(skill_root) not in sys.path:
    sys.path.insert(0, str(skill_root))


def clone_repo(repo_url: str, work_dir: str = "./repos") -> str:
    """
    克隆GitHub仓库
    
    Args:
        repo_url: 仓库URL（如 https://github.com/owner/repo）
        work_dir: 工作目录
    
    Returns:
        str: 克隆后的目录路径
    """
    # 提取仓库名称
    repo_name = repo_url.rstrip('/').split('/')[-1]
    owner = repo_url.rstrip('/').split('/')[-2]
    full_name = f"{owner}/{repo_name}"
    
    # 创建目标目录
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    
    clone_dir = work_dir / repo_name
    
    # 如果已存在，删除重新克隆
    if clone_dir.exists():
        print(f"🗑️  删除已存在的目录: {clone_dir}")
        shutil.rmtree(clone_dir)
    
    # 克隆仓库
    print(f"📥 正在克隆仓库: {full_name}")
    clone_url = f"https://github.com/{full_name}.git"
    
    try:
        result = subprocess.run(
            ["git", "clone", clone_url, str(clone_dir)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode != 0:
            print(f"❌ 克隆失败: {result.stderr}")
            return None
        
        print(f"✅ 克隆成功: {clone_dir}")
        return str(clone_dir)
        
    except subprocess.TimeoutExpired:
        print(f"❌ 克隆超时")
        return None
    except Exception as e:
        print(f"❌ 克隆失败: {str(e)}")
        return None


def detect_language(repo_dir: str) -> dict:
    """
    检测仓库的编程语言
    
    Args:
        repo_dir: 仓库目录
    
    Returns:
        dict: 语言信息
    """
    repo_dir = Path(repo_dir)
    language_info = {
        "detected": False,
        "language": "",
        "package_manager": "",
        "install_command": "",
        "run_command": ""
    }
    
    # Python
    if (repo_dir / "requirements.txt").exists():
        language_info.update({
            "detected": True,
            "language": "Python",
            "package_manager": "pip",
            "install_command": "pip install -r requirements.txt"
        })
    elif (repo_dir / "setup.py").exists() or (repo_dir / "pyproject.toml").exists():
        language_info.update({
            "detected": True,
            "language": "Python",
            "package_manager": "pip",
            "install_command": "pip install -e ."
        })
    
    # Node.js
    elif (repo_dir / "package.json").exists():
        language_info.update({
            "detected": True,
            "language": "JavaScript/TypeScript",
            "package_manager": "npm",
            "install_command": "npm install"
        })
    
    # Go
    elif (repo_dir / "go.mod").exists():
        language_info.update({
            "detected": True,
            "language": "Go",
            "package_manager": "go",
            "install_command": "go mod download"
        })
    
    # Rust
    elif (repo_dir / "Cargo.toml").exists():
        language_info.update({
            "detected": True,
            "language": "Rust",
            "package_manager": "cargo",
            "install_command": "cargo build"
        })
    
    return language_info


def find_examples(repo_dir: str) -> list:
    """
    查找示例代码文件
    
    Args:
        repo_dir: 仓库目录
    
    Returns:
        list: 示例文件列表
    """
    repo_dir = Path(repo_dir)
    examples = []
    
    # 查找examples目录
    examples_dir = repo_dir / "examples"
    if examples_dir.exists():
        for file in examples_dir.rglob("*.py"):
            examples.append(str(file.relative_to(repo_dir)))
    
    # 查找demo目录
    demo_dir = repo_dir / "demo"
    if demo_dir.exists():
        for file in demo_dir.rglob("*.py"):
            examples.append(str(file.relative_to(repo_dir)))
    
    # 查找test目录
    test_dir = repo_dir / "tests"
    if test_dir.exists():
        for file in test_dir.rglob("*.py"):
            if "example" in file.name.lower() or "demo" in file.name.lower():
                examples.append(str(file.relative_to(repo_dir)))
    
    return examples


def install_dependencies(repo_dir: str, install_command: str) -> dict:
    """
    安装依赖
    
    Args:
        repo_dir: 仓库目录
        install_command: 安装命令
    
    Returns:
        dict: 安装结果
    """
    print(f"📦 正在安装依赖...")
    print(f"   命令: {install_command}")
    
    result = {
        "success": False,
        "output": "",
        "error": ""
    }
    
    try:
        process = subprocess.run(
            install_command,
            shell=True,
            cwd=repo_dir,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        result["output"] = process.stdout
        result["error"] = process.stderr
        result["success"] = process.returncode == 0
        
        if result["success"]:
            print(f"✅ 依赖安装成功")
        else:
            print(f"❌ 依赖安装失败")
            print(f"   错误: {result['error'][:200]}")
        
    except subprocess.TimeoutExpired:
        result["error"] = "安装超时"
        print(f"❌ 安装超时")
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ 安装失败: {str(e)}")
    
    return result


def run_example(repo_dir: str, example_file: str) -> dict:
    """
    运行示例代码
    
    Args:
        repo_dir: 仓库目录
        example_file: 示例文件路径（相对于仓库根目录）
    
    Returns:
        dict: 运行结果
    """
    print(f"🚀 正在运行示例: {example_file}")
    
    repo_dir = Path(repo_dir)
    example_path = repo_dir / example_file
    
    if not example_path.exists():
        return {
            "success": False,
            "error": f"文件不存在: {example_file}"
        }
    
    result = {
        "success": False,
        "output": "",
        "error": "",
        "duration": 0
    }
    
    try:
        start_time = datetime.now()
        
        # 运行Python脚本
        process = subprocess.run(
            ["python", str(example_path)],
            cwd=str(repo_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        end_time = datetime.now()
        result["duration"] = (end_time - start_time).total_seconds()
        result["output"] = process.stdout
        result["error"] = process.stderr
        result["success"] = process.returncode == 0
        
        if result["success"]:
            print(f"✅ 运行成功 (耗时: {result['duration']:.2f}s)")
            if result["output"]:
                print(f"   输出: {result['output'][:200]}...")
        else:
            print(f"❌ 运行失败")
            if result["error"]:
                print(f"   错误: {result['error'][:200]}...")
        
    except subprocess.TimeoutExpired:
        result["error"] = "运行超时"
        print(f"❌ 运行超时")
    except Exception as e:
        result["error"] = str(e)
        print(f"❌ 运行失败: {str(e)}")
    
    return result


def clone_and_run(repo_url: str, work_dir: str = "./repos", max_examples: int = 1) -> dict:
    """
    克隆并运行仓库
    
    Args:
        repo_url: 仓库URL
        work_dir: 工作目录
        max_examples: 最多运行几个示例
    
    Returns:
        dict: 完整的运行结果
    """
    print(f"\n{'='*60}")
    print(f"开始处理仓库: {repo_url}")
    print(f"{'='*60}\n")
    
    result = {
        "repo_url": repo_url,
        "repo_name": repo_url.rstrip('/').split('/')[-1],
        "cloned": False,
        "clone_dir": "",
        "language": {},
        "dependencies_installed": False,
        "examples_found": [],
        "examples_run": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 1. 克隆仓库
    clone_dir = clone_repo(repo_url, work_dir)
    if not clone_dir:
        return result
    
    result["cloned"] = True
    result["clone_dir"] = clone_dir
    
    # 2. 检测语言
    language_info = detect_language(clone_dir)
    result["language"] = language_info
    
    if not language_info["detected"]:
        print(f"⚠️  无法检测到编程语言，跳过依赖安装和代码运行")
        return result
    
    print(f"\n🔍 检测到语言: {language_info['language']}")
    print(f"📦 包管理器: {language_info['package_manager']}")
    
    # 3. 安装依赖
    if language_info["install_command"]:
        install_result = install_dependencies(clone_dir, language_info["install_command"])
        result["dependencies_installed"] = install_result["success"]
        
        if not install_result["success"]:
            print(f"⚠️  依赖安装失败，跳过代码运行")
            return result
    else:
        result["dependencies_installed"] = True
    
    # 4. 查找示例
    examples = find_examples(clone_dir)
    result["examples_found"] = examples
    
    if not examples:
        print(f"⚠️  未找到示例代码")
        return result
    
    print(f"\n📝 找到 {len(examples)} 个示例文件:")
    for ex in examples[:5]:
        print(f"   - {ex}")
    
    # 5. 运行示例
    print(f"\n🚀 开始运行示例（最多 {max_examples} 个）...")
    for example_file in examples[:max_examples]:
        run_result = run_example(clone_dir, example_file)
        run_result["file"] = example_file
        result["examples_run"].append(run_result)
        
        # 如果成功运行一个示例，就停止
        if run_result["success"]:
            break
    
    print(f"\n{'='*60}")
    print(f"处理完成")
    print(f"{'='*60}\n")
    
    return result


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="克隆GitHub仓库并运行示例代码")
    parser.add_argument("--repo", type=str, required=True, help="仓库URL")
    parser.add_argument("--work-dir", type=str, default="./repos", help="工作目录")
    parser.add_argument("--max-examples", type=int, default=1, help="最多运行几个示例")
    parser.add_argument("--output", type=str, default="run_result.json", help="输出JSON文件路径")
    
    args = parser.parse_args()
    
    # 运行
    result = clone_and_run(
        repo_url=args.repo,
        work_dir=args.work_dir,
        max_examples=args.max_examples
    )
    
    # 保存结果
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 结果已保存到: {args.output}")


if __name__ == "__main__":
    main()
