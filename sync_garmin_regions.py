#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
同步佳明国内区(CN)和国际区(Global)的数据
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from garminconnect import Garmin
    garmin_available = True
except ImportError:
    print("错误: 未安装garminconnect库")
    sys.exit(1)

# 添加 src 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 从公共模块导入攀岩工具函数
from garmin_mcp.climbing_utils import get_climbing_activities

def sync_regions():
    """同步国内区和国际区数据"""
    print("=" * 60)
    print("Garmin Connect 国内区 & 国际区数据同步")
    print("=" * 60)
    
    # 获取国内区数据
    print("\n1. 连接国内区 (Garmin Connect China)...")
    cn_token_path = os.path.expanduser("~/.garminconnect_cn")
    cn_activities = []
    try:
        garmin_cn = Garmin(is_cn=True)
        garmin_cn.login(cn_token_path)
        cn_activities = get_climbing_activities(garmin_cn)
        print("   OK 国内区获取到 {} 条攀岩活动".format(len(cn_activities)))
    except Exception as e:
        print("   FAIL 国内区连接失败: {}".format(e))
    
    # 获取国际区数据
    print("\n2. 连接国际区 (Garmin Connect Global)...")
    global_token_path = os.path.expanduser("~/.garminconnect")
    global_activities = []
    try:
        garmin_global = Garmin(is_cn=False)
        garmin_global.login(global_token_path)
        global_activities = get_climbing_activities(garmin_global)
        print("   OK 国际区获取到 {} 条攀岩活动".format(len(global_activities)))
    except Exception as e:
        print("   FAIL 国际区连接失败: {}".format(e))
    
    # 合并数据并去重
    print("\n3. 合并数据并去重...")
    all_activities = []
    seen_ids = set()
    
    for activity in cn_activities + global_activities:
        activity_id = activity.get('activityId')
        if activity_id and activity_id not in seen_ids:
            seen_ids.add(activity_id)
            all_activities.append(activity)
    
    # 按日期排序
    all_activities.sort(key=lambda x: x.get('startTimeLocal', ''), reverse=True)
    
    cn_ids = set(a.get('activityId') for a in cn_activities if a.get('activityId'))
    global_ids = set(a.get('activityId') for a in global_activities if a.get('activityId'))
    
    cn_only = len(cn_ids - global_ids)
    global_only = len(global_ids - cn_ids)
    duplicates = len(cn_ids & global_ids)
    
    print("   OK 合并后共 {} 条活动（去重后）".format(len(all_activities)))
    print("   - 国内区独有: {}".format(cn_only))
    print("   - 国际区独有: {}".format(global_only))
    print("   - 重复数据: {}".format(duplicates))
    
    # 输出合并后的活动列表
    print("\n4. 合并后的攀岩活动列表:")
    print("-" * 80)
    for activity in all_activities[:15]:
        start_time = activity.get('startTimeLocal', '')
        date = start_time.split(' ')[0] if start_time else 'Unknown'
        is_cn_only = activity.get('activityId') in cn_ids and activity.get('activityId') not in global_ids
        is_global_only = activity.get('activityId') in global_ids and activity.get('activityId') not in cn_ids
        is_both = activity.get('activityId') in cn_ids and activity.get('activityId') in global_ids
        
        region = "CN" if is_cn_only else ("GL" if is_global_only else "BOTH")
        print("{} | {} | {} | {} | {}min".format(
            region,
            date,
            activity.get('activityName', 'Unnamed'),
            activity.get('activityType', {}).get('typeKey', 'Unknown'),
            activity.get('duration', 0) // 60
        ))
    
    if len(all_activities) > 15:
        print("... 还有 {} 条活动".format(len(all_activities) - 15))
    
    print("\n" + "=" * 60)
    print("同步完成!")
    print("=" * 60)
    
    return all_activities

if __name__ == "__main__":
    sync_regions()