#!/usr/bin/env python3
"""
使用国际区API分析异常心率活动的详细数据
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
            print("错误: 未找到国际区token文件")
            return None
        
        return garmin
        
    except Exception as e:
        print(f"错误: {e}")
        return None

def analyze_hr_anomaly(garmin_client, activity_id, date, activity_name, max_hr):
    """
    分析单个心率异常活动
    """
    try:
        # 获取活动详情
        activity = garmin_client.get_activity(activity_id)
        
        # 获取活动时长
        duration = activity.get('duration', 0)
        
        # 尝试获取心率数据
        try:
            # 尝试使用get_activity_hr_in_timezones方法
            hr_data = garmin_client.get_activity_hr_in_timezones(activity_id)
        except Exception as e:
            print(f"get_activity_hr_in_timezones失败: {e}")
            # 尝试使用其他方法
            try:
                # 尝试使用get_activity方法获取详细信息，看是否包含心率数据
                activity_details = garmin_client.get_activity(activity_id)
                # 检查是否有心率相关数据
                if 'heartRateValues' in activity_details:
                    hr_data = {'heartRateValues': activity_details['heartRateValues']}
                else:
                    return {
                        'success': False,
                        'error': '活动详情中没有心率数据'
                    }
            except Exception as e2:
                print(f"获取活动详情也失败: {e2}")
                return {
                    'success': False,
                    'error': '无法获取心率数据'
                }
        
        if not hr_data:
            return {
                'success': False,
                'error': '心率数据为空'
            }
        
        # 处理心率数据
        heart_rate_values = []
        
        # 检查数据格式
        if isinstance(hr_data, dict) and 'heartRateValues' in hr_data:
            heart_rate_values = hr_data['heartRateValues']
        elif isinstance(hr_data, list):
            # 处理心率时区数据
            for item in hr_data:
                if isinstance(item, dict) and 'heartRate' in item and 'timeOffset' in item:
                    heart_rate_values.append([item['timeOffset'], item['heartRate']])
        
        if not heart_rate_values:
            return {
                'success': False,
                'error': '无法解析心率数据'
            }
        
        # 找到异常心率的发生点
        anomaly_time = None
        for timestamp, hr in heart_rate_values:
            if hr == max_hr:
                anomaly_time = timestamp
                break
        
        if not anomaly_time:
            # 找不到确切的异常心率，使用最高心率的时间点
            anomaly_time = max(heart_rate_values, key=lambda x: x[1])[0]
        
        # 计算异常前一段正常时间的平均心率
        # 取异常前3分钟的数据
        pre_anomaly_time = max(0, anomaly_time - 180)  # 180秒 = 3分钟
        pre_anomaly_hr = []
        
        for timestamp, hr in heart_rate_values:
            if pre_anomaly_time <= timestamp < anomaly_time:
                pre_anomaly_hr.append(hr)
        
        if pre_anomaly_hr:
            avg_pre_anomaly_hr = sum(pre_anomaly_hr) / len(pre_anomaly_hr)
        else:
            avg_pre_anomaly_hr = 0
        
        # 计算异常发生的时间点（相对于活动开始）
        anomaly_time_minutes = anomaly_time / 60.0
        
        return {
            'success': True,
            'activity_id': activity_id,
            'date': date,
            'activity_name': activity_name,
            'max_hr': max_hr,
            'anomaly_time_seconds': anomaly_time,
            'anomaly_time_minutes': round(anomaly_time_minutes, 1),
            'pre_anomaly_avg_hr': round(avg_pre_anomaly_hr, 1),
            'pre_anomaly_data_points': len(pre_anomaly_hr),
            'activity_duration': duration / 60.0
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
    print("Garmin Connect 异常心率活动详细分析工具")
    print("=" * 80)
    print("分析异常心率的发生点及之前的平均心率")
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
    
    # 分析每个异常活动
    results = []
    total_analyzed = 0
    success_count = 0
    
    print("\n开始分析异常活动...")
    print("=" * 80)
    print(f"{'活动ID':<12} {'日期':<10} {'最大心率':<8} {'异常时间点':<10} {'前3分钟平均心率':<15} {'状态':<10}")
    print("=" * 80)
    
    for anomaly in anomalies:
        activity_id = anomaly.get('id')
        date = anomaly.get('date')
        activity_name = anomaly.get('name')
        max_hr = anomaly.get('max_hr')
        
        print(f"分析活动: {activity_id} ({date})")
        
        result = analyze_hr_anomaly(garmin_client, activity_id, date, activity_name, max_hr)
        results.append(result)
        
        total_analyzed += 1
        
        if result['success']:
            success_count += 1
            status = "成功"
            anomaly_time = f"{result['anomaly_time_minutes']}分钟"
            pre_avg_hr = f"{result['pre_anomaly_avg_hr']} BPM"
        else:
            status = "失败"
            anomaly_time = "-"
            pre_avg_hr = "-"
        
        print(f"{str(activity_id):<12} {date:<10} {max_hr:<8} {anomaly_time:<10} {pre_avg_hr:<15} {status:<10}")
        
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
        with open('anomaly_hr_analysis_global.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        print(f"\n分析结果已保存到: anomaly_hr_analysis_global.json")
    except Exception as e:
        print(f"保存分析结果失败: {e}")
    
    # 生成统计信息
    print("\n" + "=" * 80)
    print("分析统计")
    print("=" * 80)
    print(f"总异常活动数: {len(anomalies)}")
    print(f"成功分析: {success_count}")
    print(f"失败分析: {total_analyzed - success_count}")
    
    # 计算平均值
    successful_results = [r for r in results if r['success']]
    if successful_results:
        avg_anomaly_time = sum(r['anomaly_time_minutes'] for r in successful_results) / len(successful_results)
        avg_pre_hr = sum(r['pre_anomaly_avg_hr'] for r in successful_results) / len(successful_results)
        
        print(f"\n平均异常发生时间: {avg_anomaly_time:.1f} 分钟")
        print(f"平均前3分钟心率: {avg_pre_hr:.1f} BPM")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
