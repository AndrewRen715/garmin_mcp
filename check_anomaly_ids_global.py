#!/usr/bin/env python3
"""
检查异常心率活动ID是否在国际区存在
"""

import json
import sys
import os
import time
from garminconnect import Garmin

def get_global_garmin_client():
    """
    获取国际区Garmin客户端实例
    """
    try:
        token_path = os.path.expanduser("~/.garminconnect")
        
        # 尝试使用token登录
        if os.path.exists(token_path):
            print(f"尝试使用国际区现有token登录: {token_path}")
            garmin = Garmin(is_cn=False)
            garmin.login(token_path)
            print("使用国际区token登录成功！")
        else:
            print("警告: 未找到国际区token文件，将尝试使用中国区token")
            # 尝试使用中国区token
            cn_token_path = os.path.expanduser("~/.garminconnect_cn")
            if os.path.exists(cn_token_path):
                print(f"尝试使用中国区token登录国际区: {cn_token_path}")
                garmin = Garmin(is_cn=False)
                try:
                    garmin.login(cn_token_path)
                    print("使用中国区token登录国际区成功！")
                except Exception as e:
                    print(f"使用中国区token登录国际区失败: {e}")
                    return None
            else:
                print("错误: 未找到任何token文件")
                return None
        
        return garmin
        
    except Exception as e:
        print(f"错误: {e}")
        return None

def check_activity(garmin_client, activity_id, date, activity_name, max_hr):
    """
    检查活动是否存在并获取详细信息
    """
    try:
        # 尝试获取活动详情
        activity = garmin_client.get_activity(activity_id)
        
        # 提取时间戳信息
        start_time_local = activity.get('startTimeLocal')
        start_time_gmt = activity.get('startTimeGMT')
        
        # 提取其他相关信息
        activity_type = activity.get('activityType', {}).get('typeKey')
        duration = activity.get('duration')
        distance = activity.get('distance')
        
        return {
            'success': True,
            'activity_id': activity_id,
            'date': date,
            'activity_name': activity_name,
            'max_hr': max_hr,
            'start_time_local': start_time_local,
            'start_time_gmt': start_time_gmt,
            'activity_type': activity_type,
            'duration': duration,
            'distance': distance
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'activity_id': activity_id,
            'date': date,
            'activity_name': activity_name,
            'max_hr': max_hr
        }

def main():
    """
    主函数
    """
    print("=" * 80)
    print("Garmin Connect 异常活动ID检查工具")
    print("=" * 80)
    print("检查异常心率活动ID是否在国际区存在")
    print("=" * 80)
    
    # 读取异常活动文件
    try:
        with open('hr_anomalies.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        anomalies = data.get('anomalies', [])
        print(f"\n从hr_anomalies.json读取到{len(anomalies)}个异常活动")
        
    except Exception as e:
        print(f"读取hr_anomalies.json失败: {e}")
        return
    
    # 获取国际区Garmin客户端
    garmin_client = get_global_garmin_client()
    
    if not garmin_client:
        print("\n无法初始化Garmin客户端，程序退出")
        return
    
    # 检查每个异常活动
    results = []
    total_checked = 0
    success_count = 0
    
    print("\n开始检查异常活动...")
    print("=" * 80)
    print(f"{'活动ID':<12} {'日期':<10} {'最大心率':<8} {'时间戳':<25} {'状态':<10}")
    print("=" * 80)
    
    for anomaly in anomalies:
        activity_id = anomaly.get('id')
        date = anomaly.get('date')
        activity_name = anomaly.get('name')
        max_hr = anomaly.get('max_hr')
        
        print(f"检查活动: {activity_id} ({date})")
        
        result = check_activity(garmin_client, activity_id, date, activity_name, max_hr)
        results.append(result)
        
        total_checked += 1
        
        if result['success']:
            success_count += 1
            status = "存在"
            timestamp = result.get('start_time_local', 'N/A') or 'N/A'
        else:
            status = "不存在"
            timestamp = "N/A"
        
        print(f"{str(activity_id):<12} {date:<10} {max_hr:<8} {str(timestamp):<25} {status:<10}")
        
        # 避免API调用过于频繁
        time.sleep(2)
    
    # 保存检查结果
    check_data = {
        'total_anomalies': len(anomalies),
        'total_checked': total_checked,
        'success_count': success_count,
        'check_date': time.strftime("%Y-%m-%d %H:%M:%S"),
        'results': results
    }
    
    try:
        with open('anomaly_id_check.json', 'w', encoding='utf-8') as f:
            json.dump(check_data, f, indent=2, ensure_ascii=False)
        print(f"\n检查结果已保存到: anomaly_id_check.json")
    except Exception as e:
        print(f"保存检查结果失败: {e}")
    
    # 生成统计信息
    print("\n" + "=" * 80)
    print("检查统计")
    print("=" * 80)
    print(f"总异常活动数: {len(anomalies)}")
    print(f"在国际区存在: {success_count}")
    print(f"在国际区不存在: {total_checked - success_count}")
    
    print("\n" + "=" * 80)
    print("检查完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
