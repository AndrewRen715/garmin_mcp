#!/usr/bin/env python3
"""
测试获取最近活动的详细数据
"""

import sys
import os
import time

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 尝试导入garmin_mcp
try:
    from garmin_mcp import init_api
    mcp_available = True
except ImportError:
    mcp_available = False

def main():
    """
    主函数
    """
    print("=" * 80)
    print("测试获取最近活动的详细数据")
    print("=" * 80)
    
    # 检查garmin_mcp是否可用
    if not mcp_available:
        print("\ngarmin_mcp模块未找到")
        return
    
    # 获取Garmin客户端
    try:
        os.environ['GARMIN_CN'] = 'true'
        print("尝试初始化Garmin客户端...")
        client = init_api("", "", is_cn=True)
        print("登录成功！")
        
        # 获取最近的活动
        print("\n获取最近的活动...")
        activities = client.get_activities(0, 10)
        print(f"找到{len(activities)}个最近活动")
        
        # 显示最近活动的信息
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
            
            # 尝试获取活动详情
            if activity_id:
                print("\n尝试获取活动详情...")
                try:
                    details = client.get_activity_details(activity_id)
                    print("成功获取活动详情")
                    print(f"活动时长: {details.get('duration', 0)/60:.1f}分钟")
                    
                    # 尝试获取心率数据
                    print("\n尝试获取心率数据...")
                    hr_data = client.get_activity_heart_rates(activity_id)
                    if hr_data and 'heartRateValues' in hr_data:
                        print(f"成功获取心率数据，共{len(hr_data['heartRateValues'])}个数据点")
                        # 显示前几个数据点
                        for j, (timestamp, hr) in enumerate(hr_data['heartRateValues'][:5]):
                            print(f"  {j+1}: {timestamp}秒 - {hr} BPM")
                    else:
                        print("无法获取心率数据")
                        
                except Exception as e:
                    print(f"获取活动详情失败: {e}")
            
            # 避免API调用过于频繁
            time.sleep(2)
            
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
