#!/usr/bin/env python3
"""
使用环境变量重新认证 Garmin Connect 并更新 token
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

def main():
    """主函数"""
    print("使用环境变量重新认证 Garmin Connect 并更新 token")
    print("=" * 80)
    
    # 从环境变量获取凭据
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    is_cn = os.environ.get("GARMIN_CN", "true").lower() == "true"
    
    if not email or not password:
        print("错误: 请设置 GARMIN_EMAIL 和 GARMIN_PASSWORD 环境变量")
        print("例如:")
        print("  set GARMIN_EMAIL=您的邮箱")
        print("  set GARMIN_PASSWORD=您的密码")
        print("  set GARMIN_CN=true (使用中国区)")
        return
    
    print(f"\n正在初始化 API (中国区: {is_cn})...")
    print(f"使用邮箱: {email}")
    
    # 初始化 API
    garmin_client = init_api(email, password, is_cn)
    
    if garmin_client:
        print("\n✓ 认证