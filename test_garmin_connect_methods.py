#!/usr/bin/env python3
"""
测试garminconnect库的可用方法
"""

import sys
import os
from garminconnect import Garmin

def main():
    """
    主函数
    """
    print("=" * 80)
    print("测试garminconnect库的可用方法")
    print("=" * 80)
    
    # 尝试初始化Garmin客户端
    try:
        token_path = os.path.expanduser("~/.garminconnect_cn")
        print(f"尝试使用token登录: {token_path}")
        
        garmin = Garmin(is_cn=True)
        garmin.login(token_path)
        print("登录成功！")
        
        # 查看Garmin对象的所有方法
        print("\nGarmin对象的可用方法:")
        print("=" * 60)
        
        methods = [method for method in dir(garmin) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  - {method}")
        
        # 特别查看与心率相关的方法
        print("\n与心率相关的方法:")
        print("=" * 60)
        hr_methods = [method for method in methods if 'hr' in method.lower() or 'heart' in method.lower()]
        for method in hr_methods:
            print(f"  - {method}")
        
        # 特别查看与活动相关的方法
        print("\n与活动相关的方法:")
        print("=" * 60)
        activity_methods = [method for method in methods if 'activity' in method.lower()]
        for method in activity_methods:
            print(f"  - {method}")
        
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
