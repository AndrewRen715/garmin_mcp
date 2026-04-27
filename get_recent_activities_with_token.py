#!/usr/bin/env python3
"""
通过Garmin Connect API获取最近的活动记录（使用token）
"""
import json
import sys
import os
from pathlib import Path

# 尝试导入garminconnect库
try:
    from garminconnect import Garmin
    import getpass
    garmin_available = True
except ImportError:
    garmin_available = False


def get_token_path():
    """
    获取token存储路径
    """
    return os.getenv("GARMINTOKENS") or "~/.garminconnect"


def token_exists():
    """
    检查token是否存在
    """
    token_path = get_token_path()
    expanded_path = Path(os.path.expanduser(token_path))
    return expanded_path.exists()


def get_recent_activities():
    """
    通过Garmin Connect API获取最近的活动记录
    """
    if not garmin_available:
        print("错误: 未安装garminconnect库。请使用 'pip install garminconnect' 安装。")
        return None
    
    try:
        token_path = get_token_path()
        expanded_token_path = os.path.expanduser(token_path)
        
        # 首先尝试使用token登录
        if token_exists():
            print(f"尝试使用现有token登录: {expanded_token_path}")
            # 默认使用中国区
            garmin = Garmin(is_cn=True)
            garmin.login(expanded_token_path)
            print("使用token登录成功！")
        else:
            # 如果token不存在，要求用户输入凭据
            print("未找到现有token，需要输入凭据登录...")
            email = input("请输入您的Garmin Connect邮箱: ")
            password = getpass.getpass("请输入您的Garmin Connect密码: ")
            
            # 初始化Garmin客户端，默认使用中国区
            print("正在登录Garmin Connect中国区...")
            garmin = Garmin(email, password, is_cn=True)
            garmin.login()
            
            # 保存token
            print(f"正在保存token到: {expanded_token_path}")
            garmin.garth.dump(expanded_token_path)
            print("token保存成功，下次登录将自动使用！")
        
        # 获取最近的活动记录
        print("正在获取最近的活动记录...")
        activities = garmin.get_activities(0, 20)  # 获取最近20个活动
        
        if not activities:
            print("未找到活动记录")
            return None
        
        # 整理活动数据
        curated = {
            "count": len(activities),
            "activities": []
        }
        
        for a in activities:
            activity = {
                "id": a.get('activityId'),
                "name": a.get('activityName'),
                "type": a.get('activityType', {}).get('typeKey'),
                "start_time": a.get('startTimeLocal'),
                "distance_meters": a.get('distance'),
                "duration_seconds": a.get('duration'),
                "calories": a.get('calories'),
                "avg_hr_bpm": a.get('averageHR'),
                "max_hr_bpm": a.get('maxHR'),
                "steps": a.get('steps'),
            }
            # 移除None值
            activity = {k: v for k, v in activity.items() if v is not None}
            curated["activities"].append(activity)
        
        print("\n成功获取最近的活动记录:")
        print(json.dumps(curated, indent=2, ensure_ascii=False))
        
        return curated
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None


def main():
    """
    主函数
    """
    print("=" * 80)
    print("Garmin Connect 活动记录获取工具 (使用token)")
    print("=" * 80)
    print("此工具将通过Garmin Connect API获取您最近的活动记录")
    print("优先使用现有的token登录，无需重复输入凭据")
    print("=" * 80)
    
    # 检查garminconnect库是否可用
    if not garmin_available:
        print("\ngarminconnect库未安装，无法直接连接Garmin Connect。")
        print("请使用 'pip install garminconnect' 安装。")
        return
    
    # 获取活动记录
    activities = get_recent_activities()
    
    if activities:
        print("\n活动记录获取成功！")
    else:
        print("\n活动记录获取失败。")


if __name__ == "__main__":
    main()
