#!/usr/bin/env python3
"""
分析心率异常活动的详细数据，包括异常发生点和之前的平均心率
"""

import os
import json
import time
from datetime import datetime, timedelta
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
        
        try:
            # 首先尝试获取活动基本信息
            activity = garmin.get_activity(activity_id)
            
            # 提取活动时间信息
            start_time = activity.get('startTimeLocal')
            if not start_time:
                print(f"  无法获取活动开始时间")
                continue
            
            print(f"  活动开始时间: {start_time}")
            
            # 尝试获取活动的心率数据
            try:
                # 尝试使用不同的方法获取心率数据
                try:
                    # 方法1: get_heart_rates
                    hr_data = garmin.get_heart_rates(activity_id)
                except Exception as e1:
                    print(f"  get_heart_rates 失败: {e1}")
                    try:
                        # 方法2: get_activity_hr_in_timezones
                        hr_data = garmin.get_activity_hr_in_timezones(activity_id)
                    except Exception as e2:
                        print(f"  get_activity_hr_in_timezones 失败: {e2}")
                        try:
                            # 方法3: get_activity_details (可能包含心率数据)
                            activity_details = garmin.get_activity_details(activity_id)
                            hr_data = activity_details.get('heartRateValues')
                        except Exception as e3:
                            print(f"  get_activity_details 失败: {e3}")
                            hr_data = None
                
                if hr_data:
                    # 处理不同格式的心率数据
                    hr_values = []
                    if isinstance(hr_data, dict):
                        if 'heartRateValues' in hr_data:
                            hr_values = hr_data['heartRateValues']
                        elif 'heartRateValuesWithTime' in hr_data:
                            hr_values = hr_data['heartRateValuesWithTime']
                    elif isinstance(hr_data, list):
                        hr_values = hr_data
                    
                    if hr_values:
                        print(f"  获取到 {len(hr_values)} 个心率数据点")
                        
                        # 找到异常心率点
                        anomaly_point = None
                        anomaly_time = None
                        
                        for i, hr_point in enumerate(hr_values):
                            if isinstance(hr_point, list) and len(hr_point) >= 2:
                                timestamp = hr_point[0]
                                hr = hr_point[1]
                                
                                if hr >= 200:
                                    anomaly_point = hr_point
                                    # 计算异常发生时间
                                    anomaly_time = datetime.fromtimestamp(timestamp / 1000)
                                    print(f"  异常心率点: {hr} BPM, 时间: {anomaly_time}")
                                    break
                        
                        if anomaly_point:
                            # 计算异常前3分钟的平均心率
                            anomaly_timestamp = anomaly_point[0]
                            three_minutes_before = anomaly_timestamp - 3 * 60 * 1000  # 3分钟前的时间戳
                            
                            pre_anomaly_hr = []
                            for hr_point in hr_values:
                                if isinstance(hr_point, list) and len(hr_point) >= 2:
                                    timestamp = hr_point[0]
                                    hr = hr_point[1]
                                    
                                    if three_minutes_before <= timestamp < anomaly_timestamp and hr > 0:
                                        pre_anomaly_hr.append(hr)
                            
                            if pre_anomaly_hr:
                                avg_pre_anomaly_hr = sum(pre_anomaly_hr) / len(pre_anomaly_hr)
                                print(f"  异常前3分钟平均心率: {avg_pre_anomaly_hr:.1f} BPM")
                                
                                # 计算异常发生在活动开始后多久
                                start_datetime = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                                time_since_start = anomaly_time - start_datetime
                                minutes_since_start = time_since_start.total_seconds() / 60
                                print(f"  异常发生在活动开始后: {minutes_since_start:.1f} 分钟")
                                
                                # 保存分析结果
                                analysis_results.append({
                                    'activity_id': activity_id,
                                    'activity_name': activity_name,
                                    'date': activity_date,
                                    'max_hr': max_hr,
                                    'anomaly_time': anomaly_time.isoformat(),
                                    'time_since_start_minutes': minutes_since_start,
                                    'pre_anomaly_avg_hr': avg_pre_anomaly_hr,
                                    'pre_anomaly_data_points': len(pre_anomaly_hr)
                                })
                            else:
                                print("  无法计算异常前的平均心率")
                        else:
                            print("  未找到异常心率点")
                    else:
                        print("  未获取到心率数据")
                else:
                    print("  心率数据格式不正确")
                    
            except Exception as e:
                print(f"  获取心率数据失败: {e}")
                
        except Exception as e:
            print(f"  获取活动详情失败: {e}")
        
        # 避免API速率限制
        time.sleep(2)
    
    # 保存分析结果
    if analysis_results:
        output_file = "anomaly_hr_analysis.json"
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
    report_file = "anomaly_hr_detailed_analysis_report.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 心率异常详细分析报告\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"分析活动数量: {len(results)}\n\n")
        f.write("## 异常心率分析\n\n")
        
        for result in results:
            f.write(f"### {result['activity_name']}\n")
            f.write(f"- 活动ID: {result['activity_id']}\n")
            f.write(f"- 日期: {result['date']}\n")
            f.write(f"- 最大心率: {result['max_hr']} BPM\n")
            f.write(f"- 异常发生时间: {result['anomaly_time']}\n")
            f.write(f"- 异常发生在活动开始后: {result['time_since_start_minutes']:.1f} 分钟\n")
            f.write(f"- 异常前3分钟平均心率: {result['pre_anomaly_avg_hr']:.1f} BPM\n")
            f.write(f"- 异常前数据点数量: {result['pre_anomaly_data_points']}\n\n")
        
        # 统计分析
        if results:
            avg_pre_anomaly = sum(r['pre_anomaly_avg_hr'] for r in results) / len(results)
            avg_time_since_start = sum(r['time_since_start_minutes'] for r in results) / len(results)
            
            f.write("## 统计分析\n\n")
            f.write(f"- 异常前平均心率: {avg_pre_anomaly:.1f} BPM\n")
            f.write(f"- 异常发生平均时间: 活动开始后 {avg_time_since_start:.1f} 分钟\n\n")
    
    print(f"分析报告已生成: {report_file}")


if __name__ == "__main__":
    analyze_heart_rate_anomalies()
