#!/usr/bin/env python3
"""
查找Garmin Connect中所有最大心率>200 BPM的活动
"""
import json
import sys
import os
from pathlib import Path
import time

# 尝试导入garminconnect库
try:
    from garminconnect import Garmin
    import getpass
    garmin_available = True
except ImportError:
    garmin_available = False


def get_token_path():
    """
    获取token存储路径
    """
    return os.getenv("GARMINTOKENS") or "~/.garminconnect"


def token_exists():
    """
    检查token是否存在
    """
    token_path = get_token_path()
    expanded_path = Path(os.path.expanduser(token_path))
    return expanded_path.exists()


def get_garmin_client():
    """
    获取Garmin客户端实例
    """
    if not garmin_available:
        print("错误: 未安装garminconnect库。请使用 'pip install garminconnect' 安装。")
        return None
    
    try:
        token_path = get_token_path()
        expanded_token_path = os.path.expanduser(token_path)
        
        # 首先尝试使用token登录
        if token_exists():
            print(f"尝试使用现有token登录: {expanded_token_path}")
            garmin = Garmin()
            garmin.login(expanded_token_path)
            print("使用token登录成功！")
        else:
            # 如果token不存在，要求用户输入凭据
            print("未找到现有token，需要输入凭据登录...")
            email = input("请输入您的Garmin Connect邮箱: ")
            password = getpass.getpass("请输入您的Garmin Connect密码: ")
            
            # 初始化Garmin客户端
            print("正在登录Garmin Connect...")
            garmin = Garmin(email, password)
            garmin.login()
            
            # 保存token
            print(f"正在保存token到: {expanded_token_path}")
            garmin.garth.dump(expanded_token_path)
            print("token保存成功，下次登录将自动使用！")
        
        return garmin
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None


def find_hr_anomalies(garmin_client, max_hr_threshold=200):
    """
    查找所有最大心率>max_hr_threshold的活动
    
    Args:
        garmin_client: Garmin客户端实例
        max_hr_threshold: 最大心率阈值
    
    Returns:
        list: 包含异常活动信息的列表
    """
    if not garmin_client:
        print("错误: Garmin客户端未初始化")
        return []
    
    print(f"开始查找最大心率>{max_hr_threshold} BPM的活动...")
    print("这可能需要较长时间，请耐心等待...")
    
    anomalies = []
    start = 0
    limit = 100  # 每次查询100个活动
    total_processed = 0
    batch_count = 0
    
    while True:
        batch_count += 1
        print(f"\n处理第{batch_count}批活动，从第{start}个开始...")
        
        try:
            # 获取一批活动
            activities = garmin_client.get_activities(start, limit)
            
            if not activities:
                print("已获取所有活动，搜索完成！")
                break
            
            # 处理这批活动
            for activity in activities:
                total_processed += 1
                
                # 获取活动的最大心率
                max_hr = activity.get('maxHR')
                
                # 筛选出最大心率>max_hr_threshold的活动
                if max_hr and max_hr > max_hr_threshold:
                    # 获取活动的ID和日期
                    activity_id = activity.get('activityId')
                    start_time = activity.get('startTimeLocal')
                    activity_name = activity.get('activityName')
                    activity_type = activity.get('activityType', {}).get('typeKey')
                    
                    # 提取日期部分
                    if start_time:
                        date = start_time.split(' ')[0] if ' ' in start_time else start_time.split('T')[0]
                    else:
                        date = "未知"
                    
                    # 添加到异常列表
                    anomaly = {
                        "id": activity_id,
                        "date": date,
                        "name": activity_name,
                        "type": activity_type,
                        "max_hr": max_hr
                    }
                    anomalies.append(anomaly)
                    
                    print(f"找到异常活动: ID={activity_id}, 日期={date}, 最大心率={max_hr} BPM")
            
            # 更新起始位置
            start += limit
            
            # 打印进度
            print(f"已处理{total_processed}个活动，找到{len(anomalies)}个异常活动")
            
            # 避免API调用过于频繁
            time.sleep(1)
            
        except Exception as e:
            print(f"处理批次时出错: {str(e)}")
            # 继续处理下一批
            start += limit
            time.sleep(2)
    
    print(f"\n搜索完成！共处理{total_processed}个活动，找到{len(anomalies)}个异常活动")
    return anomalies


def save_anomalies_to_file(anomalies, filename="hr_anomalies.json"):
    """
    将异常活动保存到文件中
    
    Args:
        anomalies: 异常活动列表
        filename: 保存文件名
    """
    if not anomalies:
        print("没有找到异常活动，无需保存")
        return
    
    try:
        # 整理数据格式
        output_data = {
            "total_anomalies": len(anomalies),
            "threshold": "最大心率>200 BPM",
            "search_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "anomalies": anomalies
        }
        
        # 保存到文件
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n异常活动已保存到文件: {filename}")
        print(f"共保存{len(anomalies)}个异常活动")
        
    except Exception as e:
        print(f"保存文件时出错: {str(e)}")


def main():
    """
    主函数
    """
    print("=" * 80)
    print("Garmin Connect 心率异常活动查找工具")
    print("=" * 80)
    print("此工具将查找所有最大心率>200 BPM的活动")
    print("并将结果保存到文件中")
    print("=" * 80)
    
    # 检查garminconnect库是否可用
    if not garmin_available:
        print("\ngarminconnect库未安装，无法直接连接Garmin Connect。")
        print("请使用 'pip install garminconnect' 安装。")
        return
    
    # 获取Garmin客户端
    garmin_client = get_garmin_client()
    
    if not garmin_client:
        print("\n无法初始化Garmin客户端，程序退出")
        return
    
    # 查找心率异常活动
    anomalies = find_hr_anomalies(garmin_client, 200)
    
    # 保存结果到文件
    save_anomalies_to_file(anomalies, "hr_anomalies.json")
    
    print("\n" + "=" * 80)
    print("程序执行完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
