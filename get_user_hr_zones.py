#!/usr/bin/env python3
"""Script to get user's heart rate zones from Garmin Connect"""

import json
import sys
from datetime import datetime

# Add src directory to path
sys.path.insert(0, 'src')

from garmin_mcp import init_api
from garmin_mcp.activity_management import garmin_client as activity_client
from garmin_mcp.health_wellness import garmin_client as health_client

# This script should be run through the MCP server, but for testing purposes
# we'll create a simple function to demonstrate how to get HR zones

def get_user_hr_zones():
    """Get user's heart rate zones from Garmin Connect"""
    
    print("获取用户心率区间设置...")
    print("=" * 80)
    
    # Check if garmin_client is available
    if not activity_client:
        print("错误: 请先通过MCP服务器初始化Garmin客户端")
        return None
    
    try:
        # Get recent activities to find one with HR data
        print("\n获取最近的活动...")
        activities = activity_client.get_activities(0, 5)
        
        if not activities:
            print("没有找到活动")
            return None
        
        # Find the first activity with heart rate data
        target_activity = None
        for activity in activities:
            if activity.get('maxHR') and activity.get('averageHR'):
                target_activity = activity
                break
        
        if not target_activity:
            print("没有找到包含心率数据的活动")
            return None
        
        activity_id = target_activity.get('activityId')
        activity_name = target_activity.get('activityName')
        activity_type = target_activity.get('activityType', {}).get('typeKey')
        
        print(f"\n找到目标活动: {activity_name} (类型: {activity_type})")
        print(f"活动ID: {activity_id}")
        print(f"平均心率: {target_activity.get('averageHR')} BPM")
        print(f"最大心率: {target_activity.get('maxHR')} BPM")
        
        # Get HR zones for this activity
        print("\n获取活动的心率区间数据...")
        hr_zones_data = activity_client.get_activity_hr_in_timezones(activity_id)
        
        if not hr_zones_data:
            print("没有找到心率区间数据")
            return None
        
        # Save HR zones data to file
        with open('hr_zones_data.json', 'w', encoding='utf-8') as f:
            json.dump(hr_zones_data, f, indent=2, ensure_ascii=False)
        print("心率区间数据已保存到 hr_zones_data.json")
        
        # Analyze HR zones data
        print("\n分析心率区间数据...")
        print("=" * 80)
        
        if isinstance(hr_zones_data, dict):
            # Check the structure of HR zones data
            print("心率区间数据结构:")
            for key, value in hr_zones_data.items():
                if isinstance(value, list):
                    print(f"  - {key}: 包含 {len(value)} 个项目")
                else:
                    print(f"  - {key}: {type(value).__name__}")
            
            # If it's a list, process each item
            if 'zones' in hr_zones_data:
                zones = hr_zones_data['zones']
                print("\n用户的心率区间设置:")
                for i, zone in enumerate(zones):
                    print(f"  区间 {i+1}: {zone.get('min')} - {zone.get('max')} BPM")
            elif 'heartRateZones' in hr_zones_data:
                zones = hr_zones_data['heartRateZones']
                print("\n用户的心率区间设置:")
                for i, zone in enumerate(zones):
                    print(f"  区间 {i+1}: {zone.get('min')} - {zone.get('max')} BPM")
            else:
                # Try to find zones in the data
                print("\n尝试在数据中查找心率区间...")
                for key, value in hr_zones_data.items():
                    if isinstance(value, list) and len(value) > 0:
                        first_item = value[0]
                        if isinstance(first_item, dict) and ('min' in first_item and 'max' in first_item):
                            print(f"在 '{key}' 中找到心率区间:")
                            for i, zone in enumerate(value):
                                print(f"  区间 {i+1}: {zone.get('min')} - {zone.get('max')} BPM")
                            break
        
        return hr_zones_data
        
    except Exception as e:
        print(f"错误获取心率区间数据: {str(e)}")
        return None

if __name__ == "__main__":
    print("此脚本应通过MCP服务器运行")
    print("示例用法:")
    print("1. 启动MCP服务器: garmin-mcp")
    print("2. 使用get_activity_hr_in_timezones工具获取活动的心率区间数据")
    print("3. 分析返回的数据以获取用户的心率区间设置")
    
    # For demonstration purposes, we'll show how to use the tool
    print("\n工具调用示例:")
    print("get_activity_hr_in_timezones(activity_id=1234567890)")
