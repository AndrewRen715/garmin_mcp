#!/usr/bin/env python3
"""Script to analyze the most recent running activity using custom HR zones"""

import os
import json
import sys
from datetime import datetime
from garminconnect import Garmin

def get_user_credentials():
    """Get user credentials from environment variables"""
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    is_cn = os.environ.get("GARMIN_CN", "false").lower() == "true"
    
    if not email or not password:
        print("错误: 请设置GARMIN_EMAIL和GARMIN_PASSWORD环境变量")
        print("或者直接在脚本中输入您的凭据")
        email = input("请输入您的Garmin邮箱: ")
        password = input("请输入您的Garmin密码: ")
    
    return email, password, is_cn

def init_garmin_client(email, password, is_cn):
    """Initialize Garmin client"""
    print("初始化Garmin客户端...")
    try:
        garmin_client = Garmin(email=email, password=password, is_cn=is_cn)
        garmin_client.login()
        print("Garmin客户端初始化成功")
        return garmin_client
    except Exception as e:
        print(f"错误: 初始化Garmin客户端失败: {str(e)}")
        return None

def get_recent_running_activities(garmin_client, limit=5):
    """Get recent running activities"""
    print(f"\n获取最近的{limit}个跑步活动...")
    try:
        activities = garmin_client.get_activities(0, limit)
        
        if not activities:
            print("错误: 没有找到活动")
            return []
        
        # Filter running activities
        running_activities = []
        for activity in activities:
            activity_type = activity.get('activityType', {}).get('typeKey')
            if activity_type and 'running' in activity_type.lower():
                running_activities.append(activity)
        
        if not running_activities:
            print("错误: 没有找到跑步活动")
            return []
        
        print(f"找到 {len(running_activities)} 个跑步活动")
        return running_activities
    except Exception as e:
        print(f"错误获取活动: {str(e)}")
        return []

def get_user_hr_data(garmin_client):
    """Get user's max heart rate and resting heart rate"""
    
    print("\n获取用户心率数据...")
    
    max_hr = None
    resting_hr = None
    
    try:
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Try to get heart rate data from health stats
        print("从健康数据中获取心率信息...")
        hr_data = garmin_client.get_heart_rates(today)
        
        if hr_data:
            max_hr = hr_data.get('maxHeartRate')
            resting_hr = hr_data.get('restingHeartRate')
            
            print(f"从健康数据获取: 最大心率={max_hr} BPM, 静息心率={resting_hr} BPM")
        
        # If max HR not found, try to get from recent activities
        if not max_hr:
            print("从最近活动中获取最大心率...")
            activities = garmin_client.get_activities(0, 10)
            
            if activities:
                for activity in activities:
                    if activity.get('maxHR'):
                        max_hr = activity.get('maxHR')
                        print(f"从活动获取: 最大心率={max_hr} BPM")
                        break
        
        # If resting HR not found, try to get from RHR day data
        if not resting_hr:
            print("从静息心率数据中获取...")
            try:
                rhr_data = garmin_client.get_rhr_day(today)
                if rhr_data:
                    resting_hr = rhr_data.get('restingHeartRate')
                    print(f"从静息心率数据获取: 静息心率={resting_hr} BPM")
            except Exception as e:
                print(f"获取静息心率数据失败: {str(e)}")
        
        return max_hr, resting_hr
        
    except Exception as e:
        print(f"错误获取心率数据: {str(e)}")
        return None, None

def calculate_custom_zones(max_hr, resting_hr, method="hrr"):
    """Calculate custom HR zones based on the provided chart"""
    
    if not max_hr:
        return None
    
    # Define zones based on the chart
    zones = []
    
    if method == "hrr" and resting_hr:
        # Calculate using Heart Rate Reserve (Karvonen formula)
        hrr = max_hr - resting_hr
        print(f"\n使用储备心率法计算 (HRR = {hrr} BPM):")
        
        zones = [
            {
                "name": "E强度 (轻松跑区间)",
                "min_pct": 0.59,
                "max_pct": 0.74,
                "min": int(resting_hr + (hrr * 0.59)),
                "max": int(resting_hr + (hrr * 0.74)),
                "intensity": "Easy"
            },
            {
                "name": "M强度 (马拉松配速区间)",
                "min_pct": 0.74,
                "max_pct": 0.84,
                "min": int(resting_hr + (hrr * 0.74)),
                "max": int(resting_hr + (hrr * 0.84)),
                "intensity": "Marathon"
            },
            {
                "name": "T强度 (乳酸阈值区间)",
                "min_pct": 0.84,
                "max_pct": 0.88,
                "min": int(resting_hr + (hrr * 0.84)),
                "max": int(resting_hr + (hrr * 0.88)),
                "intensity": "Threshold"
            },
            {
                "name": "A强度 (无氧耐力区间)",
                "min_pct": 0.88,
                "max_pct": 0.95,
                "min": int(resting_hr + (hrr * 0.88)),
                "max": int(resting_hr + (hrr * 0.95)),
                "intensity": "Anaerobic"
            },
            {
                "name": "I强度 (最大摄氧区间)",
                "min_pct": 0.95,
                "max_pct": 1.00,
                "min": int(resting_hr + (hrr * 0.95)),
                "max": max_hr,
                "intensity": "Interval"
            }
        ]
    else:
        # Calculate using Max HR percentage method
        print(f"\n使用最大心率百分比法计算:")
        
        zones = [
            {
                "name": "E强度 (轻松跑区间)",
                "min_pct": 0.59,
                "max_pct": 0.74,
                "min": int(max_hr * 0.59),
                "max": int(max_hr * 0.74),
                "intensity": "Easy"
            },
            {
                "name": "M强度 (马拉松配速区间)",
                "min_pct": 0.74,
                "max_pct": 0.84,
                "min": int(max_hr * 0.74),
                "max": int(max_hr * 0.84),
                "intensity": "Marathon"
            },
            {
                "name": "T强度 (乳酸阈值区间)",
                "min_pct": 0.84,
                "max_pct": 0.88,
                "min": int(max_hr * 0.84),
                "max": int(max_hr * 0.88),
                "intensity": "Threshold"
            },
            {
                "name": "A强度 (无氧耐力区间)",
                "min_pct": 0.88,
                "max_pct": 0.95,
                "min": int(max_hr * 0.88),
                "max": int(max_hr * 0.95),
                "intensity": "Anaerobic"
            },
            {
                "name": "I强度 (最大摄氧区间)",
                "min_pct": 0.95,
                "max_pct": 1.00,
                "min": int(max_hr * 0.95),
                "max": max_hr,
                "intensity": "Interval"
            }
        ]
    
    return zones

def analyze_running_activity(activity_id, garmin_client, custom_zones, max_hr, resting_hr, method="hrr"):
    """Analyze a running activity using custom HR zones"""
    
    print(f"\n分析活动 ID: {activity_id}")
    print("=" * 80)
    
    try:
        # Get activity details
        activity = garmin_client.get_activity(activity_id)
        if not activity:
            print("错误: 无法获取活动详情")
            return None
        
        # Get activity name and type
        activity_name = activity.get('activityName')
        activity_type = activity.get('activityTypeDTO', {}).get('typeKey')
        
        print(f"活动名称: {activity_name}")
        print(f"活动类型: {activity_type}")
        print(f"开始时间: {activity.get('summaryDTO', {}).get('startTimeLocal')}")
        
        # Get activity HR data
        try:
            hr_zones_data = garmin_client.get_activity_hr_in_timezones(activity_id)
        except Exception as e:
            print(f"获取心率区间数据失败: {str(e)}")
            hr_zones_data = None
        
        # Analyze HR zones
        print("\n心率区间分析:")
        print("=" * 80)
        
        # Print custom zones
        print("\n自定义心率区间 (基于提供的图表):")
        for zone in custom_zones:
            print(f"{zone['name']}: {zone['min']}-{zone['max']} BPM ({zone['min_pct']*100:.0f}%-{zone['max_pct']*100:.0f}% {"储备心率" if method == "hrr" else "最大心率"})")
        
        # Get time in zones data
        time_in_zones = []
        if hr_zones_data:
            time_in_zones = hr_zones_data.get('timeInZones', [])
        
        if time_in_zones:
            print("\n各区间时间分布:")
            print("-" * 80)
            
            total_time = sum([tz.get('seconds', 0) for tz in time_in_zones])
            
            for tz in time_in_zones:
                zone_num = tz.get('zone')
                seconds = tz.get('seconds', 0)
                minutes = seconds / 60
                percentage = (seconds / total_time * 100) if total_time > 0 else 0
                
                # Find corresponding custom zone
                custom_zone = None
                if 1 <= zone_num <= len(custom_zones):
                    custom_zone = custom_zones[zone_num - 1]
                
                if custom_zone:
                    print(f"{custom_zone['name']}: {minutes:.1f} 分钟 ({percentage:.1f}%)")
                else:
                    print(f"区间 {zone_num}: {minutes:.1f} 分钟 ({percentage:.1f}%)")
            
            print(f"\n总时间: {total_time / 60:.1f} 分钟")
        else:
            print("\n无法获取各区间时间分布数据")
        
        # Get activity summary
        summary = activity.get('summaryDTO', {})
        avg_hr = summary.get('averageHR')
        max_hr_activity = summary.get('maxHR')
        distance = summary.get('distance')
        duration = summary.get('duration')
        calories = summary.get('calories')
        avg_speed = summary.get('averageSpeed')
        
        print("\n活动摘要:")
        print("=" * 80)
        print(f"平均心率: {avg_hr} BPM")
        print(f"最大心率: {max_hr_activity} BPM")
        print(f"距离: {distance / 1000:.2f} km")
        print(f"时长: {duration / 60:.1f} 分钟")
        print(f"卡路里: {calories}")
        if avg_speed:
            print(f"平均配速: {60 / (avg_speed * 3.6):.2f} 分钟/km")
        
        # Calculate average intensity
        if avg_hr:
            if method == "hrr" and resting_hr and max_hr:
                # Calculate using HRR method
                hrr = max_hr - resting_hr
                avg_intensity_pct = ((avg_hr - resting_hr) / hrr) * 100
                print(f"平均强度: {avg_intensity_pct:.1f}% 储备心率")
            else:
                # Calculate using max HR method
                avg_intensity_pct = (avg_hr / max_hr) * 100
                print(f"平均强度: {avg_intensity_pct:.1f}% 最大心率")
            
            # Determine intensity zone
            for zone in custom_zones:
                if zone['min_pct'] * 100 <= avg_intensity_pct < zone['max_pct'] * 100:
                    print(f"平均强度区间: {zone['name']}")
                    break
        
        return activity
        
    except Exception as e:
        print(f"错误分析活动: {str(e)}")
        return None

def main():
    """Main function"""
    
    print("分析最近的跑步活动")
    print("基于用户提供的图表设置")
    print("=" * 80)
    
    # Get user credentials
    email, password, is_cn = get_user_credentials()
    
    # Initialize Garmin client
    garmin_client = init_garmin_client(email, password, is_cn)
    if not garmin_client:
        return
    
    # Get recent running activities
    running_activities = get_recent_running_activities(garmin_client)
    if not running_activities:
        return
    
    # Get the most recent running activity
    most_recent_activity = running_activities[0]
    activity_id = most_recent_activity.get('activityId')
    activity_name = most_recent_activity.get('activityName')
    start_time = most_recent_activity.get('startTimeLocal')
    
    print(f"\n分析最近的跑步活动: {activity_name}")
    print(f"开始时间: {start_time}")
    print(f"活动ID: {activity_id}")
    
    # Get user's HR data
    max_hr, resting_hr = get_user_hr_data(garmin_client)
    
    if not max_hr:
        print("\n错误: 无法获取最大心率")
        print("请输入您的最大心率:")
        max_hr = int(input("最大心率: "))
    
    if not resting_hr:
        print("\n错误: 无法获取静息心率")
        print("请输入您的静息心率:")
        resting_hr = int(input("静息心率: "))
    
    print(f"\n使用的心率数据:")
    print(f"最大心率: {max_hr} BPM")
    print(f"静息心率: {resting_hr} BPM")
    
    # Calculate custom zones
    custom_zones = calculate_custom_zones(max_hr, resting_hr, method="hrr")
    
    if not custom_zones:
        print("\n错误: 无法计算自定义心率区间")
        return
    
    # Analyze the most recent activity
    analyze_running_activity(activity_id, garmin_client, custom_zones, max_hr, resting_hr, method="hrr")

if __name__ == "__main__":
    main()
