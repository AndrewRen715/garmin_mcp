#!/usr/bin/env python3
"""
分析hr_anomalies.json中的活动split数据
"""

import json
import sys
import os
import time
from garminconnect import Garmin

def get_garmin_client():
    """
    获取Garmin客户端实例（中国区）
    """
    try:
        token_path = os.path.expanduser("~/.garminconnect_cn")
        
        # 尝试使用token登录
        if os.path.exists(token_path):
            print(f"尝试使用现有token登录: {token_path}")
            garmin = Garmin(is_cn=True)
            garmin.login(token_path)
            print("使用token登录成功！")
        else:
            print("错误: 未找到中国区token文件")
            return None
        
        return garmin
        
    except Exception as e:
        print(f"错误: {e}")
        return None

def analyze_activity_splits(garmin_client, activity_id, activity_name, max_hr, date):
    """
    分析活动的split数据
    
    Args:
        garmin_client: Garmin客户端实例
        activity_id: 活动ID
        activity_name: 活动名称
        max_hr: 最大心率
        date: 活动日期
    
    Returns:
        dict: 分析结果
    """
    try:
        # 获取活动的split数据
        splits = garmin_client.get_activity_splits(activity_id)
        
        if not splits or 'lapDTOs' not in splits:
            return {
                'success': False,
                'error': '无法获取split数据'
            }
        
        laps = splits.get('lapDTOs', [])
        
        if not laps:
            return {
                'success': False,
                'error': 'split数据为空'
            }
        
        # 分析每个split的心率数据
        split_hr_data = []
        for i, lap in enumerate(laps):
            lap_data = {
                'lap_number': lap.get('lapIndex', i+1),
                'distance_meters': lap.get('distance'),
                'duration_seconds': lap.get('duration'),
                'avg_hr': lap.get('averageHR'),
                'max_hr': lap.get('maxHR')
            }
            split_hr_data.append(lap_data)
        
        # 找到最大心率所在的split
        max_hr_split = None
        for i, lap in enumerate(laps):
            lap_max_hr = lap.get('maxHR')
            if lap_max_hr == max_hr:
                max_hr_split = i + 1
                break
        
        if not max_hr_split:
            # 找不到确切的最大心率split，使用最高心率的split
            max_hr_split = 1
            highest_hr = 0
            for i, lap in enumerate(laps):
                lap_max_hr = lap.get('maxHR', 0)
                if lap_max_hr > highest_hr:
                    highest_hr = lap_max_hr
                    max_hr_split = i + 1
        
        # 计算前一个split的平均心率
        previous_split_avg_hr = 0
        if max_hr_split > 1:
            previous_split = laps[max_hr_split - 2]
            previous_split_avg_hr = previous_split.get('averageHR', 0)
        
        return {
            'success': True,
            'activity_id': activity_id,
            'activity_name': activity_name,
            'date': date,
            'max_hr': max_hr,
            'max_hr_split': max_hr_split,
            'previous_split_avg_hr': previous_split_avg_hr,
            'total_splits': len(laps),
            'split_data': split_hr_data
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """
    主函数
    """
    print("=" * 80)
    print("Garmin Connect 心率异常活动Split分析工具")
    print("=" * 80)
    print("分析hr_anomalies.json中的活动split数据")
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
    
    # 获取Garmin客户端
    garmin_client = get_garmin_client()
    
    if not garmin_client:
        print("\n无法初始化Garmin客户端，程序退出")
        return
    
    # 分析每个异常活动的split数据
    results = []
    total_analyzed = 0
    success_count = 0
    
    print("\n开始分析异常活动...")
    print("=" * 80)
    print(f"{'活动ID':<12} {'日期':<10} {'最大心率':<8} {'最大心率Split':<12} {'前一个Split平均心率':<15} {'状态':<10}")
    print("=" * 80)
    
    for anomaly in anomalies:
        activity_id = anomaly.get('id')
        date = anomaly.get('date')
        activity_name = anomaly.get('name')
        max_hr = anomaly.get('max_hr')
        
        print(f"分析活动: {activity_id} ({date})")
        
        result = analyze_activity_splits(garmin_client, activity_id, activity_name, max_hr, date)
        result['date'] = date
        results.append(result)
        
        total_analyzed += 1
        
        if result['success']:
            success_count += 1
            status = "成功"
            max_hr_split = result['max_hr_split']
            prev_avg_hr = f"{result['previous_split_avg_hr']} BPM"
        else:
            status = "失败"
            max_hr_split = "-"
            prev_avg_hr = "-"
        
        print(f"{str(activity_id):<12} {date:<10} {max_hr:<8} {max_hr_split:<12} {prev_avg_hr:<15} {status:<10}")
        
        # 避免API调用过于频繁
        time.sleep(2)
    
    # 保存分析结果
    analysis_data = {
        'total_anomalies': len(anomalies),
        'total_analyzed': total_analyzed,
        'success_count': success_count,
        'analysis_date': time.strftime("%Y-%m-%d %H:%M:%S"),
        'results': results
    }
    
    try:
        with open('anomaly_split_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        print(f"\n分析结果已保存到: anomaly_split_analysis.json")
    except Exception as e:
        print(f"保存分析结果失败: {e}")
    
    # 生成统计信息
    print("\n" + "=" * 80)
    print("分析统计")
    print("=" * 80)
    print(f"总异常活动数: {len(anomalies)}")
    print(f"成功分析: {success_count}")
    print(f"失败分析: {total_analyzed - success_count}")
    
    # 计算平均前一个split心率
    successful_results = [r for r in results if r['success']]
    if successful_results:
        avg_prev_split_hr = sum(r['previous_split_avg_hr'] for r in successful_results) / len(successful_results)
        print(f"\n平均前一个split心率: {avg_prev_split_hr:.1f} BPM")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
