#!/usr/bin/env python3
"""
获取最近的攀岩活动记录 - JSON格式输出
"""
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 获取脚本所在目录，回退到项目根目录后找到 src 目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 脚本位于 .trae/skills/climbing-diary/Scripts/，需要回退 4 级到项目根目录
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(script_dir))))
src_path = os.path.join(base_dir, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from garmin_mcp import init_api
# 从公共模块导入攀岩工具函数
from garmin_mcp.climbing_utils import get_climbing_activities, format_duration

os.environ['GARMIN_CN'] = 'true'

def main(days=30):
    """
    主函数：初始化 Garmin 客户端并获取攀岩活动
    
    Args:
        days: 获取最近多少天的活动
        
    Returns:
        list: 攀岩活动列表
    """
    garmin_client = init_api(None, None, is_cn=True)

    if not garmin_client:
        return {"error": "Failed to initialize Garmin API"}

    # 使用公共模块的函数获取攀岩活动
    climbing_activities = get_climbing_activities(garmin_client, days=days)
    
    return climbing_activities

if __name__ == "__main__":
    activities = main(days=30)
    print(json.dumps(activities, ensure_ascii=False, indent=2))
