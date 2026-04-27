#!/usr/bin/env python3
"""
通过Garmin Connect API获取最近的活动记录
"""
import json
import sys
from datetime import datetime, timedelta

# 尝试导入garminconnect库
try:
    from garminconnect import Garmin
    import getpass
    garmin_available = True
except ImportError:
    garmin_available = False


def get_recent_activities():
    """
    通过Garmin Connect API获取最近的活动记录
    """
    if not garmin_available:
        print("错误: 未安装garminconnect库。请使用 'pip install garminconnect' 安装。")
        return None
    
    try:
        # 获取用户输入
        email = input("请输入您的Garmin Connect邮箱: ")
        password = getpass.getpass("请输入您的Garmin Connect密码: ")
        
        # 初始化Garmin客户端
        print("正在登录Garmin Connect...")
        garmin = Garmin(email, password)
        garmin.login()
        
        # 获取最近的活动记录
        print("正在获取最近的活动记录...")
        activities = garmin.get_activities(0, 10)  # 获取最近10个活动
        
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
    print("Garmin Connect 活动记录获取工具")
    print("=" * 80)
    print("此工具将通过Garmin Connect API获取您最近的活动记录")
    print("\n注意:")
    print("1. 您需要输入有效的Garmin Connect账号密码")
    print("2. 首次登录可能需要验证码验证")
    print("3. 请确保您的账号已启用API访问")
    print("=" * 80)
    
    # 检查garminconnect库是否可用
    if not garmin_available:
        print("\ngarminconnect库未安装，无法直接连接Garmin Connect。")
        print("在实际环境中，您可以通过以下步骤获取活动记录:")
        print("1. 安装garminconnect库: pip install garminconnect")
        print("2. 使用Garmin类登录并获取活动:")
        print("   from garminconnect import Garmin")
        print("   garmin = Garmin(email, password)")
        print("   garmin.login()")
        print("   activities = garmin.get_activities(0, 10)  # 获取最近10个活动")
        return
    
    # 获取活动记录
    activities = get_recent_activities()
    
    if activities:
        print("\n活动记录获取成功！")
    else:
        print("\n活动记录获取失败。")


if __name__ == "__main__":
    main()
