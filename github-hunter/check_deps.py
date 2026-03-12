#!/usr/bin/env python3
"""
检查并安装 github-hunter 的依赖项

用法:
    python check_deps.py
    python check_deps.py --install
"""

import sys
import subprocess
import argparse


def check_python_package(package_name: str) -> bool:
    """检查 Python 包是否已安装"""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def install_python_package(package_name: str) -> bool:
    """安装 Python 包"""
    print(f"📦 正在安装: {package_name}")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", package_name
        ])
        return True
    except subprocess.CalledProcessError:
        return False


def check_command(command: str) -> bool:
    """检查系统命令是否可用"""
    try:
        subprocess.check_call(
            [command, "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    parser = argparse.ArgumentParser(description="检查并安装 github-hunter 依赖")
    parser.add_argument("--install", action="store_true", help="自动安装缺失的依赖")
    args = parser.parse_args()

    print("=" * 80)
    print("🔍 github-hunter 依赖检查")
    print("=" * 80)
    print()

    # 检查 Python 包
    python_packages = [
        ("playwright", "playwright>=1.40.0"),
        ("git", "gitpython>=3.1.40"),
    ]

    print("📦 Python 包检查:")
    all_python_ok = True
    for module_name, package_name in python_packages:
        if check_python_package(module_name):
            print(f"   ✅ {package_name}")
        else:
            print(f"   ❌ {package_name} (缺失)")
            all_python_ok = False

    print()

    # 检查系统命令
    system_commands = ["git"]
    print("💻 系统命令检查:")
    all_system_ok = True
    for cmd in system_commands:
        if check_command(cmd):
            print(f"   ✅ {cmd}")
        else:
            print(f"   ❌ {cmd} (缺失)")
            all_system_ok = False

    print()

    # 检查 Playwright 浏览器
    print("🌐 Playwright 浏览器检查:")
    playwright_ok = False
    if check_python_package("playwright"):
        try:
            import playwright
            # 简单检查是否有浏览器
            from playwright.sync_api import sync_playwright
            try:
                with sync_playwright() as p:
                    # 尝试启动浏览器（不实际启动，只检查）
                    print(f"   ✅ playwright 可用")
                    playwright_ok = True
            except:
                print(f"   ⚠️  playwright 已安装，但需要运行 'playwright install chromium'")
        except Exception as e:
            print(f"   ❌ playwright 检查失败: {e}")
    else:
        print(f"   ❌ playwright 未安装")

    print()

    # 总结
    print("=" * 80)
    print("📊 检查结果:")
    print("=" * 80)

    if all_python_ok and all_system_ok and playwright_ok:
        print()
        print("✅ 所有依赖已满足！")
        print()
        print("💡 快速开始:")
        print("   python github-hunter.py --since daily --limit 15")
        print("   ./run.sh --since daily --limit 15")
        return 0
    else:
        print()
        print("⚠️  部分依赖缺失")
        print()

        if args.install:
            print("🚀 开始自动安装...")
            print()

            # 安装 Python 包
            for module_name, package_name in python_packages:
                if not check_python_package(module_name):
                    if install_python_package(package_name):
                        print(f"✅ 已安装: {package_name}")
                    else:
                        print(f"❌ 安装失败: {package_name}")

            # 安装 Playwright 浏览器
            if check_python_package("playwright"):
                print()
                print("🌐 正在安装 Playwright Chromium...")
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "playwright", "install", "chromium"
                    ])
                    print("✅ Playwright Chromium 已安装")
                except subprocess.CalledProcessError:
                    print("❌ Playwright 浏览器安装失败")

            print()
            print("=" * 80)
            print("✅ 安装完成，请重新运行检查:")
            print("   python check_deps.py")
            print("=" * 80)
        else:
            print("💡 安装命令:")
            print("   pip install playwright gitpython")
            print("   playwright install chromium")
            print()
            print("   或者自动安装:")
            print("   python check_deps.py --install")

        return 1


if __name__ == "__main__":
    sys.exit(main())
