#!/usr/bin/env python3
"""Script to analyze the most recent running activity using custom HR zones (China region support)"""

import os
import json
import sys
from datetime import datetime
from garminconnect import Garmin

def get_user_credentials():
    """Get user credentials from environment variables"""
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    is_cn = os.environ.get("GARMIN_CN", "true").lower() == "true"
    
    if not email or not password:
        print("错误: 请设置GARMIN_EMAIL和GARMIN_PASSWORD环境变量")
        print("或者直接在脚本中输入您的凭据")
        email = input("请输入您的Garmin邮箱: ")
        password = input("请输入您的Garmin密码: ")
        cn_input = input("是否使用中国区账号? (y/n): ")
        is_cn = cn_input.lower() == "y"
    
    return email, password, is_cn

def get_mfa():
    """Get MFA code from user input"""
    return input("请输入MFA验证码: ")

def init_garmin_client():
    """Initialize Garmin client using token or credentials"""
    print("初始化Garmin客户端...")
    
    # Token store path
    tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
    tokenstore = os.path.expanduser(tokenstore)
    
    try:
        # First try to login using existing tokens
        print(f"尝试使用token文件登录: {tokenstore}")
        garmin_client = Garmin()
        garmin_client.login(tokenstore)
        print("使用token登录成功")
        return garmin_client
    except Exception as e:
        print(f"使用token登录失败: {str(e)}")
        print("尝试使用凭据登录...")
        
        # If token login fails, try with credentials
        email, password, is_cn = get_user_credentials()
        
        try:
            garmin_client = Garmin(email=email, password=password, is_cn=is_cn, prompt_mfa=get_mfa)
            garmin_client.login()
            # Save tokens for future use
            garmin_client.garth.dump(tokenstore)
            print("使用凭据登录成功，已保存token")
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

def get_user_hr_data(garmin_client, recent_activities=None):
    """Get user's max heart rate and resting heart rate"""
    
    print("\n获取用户心率数据...")
    
    max_hr = None
    resting_hr = None
    
    try:
        # First, try to get max HR from recent activities (more reliable)
        if recent_activities:
            print("从最近活动中获取最大心率...")
            max_hr_values = []
            for activity in recent_activities:
                if activity.get('maxHR'):
                    max_hr_values.append(activity.get('maxHR'))
            
            if max_hr_values:
                max_hr = max(max_hr_values)
                print(f"从活动获取: 最大心率={max_hr} BPM")
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Try to get heart rate data from health stats
        print("从健康数据中获取心率信息...")
        try:
            hr_data = garmin_client.get_heart_rates(today)
            
            if hr_data:
                health_max_hr = hr_data.get('maxHeartRate')
                health_resting_hr = hr_data.get('restingHeartRate')
                
                print(f"从健康数据获取: 最大心率={health_max_hr} BPM, 静息心率={health_resting_hr} BPM")
                
                # Only use health data if we don't have better data from activities
                if not max_hr and health_max_hr:
                    max_hr = health_max_hr
                if not resting_hr and health_resting_hr:
                    resting_hr = health_resting_hr
        except Exception as e:
            print(f"获取心率数据失败: {str(e)}")
        
        # If still no resting HR, try to estimate it
        if not resting_hr:
            # Estimate resting HR based on common values
            resting_hr = 60
            print(f"估计静息心率: {resting_hr} BPM")
        
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
        hr_zones_data = None
        try:
            hr_zones_data = garmin_client.get_activity_hr_in_timezones(activity_id)
        except Exception as e:
            print(f"获取心率区间数据失败: {str(e)}")
        
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
            if isinstance(hr_zones_data, list):
                # If it's a list, try to find the timeInZones data
                for item in hr_zones_data:
                    if isinstance(item, dict) and 'timeInZones' in item:
                        time_in_zones = item.get('timeInZones', [])
                        break
            elif isinstance(hr_zones_data, dict):
                # If it's a dict, get timeInZones directly
                time_in_zones = hr_zones_data.get('timeInZones', [])
        
        if time_in_zones:
            print("\n各区间时间分布:")
            print("-" * 80)
            
            total_time = sum([tz.get('seconds', 0) for tz in time_in_zones if isinstance(tz, dict)])
            
            for tz in time_in_zones:
                if isinstance(tz, dict):
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
                if hrr > 0:
                    avg_intensity_pct = ((avg_hr - resting_hr) / hrr) * 100
                    print(f"平均强度: {avg_intensity_pct:.1f}% 储备心率")
                    
                    # Determine intensity zone
                    for zone in custom_zones:
                        if zone['min_pct'] * 100 <= avg_intensity_pct < zone['max_pct'] * 100:
                            print(f"平均强度区间: {zone['name']}")
                            break
                else:
                    print("错误: 储备心率计算失败 (HRR = 0)")
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
        import traceback
        traceback.print_exc()
        return None

def main():
    """Main function"""
    
    print("分析最近的跑步活动")
    print("基于用户提供的图表设置")
    print("(支持中国区账号)")
    print("=" * 80)
    
    # Initialize Garmin client
    garmin_client = init_garmin_client()
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
    
    # Get user's HR data, using recent activities for better accuracy
    max_hr, resting_hr = get_user_hr_data(garmin_client, running_activities)
    
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
