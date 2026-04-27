#!/usr/bin/env python3
"""
获取最新活动的每公里分段数据并分析
"""

import json
import sys
import os
from datetime import datetime

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

def format_pace(minutes_per_km):
    """Format pace from minutes per km to min:sec per km"""
    if minutes_per_km <= 0:
        return "00:00"
    total_seconds = minutes_per_km * 60
    mins = int(total_seconds // 60)
    secs = int(total_seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def get_latest_activity_segments():
    """
    获取最新活动的每公里分段数据并分析
    """
    print("获取最新活动的每公里分段数据并分析...")
    print()
    
    # Initialize Garmin client
    print("初始化 Garmin Connect 客户端...")
    try:
        # Try China region first
        garmin_cn = init_api(None, None, is_cn=True)
        print("✓ 中国区域客户端初始化成功")
        garmin_client = garmin_cn
        region = "China"
    except Exception as e:
        print(f"✗ 中国区域客户端初始化失败: {e}")
        try:
            # Fallback to global region
            garmin_global = init_api(None, None, is_cn=False)
            print("✓ 全球区域客户端初始化成功")
            garmin_client = garmin_global
            region = "Global"
        except Exception as e:
            print(f"✗ 全球区域客户端初始化失败: {e}")
            return
    
    print(f"\n使用 {region} 区域进行数据获取...")
    
    # Get recent activities
    print("\n获取最近的活动...")
    try:
        activities = []
        start = 0
        limit = 20
        
        # Get activities with pagination
        while True:
            page = garmin_client.get_activities(start, limit)
            if not page:
                break
            activities.extend(page)
            start += limit
            if len(page) < limit:
                break
        
        if not activities:
            print("未找到任何活动。")
            return
        
        # Sort by start time (most recent first)
        activities.sort(key=lambda x: x.get('startTimeLocal', ''), reverse=True)
        
        # Get the most recent activity
        latest_activity = activities[0]
        activity_id = latest_activity.get('activityId')
        
        if not activity_id:
            print("最新活动未找到活动 ID。")
            return
        
        print(f"\n找到最新活动:")
        print(f"- 名称: {latest_activity.get('activityName', '未命名')}")
        print(f"- 日期: {latest_activity.get('startTimeLocal', '未知')}")
        print(f"- 活动 ID: {activity_id}")
        print(f"- 活动类型: {latest_activity.get('activityType', {}).get('typeKey', '未知')}")
        print()
        
        # Try to get per-kilometer splits via garth client
        print("获取每公里分段数据...")
        
        if hasattr(garmin_client, 'garth'):
            print("✓ 使用 garth 客户端获取每公里分段数据")
            
            # Try different split endpoints to get per-kilometer splits
            split_endpoints = [
                f"activity-service/activity/{activity_id}/splits",
                f"activity-service/activity/{activity_id}/splits/summary",
                f"activity-service/activity/{activity_id}/laps"
            ]
            
            per_km_splits = []
            
            for endpoint in split_endpoints:
                try:
                    print(f"\n尝试端点: {endpoint}")
                    response = garmin_client.garth.get("connectapi", endpoint)
                    
                    if response.status_code == 200:
                        split_data = response.json()
                        print(f"✓ 成功! 状态码: {response.status_code}")
                        
                        if isinstance(split_data, dict):
                            # Check for per-kilometer splits
                            if 'lapDTOs' in split_data:
                                laps = split_data['lapDTOs']
                                print(f"  找到 {len(laps)} 个分段")
                                
                                # Filter for per-kilometer splits (distance around 1 km)
                                for lap in laps:
                                    if isinstance(lap, dict):
                                        distance = lap.get('distance', 0) / 1000  # convert to km
                                        if 0.9 <= distance <= 1.1:  # Per-kilometer splits
                                            per_km_splits.append(lap)
                                
                                if per_km_splits:
                                    print(f"  识别到 {len(per_km_splits)} 个每公里分段")
                                    break
                            elif 'splits' in split_data:
                                splits = split_data['splits']
                                print(f"  找到 {len(splits)} 个分段")
                                
                                # Check if these are per-kilometer splits
                                for split in splits:
                                    if isinstance(split, dict):
                                        distance = split.get('distance', 0) / 1000  # convert to km
                                        if 0.9 <= distance <= 1.1:  # Per-kilometer splits
                                            per_km_splits.append(split)
                                
                                if per_km_splits:
                                    print(f"  识别到 {len(per_km_splits)} 个每公里分段")
                                    break
                    else:
                        print(f"✗ 失败: 状态码 {response.status_code}")
                except Exception as e:
                    print(f"✗ 端点 {endpoint} 错误: {e}")
            
            if per_km_splits:
                print("\n每公里分段详细数据:")
                print("-" * 180)
                print(f"{'公里':<8} {'距离':<10} {'时间':<12} {'配速':<12} {'爬升':<15} {'心率':<10} {'功率':<12}")
                print("-" * 180)
                
                # Store split data for analysis
                split_analysis = []
                
                for i, split in enumerate(per_km_splits):
                    if isinstance(split, dict):
                        # Get distance and time from split data
                        split_distance = split.get('distance', 0) / 1000  # convert to km
                        split_time = split.get('duration', 0) / 60  # convert to minutes
                        split_pace = split_time / split_distance if split_distance > 0 else 0
                        
                        # Get elevation data
                        split_elevation_gain = split.get('elevationGain', 0)
                        split_elevation_loss = split.get('elevationLoss', 0)
                        
                        # Get heart rate data
                        split_hr = split.get('averageHeartRate', split.get('averageHR', 0))
                        split_max_hr = split.get('maxHeartRate', split.get('maxHR', 0))
                        
                        # Get power data
                        split_power = split.get('averagePower', 0)
                        
                        # Format display strings
                        time_str = f"{int(split_time // 60):02d}:{int(split_time % 60):02d}"
                        pace_str = f"{format_pace(split_pace)}"
                        elevation_str = f"+{split_elevation_gain:.0f}/-{split_elevation_loss:.0f}"
                        hr_str = f"{split_hr}/{split_max_hr}"
                        power_str = f"{split_power}W"
                        
                        print(f"{i+1:<8} {split_distance:.2f} km    {time_str:<12} {pace_str:<12} {elevation_str:<15} {hr_str:<10} {power_str:<12}")
                        
                        # Store data for analysis
                        split_analysis.append({
                            'km': i + 1,
                            'distance': split_distance,
                            'time': split_time,
                            'pace': split_pace,
                            'elevation_gain': split_elevation_gain,
                            'elevation_loss': split_elevation_loss,
                            'avg_hr': split_hr,
                            'max_hr': split_max_hr,
                            'power': split_power
                        })
                
                print("-" * 180)
                
                # Analyze split data
                print("\n分段数据分析:")
                print("=" * 80)
                
                if split_analysis:
                    # Calculate average pace per km
                    avg_paces = [s['pace'] for s in split_analysis if s['pace'] > 0]
                    if avg_paces:
                        overall_avg_pace = sum(avg_paces) / len(avg_paces)
                        print(f"整体平均配速: {format_pace(overall_avg_pace)} min/km")
                    
                    # Find fastest and slowest km
                    valid_splits = [s for s in split_analysis if s['pace'] > 0]
                    if valid_splits:
                        fastest_km = min(valid_splits, key=lambda x: x['pace'])
                        slowest_km = max(valid_splits, key=lambda x: x['pace'])
                        print(f"最快公里: 第 {fastest_km['km']} 公里 ({format_pace(fastest_km['pace'])} min/km)")
                        print(f"最慢公里: 第 {slowest_km['km']} 公里 ({format_pace(slowest_km['pace'])} min/km)")
                    
                    # Calculate pace consistency (standard deviation)
                    if len(avg_paces) > 1:
                        import statistics
                        pace_std = statistics.stdev(avg_paces)
                        print(f"配速一致性 (标准差): {pace_std:.3f} min/km")
                    
                    # Analyze heart rate trends
                    hr_data = [s['avg_hr'] for s in split_analysis if s['avg_hr'] > 0]
                    if hr_data:
                        avg_hr = sum(hr_data) / len(hr_data)
                        max_hr = max(hr_data)
                        print(f"平均心率: {avg_hr:.1f} BPM")
                        print(f"最高心率: {max_hr} BPM")
                    
                    # Analyze elevation gain per km
                    total_elevation_gain = sum(s['elevation_gain'] for s in split_analysis)
                    total_distance = sum(s['distance'] for s in split_analysis)
                    if total_distance > 0:
                        elevation_per_km = total_elevation_gain / total_distance
                        print(f"每公里爬升: {elevation_per_km:.1f} 米/km")
                
                # Save split data to file
                with open('latest_activity_segments.json', 'w', encoding='utf-8') as f:
                    json.dump({
                        'activity_info': {
                            'activity_id': activity_id,
                            'activity_name': latest_activity.get('activityName', '未命名'),
                            'start_time': latest_activity.get('startTimeLocal'),
                            'activity_type': latest_activity.get('activityType', {}).get('typeKey', '未知')
                        },
                        'per_km_splits': split_analysis
                    }, f, indent=2, ensure_ascii=False)
                
                print("\n每公里分段数据已保存到 latest_activity_segments.json")
                print("=" * 80)
            else:
                print("未找到每公里分段数据。")
                
                # Try to get activity details as fallback
                print("\n尝试获取活动详细数据...")
                try:
                    if hasattr(garmin_client, 'get_activity_details'):
                        activity = garmin_client.get_activity_details(activity_id)
                        
                        if activity:
                            print("✓ 获取活动详细数据成功")
                            
                            # Print basic activity information
                            print("\n活动基本信息:")
                            print(f"- 名称: {activity.get('activityName', '未命名')}")
                            print(f"- 日期: {activity.get('startTimeLocal', '未知')}")
                            print(f"- 距离: {activity.get('distance', 0) / 1000:.2f} km")
                            print(f"- 时长: {activity.get('duration', 0) / 60:.1f} 分钟")
                            print(f"- 平均配速: {activity.get('duration', 0) / (activity.get('distance', 1) / 1000):.2f} min/km")
                except Exception as e:
                    print(f"获取活动详细数据失败: {e}")
        else:
            print("✗ garth 客户端不可用，无法获取每公里分段数据")
            
            # Try to get activity details as fallback
            print("\n尝试获取活动详细数据...")
            try:
                if hasattr(garmin_client, 'get_activity_details'):
                    activity = garmin_client.get_activity_details(activity_id)
                    
                    if activity:
                        print("✓ 获取活动详细数据成功")
                        
                        # Print basic activity information
                        print("\n活动基本信息:")
                        print(f"- 名称: {activity.get('activityName', '未命名')}")
                        print(f"- 日期: {activity.get('startTimeLocal', '未知')}")
                        print(f"- 距离: {activity.get('distance', 0) / 1000:.2f} km")
                        print(f"- 时长: {activity.get('duration', 0) / 60:.1f} 分钟")
                        print(f"- 平均配速: {activity.get('duration', 0) / (activity.get('distance', 1) / 1000):.2f} min/km")
            except Exception as e:
                print(f"获取活动详细数据失败: {e}")
                
    except Exception as e:
        print(f"获取活动分段数据时出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        get_latest_activity_segments()
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
