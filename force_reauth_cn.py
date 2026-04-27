#!/usr/bin/env python3
"""
强制更新 Garmin Connect 中国区 token
"""

import sys
import os
import shutil

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

def main():
    """主函数"""
    print("强制更新 Garmin Connect 中国区 token")
    print("=" * 80)
    
    # 设置环境变量为中国区
    os.environ['GARMIN_CN'] = 'true'
    
    # 设置 token 存储路径
    cn_tokenstore = os.getenv("GARMINTOKENS_CN") or "~/.garminconnect_cn"
    expanded_tokenstore = os.path.expanduser(cn_tokenstore)
    
    print(f"使用 token 存储路径: {expanded_tokenstore}")
    
    # 获取用户输入
    email = input("请输入您的 Garmin Connect 邮箱: ")
    password = input("请输入您的 Garmin Connect 密码: ")
    
    print("\n正在初始化中国区 API...")
    print("注意：如果需要 MFA 验证码，请查看您的邮箱或手机")
    
    # 初始化 API，明确指定中国区
    garmin_client = init_api(email, password, is_cn=True)
    
    if garmin_client:
        print("\n✓ 中国区认证成功！Token 已更新")
        print(f"Token 已保存到 {expanded_tokenstore} 目录")
        print("您现在可以正常使用 Garmin 相关功能了")
    else:
        print("\n✗ 认证失败，请检查：")
        print("1. 邮箱和密码是否正确")
        print("2. 网络连接是否正常")
        print("3. MFA 验证码是否正确输入")

if __name__ == "__main__":
    main()
