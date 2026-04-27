#!/usr/bin/env python3
"""
测试获取最近活动的心率数据
"""

import sys
import os
import time
from garminconnect import Garmin

def main():
    """
    主函数
    """
    print("=" * 80)
    print("测试获取最近活动的心率数据")
    print("=" * 80)
    
    # 尝试初始化Garmin客户端
    try:
        token_path = os.path.expanduser("~/.garminconnect_cn")
        print(f"尝试使用token登录: {token_path}")
        
        garmin = Garmin(is_cn=True)
        garmin.login(token_path)
        print("登录成功！")
        
        # 获取最近的活动
        print("\n获取最近的活动...")
        activities = garmin.get_activities(0, 5)
        print(f"找到{len(activities)}个最近活动")
        
        # 显示最近活动的信息并尝试获取心率数据
        for i, activity in enumerate(activities):
            activity_id = activity.get('activityId')
            activity_name = activity.get('activityName')
            start_time = activity.get('startTimeLocal')
            max_hr = activity.get('maxHR')
            
            print(f"\n活动 {i+1}:")
            print(f"ID: {activity_id}")
            print(f"名称: {activity_name}")
            print(f"开始时间: {start_time}")
            print(f"最大心率: {max_hr}")
            
            # 尝试获取心率数据
            if activity_id:
                print("\n尝试获取心率数据...")
                try:
                    # 尝试使用不同的方法获取心率数据
                    methods = ['get_heart_rates', 'get_activity_hr_in_timezones']
                    
                    for method_name in methods:
                        print(f"尝试方法: {method_name}")
                        try:
                            method = getattr(garmin, method_name)
                            hr_data = method(activity_id)
                            print(f"成功获取心率数据")
                            
                            # 显示数据格式
                            if isinstance(hr_data, dict):
                                print(f"数据类型: dict")
                                print(f"键: {list(hr_data.keys())}")
                                if 'heartRateValues' in hr_data:
                                    print(f"心率数据点数量: {len(hr_data['heartRateValues'])}")
                                    if hr_data['heartRateValues']:
                                        print(f"前5个数据点: {hr_data['heartRateValues'][:5]}")
                            elif isinstance(hr_data, list):
                                print(f"数据类型: list")
                                print(f"数据点数量: {len(hr_data)}")
                                if hr_data:
                                    print(f"前5个数据点: {hr_data[:5]}")
                            break
                        except Exception as e:
                            print(f"{method_name}失败: {e}")
                            continue
                    
                except Exception as e:
                    print(f"获取心率数据失败: {e}")
            
            # 避免API调用过于频繁
            time.sleep(2)
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
