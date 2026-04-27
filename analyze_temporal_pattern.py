#!/usr/bin/env python3
"""
分析心率异常活动的时间分布模式
"""
import json
import os
from datetime import datetime
from collections import Counter


def load_anomalies(filename="hr_anomalies.json"):
    """
    加载心率异常数据
    
    Args:
        filename: 数据文件名
    
    Returns:
        dict: 异常数据
    """
    if not os.path.exists(filename):
        print(f"错误: 文件 {filename} 不存在")
        return None
    
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"错误: 加载文件失败 - {str(e)}")
        return None


def analyze_temporal_pattern(data):
    """
    分析异常心率的时间分布模式
    
    Args:
        data: 异常数据
    
    Returns:
        dict: 时间模式分析结果
    """
    if not data or not data.get("anomalies"):
        print("错误: 数据为空")
        return None
    
    anomalies = data.get("anomalies", [])
    
    # 按日期排序
    sorted_anomalies = sorted(anomalies, key=lambda x: x["date"])
    
    # 提取日期
    dates = [item["date"] for item in sorted_anomalies]
    
    # 转换日期为datetime对象
    date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
    
    # 计算时间间隔（天）
    time_intervals = []
    for i in range(1, len(date_objects)):
        interval = (date_objects[i] - date_objects[i-1]).days
        time_intervals.append(interval)
    
    # 分析时间间隔分布
    interval_counts = Counter(time_intervals)
    sorted_intervals = sorted(interval_counts.items(), key=lambda x: x[0])
    
    # 分析连续出现的情况
    # 定义连续出现为间隔<=7天
    consecutive_count = 0
    consecutive_sequences = []
    current_sequence = [date_objects[0]]
    
    for i in range(1, len(date_objects)):
        interval = (date_objects[i] - date_objects[i-1]).days
        if interval <= 7:
            current_sequence.append(date_objects[i])
        else:
            if len(current_sequence) >= 2:
                consecutive_count += len(current_sequence) - 1
                consecutive_sequences.append(current_sequence)
            current_sequence = [date_objects[i]]
    
    # 检查最后一个序列
    if len(current_sequence) >= 2:
        consecutive_count += len(current_sequence) - 1
        consecutive_sequences.append(current_sequence)
    
    # 计算集中程度指标
    # 计算时间间隔的标准差
    if time_intervals:
        mean_interval = sum(time_intervals) / len(time_intervals)
        variance = sum((interval - mean_interval) ** 2 for interval in time_intervals) / len(time_intervals)
        std_dev = variance ** 0.5
    else:
        mean_interval = 0
        std_dev = 0
    
    # 计算时间密度（每30天的异常次数）
    if len(date_objects) >= 2:
        total_days = (date_objects[-1] - date_objects[0]).days
        if total_days > 0:
            density = (len(date_objects) / total_days) * 30
        else:
            density = 0
    else:
        density = 0
    
    # 分析月份分布
    monthly_counts = Counter()
    for date in dates:
        month = date[:7]  # YYYY-MM
        monthly_counts[month] += 1
    
    # 分析周内分布
    weekday_counts = Counter()
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for date_obj in date_objects:
        weekday = date_obj.weekday()
        weekday_counts[weekdays[weekday]] += 1
    
    analysis_result = {
        "total_anomalies": len(anomalies),
        "time_range": {
            "start": dates[0],
            "end": dates[-1]
        },
        "time_intervals": time_intervals,
        "mean_interval_days": mean_interval,
        "std_dev_interval_days": std_dev,
        "interval_distribution": dict(interval_counts),
        "sorted_intervals": sorted_intervals,
        "consecutive_count": consecutive_count,
        "consecutive_sequences": [[d.strftime("%Y-%m-%d") for d in seq] for seq in consecutive_sequences],
        "consecutive_rate": consecutive_count / (len(anomalies) - 1) if len(anomalies) > 1 else 0,
        "density_per_30_days": density,
        "monthly_counts": dict(monthly_counts),
        "weekday_counts": dict(weekday_counts)
    }
    
    return analysis_result


def main():
    """
    主函数
    """
    print("=" * 80)
    print("心率异常活动时间分布模式分析")
    print("=" * 80)
    
    # 加载数据
    data = load_anomalies("hr_anomalies.json")
    if not data:
        return
    
    # 分析时间模式
    analysis_result = analyze_temporal_pattern(data)
    if not analysis_result:
        return
    
    # 打印分析结果
    print("\n时间分布模式分析结果:")
    print("-" * 60)
    print(f"总异常活动数: {analysis_result['total_anomalies']}")
    print(f"时间范围: {analysis_result['time_range']['start']} 至 {analysis_result['time_range']['end']}")
    print(f"平均时间间隔: {analysis_result['mean_interval_days']:.1f} 天")
    print(f"时间间隔标准差: {analysis_result['std_dev_interval_days']:.1f} 天")
    print(f"30天内异常密度: {analysis_result['density_per_30_days']:.2f} 次")
    
    print(f"\n时间间隔分布:")
    print("  间隔(天) | 出现次数")
    print("  " + "-" * 20)
    for interval, count in analysis_result['sorted_intervals']:
        print(f"  {interval:8} | {count:4}")
    
    print(f"\n连续出现分析:")
    print(f"  连续出现次数: {analysis_result['consecutive_count']}")
    print(f"  连续出现率: {analysis_result['consecutive_rate']:.2f} (出现一次后连续出现的概率)")
    
    if analysis_result['consecutive_sequences']:
        print(f"  连续出现序列:")
        for i, seq in enumerate(analysis_result['consecutive_sequences'], 1):
            print(f"    序列{i}: {', '.join(seq)}")
    else:
        print(f"  无连续出现序列")
    
    print(f"\n月份分布:")
    sorted_months = sorted(analysis_result['monthly_counts'].items())
    for month, count in sorted_months:
        print(f"  {month}: {count} 次")
    
    print(f"\n周内分布:")
    weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for day in weekdays:
        count = analysis_result['weekday_counts'].get(day, 0)
        print(f"  {day}: {count} 次")
    
    # 分析结论
    print(f"\n分析结论:")
    print("-" * 60)
    
    if analysis_result['consecutive_rate'] > 0.5:
        print("✓ 异常心率存在明显的连续出现模式")
        print(f"  出现一次后，有{analysis_result['consecutive_rate']:.0%}的概率会在7天内再次出现")
    elif analysis_result['consecutive_rate'] > 0.2:
        print("⚠ 异常心率存在一定的连续出现趋势")
        print(f"  出现一次后，有{analysis_result['consecutive_rate']:.0%}的概率会在7天内再次出现")
    else:
        print("✗ 异常心率没有明显的连续出现模式")
        print(f"  出现一次后，只有{analysis_result['consecutive_rate']:.0%}的概率会在7天内再次出现")
    
    if analysis_result['std_dev_interval_days'] < analysis_result['mean_interval_days'] * 0.5:
        print("✓ 异常心率出现时间相对集中")
        print(f"  时间间隔标准差较小({analysis_result['std_dev_interval_days']:.1f}天)，说明分布较为集中")
    else:
        print("⚠ 异常心率出现时间分布较为分散")
        print(f"  时间间隔标准差较大({analysis_result['std_dev_interval_days']:.1f}天)，说明分布较为分散")
    
    if analysis_result['density_per_30_days'] > 1:
        print("✓ 异常心率出现密度较高")
        print(f"  平均每30天出现{analysis_result['density_per_30_days']:.2f}次")
    else:
        print("⚠ 异常心率出现密度较低")
        print(f"  平均每30天出现{analysis_result['density_per_30_days']:.2f}次")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
