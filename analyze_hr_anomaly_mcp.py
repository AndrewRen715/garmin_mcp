#!/usr/bin/env python3
"""
使用garmin_mcp库分析心率异常活动的详细数据
包括异常前5分钟的平均心率和异常触发时间
"""

import json
import sys
import os
import time
from datetime import datetime, timedelta

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# 尝试导入garmin_mcp
try:
    from garmin_mcp import init_api
    mcp_available = True
except ImportError:
    mcp_available = False

def get_garmin_client():
    """
    获取Garmin客户端实例（中国区）
    """
    if not mcp_available:
        print("错误: 未找到garmin_mcp模块")
        return None
    
    try:
        os.environ['GARMIN_CN'] = 'true'
        # 使用已存储的token
        token_path = os.path.expanduser("~/.garminconnect_cn")
        if os.path.exists(token_path):
            print(f"尝试使用现有token登录: {token_path}")
        
        # 传空密码，让它用存储的token
        client = init_api("", "", is_cn=True)
        print("使用token登录成功！")
        return client
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

def analyze_hr_anomaly(client, activity_id, max_hr):
    """
    分析单个心率异常活动
    
    Args:
        client: Garmin客户端实例
        activity_id: 活动ID
        max_hr: 最大心率
    
    Returns:
        dict: 分析结果
    """
    try:
        # 获取活动的详细信息
        activity = client.get_activity_details(activity_id)
        
        # 获取活动时长（秒）
        duration = activity.get('duration', 0)
        
        # 获取心率数据
        hr_data = client.get_activity_heart_rates(activity_id)
        
        if not hr_data or 'heartRateValues' not in hr_data:
            return {
                'success': False,
                'error': '无法获取心率数据'
            }
        
        heart_rate_values = hr_data['heartRateValues']
        
        if not heart_rate_values:
            return {
                'success': False,
                'error': '心率数据为空'
            }
        
        # 找到最大心率的时间点
        max_hr_time = None
        for timestamp, hr in heart_rate_values:
            if hr == max_hr:
                max_hr_time = timestamp
                break
        
        if not max_hr_time:
            # 找不到确切的最大心率时间点，使用最高心率的时间点
            max_hr_time = max(heart_rate_values, key=lambda x: x[1])[0]
        
        # 计算异常触发时间（分钟）
        anomaly_time_minutes = max_hr_time / 60.0
        
        # 计算异常前5分钟的时间范围
        start_time = max(0, max_hr_time - 300)  # 300秒 = 5分钟
        
        # 收集异常前5分钟的心率数据
        pre_anomaly_hr = []
        for timestamp, hr in heart_rate_values:
            if start_time <= timestamp < max_hr_time:
                pre_anomaly_hr.append(hr)
        
        # 计算平均心率
        if pre_anomaly_hr:
            avg_pre_anomaly_hr = sum(pre_anomaly_hr) / len(pre_anomaly_hr)
        else:
            avg_pre_anomaly_hr = 0
        
        return {
            'success': True,
            'activity_id': activity_id,
            'max_hr': max_hr,
            'anomaly_time_minutes': round(anomaly_time_minutes, 1),
            'pre_anomaly_avg_hr': round(avg_pre_anomaly_hr, 1),
            'pre_anomaly_data_points': len(pre_anomaly_hr),
            'activity_duration': duration / 60.0  # 转换为分钟
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
    print("Garmin Connect 心率异常详细分析工具 (使用garmin_mcp)")
    print("=" * 80)
    print("分析异常心率前5分钟的平均心率和异常触发时间")
    print("=" * 80)
    
    # 检查garmin_mcp是否可用
    if not mcp_available:
        print("\ngarmin_mcp模块未找到，无法分析详细数据")
        return
    
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
    
    # 分析每个异常活动
    results = []
    total_analyzed = 0
    success_count = 0
    
    print("\n开始分析异常活动...")
    print("=" * 80)
    print(f"{'活动ID':<12} {'日期':<10} {'最大心率':<8} {'异常时间':<10} {'前5分钟平均心率':<15} {'状态':<10}")
    print("=" * 80)
    
    for anomaly in anomalies:
        activity_id = anomaly.get('id')
        date = anomaly.get('date')
        max_hr = anomaly.get('max_hr')
        
        print(f"分析活动: {activity_id} ({date})")
        
        result = analyze_hr_anomaly(garmin_client, activity_id, max_hr)
        result['date'] = date
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
        time.sleep(1)
    
    # 保存分析结果
    analysis_data = {
        'total_anomalies': len(anomalies),
        'total_analyzed': total_analyzed,
        'success_count': success_count,
        'analysis_date': time.strftime("%Y-%m-%d %H:%M:%S"),
        'results': results
    }
    
    try:
        with open('hr_anomaly_details_mcp.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        print(f"\n分析结果已保存到: hr_anomaly_details_mcp.json")
    except Exception as e:
        print(f"保存分析结果失败: {e}")
    
    # 生成统计信息
    print("\n" + "=" * 80)
    print("分析统计")
    print("=" * 80)
    print(f"总异常活动数: {len(anomalies)}")
    print(f"成功分析: {success_count}")
    print(f"失败分析: {total_analyzed - success_count}")
    
    # 计算平均异常触发时间和平均前5分钟心率
    successful_results = [r for r in results if r['success']]
    if successful_results:
        avg_anomaly_time = sum(r['anomaly_time_minutes'] for r in successful_results) / len(successful_results)
        avg_pre_hr = sum(r['pre_anomaly_avg_hr'] for r in successful_results) / len(successful_results)
        
        print(f"\n平均异常触发时间: {avg_anomaly_time:.1f} 分钟")
        print(f"平均前5分钟心率: {avg_pre_hr:.1f} BPM")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)

if __name__ == "__main__":
    main()
