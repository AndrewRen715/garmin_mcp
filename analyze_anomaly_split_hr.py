#!/usr/bin/env python3
"""
分析心率异常活动的split数据，计算异常所在split和前一个split的平均心率
"""

import os
import json
import time
from datetime import datetime
from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectAuthenticationError


def load_tokens():
    """加载全球区的token"""
    token_dir = os.path.expanduser("~/.garminconnect")
    
    if not os.path.exists(token_dir):
        print("Token目录不存在，请先运行 reauth.py 进行认证")
        return None
    
    # 检查是否存在token文件
    oauth2_token = os.path.join(token_dir, "oauth2_token.json")
    if not os.path.exists(oauth2_token):
        print("Token文件不存在，请先运行 reauth.py 进行认证")
        return None
    
    return {"token_store": token_dir}


def analyze_activity_splits(garmin, activity_id, activity_name, max_hr):
    """分析活动的split数据"""
    try:
        # 获取活动的split数据
        splits = garmin.get_activity_splits(activity_id)
        
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


def analyze_heart_rate_anomalies():
    """分析心率异常活动"""
    # 加载异常数据
    anomalies_file = "hr_anomalies.json"
    if not os.path.exists(anomalies_file):
        print("心率异常数据文件不存在")
        return
    
    with open(anomalies_file, 'r', encoding='utf-8') as f:
        anomalies_data = json.load(f)
    
    # 加载token
    tokens = load_tokens()
    if not tokens:
        return
    
    # 初始化Garmin客户端（全球区）
    try:
        # 直接使用token存储目录登录
        garmin = Garmin(is_cn=False)
        garmin.login(tokens['token_store'])
        print("登录全球区Garmin Connect成功")
    except (GarminConnectConnectionError, GarminConnectAuthenticationError) as e:
        print(f"登录失败: {e}")
        return
    
    analysis_results = []
    
    # 分析每个异常活动
    for anomaly in anomalies_data['anomalies']:
        activity_id = anomaly['id']
        activity_date = anomaly['date']
        activity_name = anomaly['name']
        max_hr = anomaly['max_hr']
        
        print(f"\n分析活动: {activity_name} (ID: {activity_id}, 日期: {activity_date}, 最大心率: {max_hr} BPM)")
        
        # 分析split数据
        result = analyze_activity_splits(garmin, activity_id, activity_name, max_hr)
        
        if result['success']:
            print(f"  成功获取split数据")
            print(f"  总split数: {result['total_splits']}")
            print(f"  最大心率所在split: {result['max_hr_split']}")
            print(f"  前一个split平均心率: {result['previous_split_avg_hr']} BPM")
            
            # 保存分析结果
            analysis_results.append({
                'activity_id': activity_id,
                'activity_name': activity_name,
                'date': activity_date,
                'max_hr': max_hr,
                'max_hr_split': result['max_hr_split'],
                'previous_split_avg_hr': result['previous_split_avg_hr'],
                'total_splits': result['total_splits'],
                'split_data': result['split_data']
            })
        else:
            print(f"  分析失败: {result['error']}")
        
        # 避免API速率限制
        time.sleep(2)
    
    # 保存分析结果
    if analysis_results:
        output_file = "anomaly_split_hr_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_date': datetime.now().isoformat(),
                'total_analyzed': len(analysis_results),
                'results': analysis_results
            }, f, ensure_ascii=False, indent=2)
        print(f"\n分析完成，结果已保存到 {output_file}")
        
        # 生成分析报告
        generate_report(analysis_results)
    else:
        print("\n没有成功分析的活动")


def generate_report(results):
    """生成分析报告"""
    report_file = "anomaly_split_hr_analysis_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 心率异常Split分析报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"分析活动数量: {len(results)}\n\n")
        f.write("## 异常心率分析\n\n")
        
        for result in results:
            f.write(f"### {result['activity_name']}\n")
            f.write(f"- 活动ID: {result['activity_id']}\n")
            f.write(f"- 日期: {result['date']}\n")
            f.write(f"- 最大心率: {result['max_hr']} BPM\n")
            f.write(f"- 总split数: {result['total_splits']}\n")
            f.write(f"- 最大心率所在split: {result['max_hr_split']}\n")
            f.write(f"- 前一个split平均心率: {result['previous_split_avg_hr']} BPM\n\n")
        
        # 统计分析
        if results:
            avg_previous_hr = sum(r['previous_split_avg_hr'] for r in results) / len(results)
            avg_max_hr_split = sum(r['max_hr_split'] for r in results) / len(results)
            
            f.write("## 统计分析\n\n")
            f.write(f"- 平均前一个split心率: {avg_previous_hr:.1f} BPM\n")
            f.write(f"- 平均最大心率所在split: {avg_max_hr_split:.1f}\n\n")
    
    print(f"分析报告已生成: {report_file}")


if __name__ == "__main__":
    analyze_heart_rate_anomalies()
