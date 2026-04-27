#!/usr/bin/env python3
"""
获取最新活动的每公里分段数据
"""

import json
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

def main():
    """获取最新活动的每公里分段数据"""
    print("获取最新活动的每公里分段数据...")
    
    # Initialize Garmin client
    try:
        garmin_client = init_api(None, None, is_cn=True)
        print("✓ 客户端初始化成功")
    except Exception as e:
        print(f"✗ 客户端初始化失败: {e}")
        return
    
    # Get recent activities
    try:
        activities = []
        start = 0
        limit = 10
        
        while True:
            page = garmin_client.get_activities(start, limit)
            if not page:
                break
            activities.extend(page)
            start += limit
            if len(page) < limit:
                break
        
        if not activities:
            print("未找到活动")
            return
        
        # Get most recent activity
        activities.sort(key=lambda x: x.get('startTimeLocal', ''), reverse=True)
        latest = activities[0]
        activity_id = latest.get('activityId')
        
        print(f"最新活动: {latest.get('activityName')}")
        print(f"活动ID: {activity_id}")
        
        # Try to get splits via laps endpoint
        if hasattr(garmin_client, 'garth'):
            print("\n获取每公里分段数据...")
            
            # Try laps endpoint
            endpoint = f"activity-service/activity/{activity_id}/laps"
            try:
                response = garmin_client.garth.get("connectapi", endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ 获取数据成功")
                    
                    if 'lapDTOs' in data:
                        laps = data['lapDTOs']
                        print(f"找到 {len(laps)} 个分段")
                        
                        # Filter for per-kilometer splits
                        km_splits = []
                        for i, lap in enumerate(laps):
                            distance = lap.get('distance', 0) / 1000
                            if 0.9 <= distance <= 1.1:
                                km_splits.append({
                                    'km': i+1,
                                    'distance': distance,
                                    'time': lap.get('duration', 0) / 60,
                                    'pace': (lap.get('duration', 0) / 60) / distance if distance > 0 else 0,
                                    'avg_hr': lap.get('averageHR', 0),
                                    'max_hr': lap.get('maxHR', 0),
                                    'elevation_gain': lap.get('elevationGain', 0)
                                })
                        
                        if km_splits:
                            print(f"\n识别到 {len(km_splits)} 个每公里分段:")
                            print("公里 | 距离(km) | 时间(min) | 配速(min/km) | 心率(BPM) | 爬升(m)")
                            print("-" * 80)
                            
                            for split in km_splits:
                                print(f"{split['km']:3d} | {split['distance']:9.2f} | {split['time']:9.2f} | {split['pace']:11.2f} | {split['avg_hr']:8.1f} | {split['elevation_gain']:6.0f}")
                            
                            # Save to file
                            with open('km_splits.json', 'w') as f:
                                json.dump({
                                    'activity': latest,
                                    'km_splits': km_splits
                                }, f, indent=2)
                            
                            print("\n数据已保存到 km_splits.json")
                        else:
                            print("未找到每公里分段")
                    else:
                        print("无lapDTOs数据")
                else:
                    print(f"获取失败: 状态码 {response.status_code}")
            except Exception as e:
                print(f"错误: {e}")
        else:
            print("garth客户端不可用")
            
    except Exception as e:
        print(f"获取活动失败: {e}")

if __name__ == "__main__":
    main()