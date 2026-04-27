#!/usr/bin/env python3
"""
重新认证 Garmin Connect 并更新 token
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

def main():
    """主函数"""
    print("重新认证 Garmin Connect 并更新 token")
    print("=" * 80)
    
    # 获取用户输入
    email = input("请输入您的 Garmin Connect 邮箱: ")
    password = input("请输入您的 Garmin Connect 密码: ")
    cn_input = input("是否使用中国区账号? (y/n): ")
    is_cn = cn_input.lower() == "y"
    
    print(f"\n正在初始化 API (中国区: {is_cn})...")
    
    # 初始化 API
    garmin_client = init_api(email, password, is_cn)
    
    if garmin_client:
        print("\n✓ 认证成功！Token 已更新")
        print("您现在可以正常使用 Garmin 相关功能了")
    else:
        print("\n✗ 认证失败，请检查您的邮箱、密码和网络连接")

if __name__ == "__main__":
    main()
