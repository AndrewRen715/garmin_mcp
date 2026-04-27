#!/usr/bin/env python3
"""
分析心率异常活动数据
"""
import json
import os
from datetime import datetime
from collections import Counter

# 尝试导入matplotlib
matplotlib_available = False
try:
    import matplotlib.pyplot as plt
    import numpy as np
    matplotlib_available = True
except ImportError:
    pass


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


def analyze_frequency(data):
    """
    分析异常心率的频率变化
    
    Args:
        data: 异常数据
    
    Returns:
        dict: 频率分析结果
    """
    if not data or not data.get("anomalies"):
        print("错误: 数据为空")
        return None
    
    anomalies = data.get("anomalies", [])
    
    # 按日期排序
    sorted_anomalies = sorted(anomalies, key=lambda x: x["date"])
    
    # 提取日期和最大心率
    dates = [item["date"] for item in sorted_anomalies]
    max_hrs = [item["max_hr"] for item in sorted_anomalies]
    
    # 转换日期为datetime对象
    date_objects = [datetime.strptime(date, "%Y-%m-%d") for date in dates]
    
    # 计算时间间隔（天）
    time_intervals = []
    for i in range(1, len(date_objects)):
        interval = (date_objects[i] - date_objects[i-1]).days
        time_intervals.append(interval)
    
    # 按年份统计异常次数
    yearly_counts = Counter()
    for date in dates:
        year = date.split("-")[0]
        yearly_counts[year] += 1
    
    # 按月份统计异常次数
    monthly_counts = Counter()
    for date in dates:
        month = date[:7]  # YYYY-MM
        monthly_counts[month] += 1
    
    # 分析频率趋势
    # 计算每年的平均异常次数
    years = sorted(yearly_counts.keys())
    yearly_averages = [yearly_counts[year] for year in years]
    
    # 计算最近一段时间的异常频率
    recent_months = sorted(monthly_counts.keys())[-6:]  # 最近6个月
    recent_counts = [monthly_counts[month] for month in recent_months]
    
    # 分析心率值的变化趋势
    # 计算每半年的平均最大心率
    half_yearly_data = {}
    for i, (date, hr) in enumerate(zip(dates, max_hrs)):
        half_year = date[:4] + "-" + ("H1" if int(date[5:7]) <= 6 else "H2")
        if half_year not in half_yearly_data:
            half_yearly_data[half_year] = []
        half_yearly_data[half_year].append(hr)
    
    half_yearly_aves = {}
    for period, hrs in half_yearly_data.items():
        half_yearly_aves[period] = sum(hrs) / len(hrs)
    
    # 分析活动类型分布
    activity_types = Counter(item["type"] for item in anomalies)
    
    # 分析季节分布
    def get_season(month):
        """根据月份获取季节"""
        if month in [3, 4, 5]:
            return "春季"
        elif month in [6, 7, 8]:
            return "夏季"
        elif month in [9, 10, 11]:
            return "秋季"
        else:
            return "冬季"
    
    seasonal_counts = Counter()
    for date in dates:
        month = int(date.split("-")[1])
        season = get_season(month)
        seasonal_counts[season] += 1
    
    analysis_result = {
        "total_anomalies": len(anomalies),
        "time_range": {
            "start": dates[0],
            "end": dates[-1]
        },
        "yearly_counts": dict(yearly_counts),
        "monthly_counts": dict(monthly_counts),
        "seasonal_counts": dict(seasonal_counts),
        "recent_months": recent_months,
        "recent_counts": recent_counts,
        "time_intervals": time_intervals,
        "average_interval_days": sum(time_intervals) / len(time_intervals) if time_intervals else 0,
        "max_hr_stats": {
            "min": min(max_hrs),
            "max": max(max_hrs),
            "average": sum(max_hrs) / len(max_hrs)
        },
        "half_yearly_averages": half_yearly_aves,
        "activity_types": dict(activity_types)
    }
    
    return analysis_result


def visualize_data(analysis_result):
    """
    可视化分析结果
    
    Args:
        analysis_result: 分析结果
    """
    if not analysis_result:
        print("错误: 分析结果为空")
        return
    
    if not matplotlib_available:
        print("matplotlib库未安装，无法生成图表")
        return
    
    try:
        # 1. 年度异常次数
        years = sorted(analysis_result["yearly_counts"].keys())
        counts = [analysis_result["yearly_counts"][year] for year in years]
        
        plt.figure(figsize=(12, 8))
        
        # 子图1: 年度异常次数
        plt.subplot(2, 2, 1)
        plt.bar(years, counts)
        plt.title('年度异常心率活动次数')
        plt.xlabel('年份')
        plt.ylabel('次数')
        plt.xticks(rotation=45)
        
        # 2. 最近6个月异常次数
        recent_months = analysis_result["recent_months"]
        recent_counts = analysis_result["recent_counts"]
        
        plt.subplot(2, 2, 2)
        plt.bar(recent_months, recent_counts)
        plt.title('最近6个月异常心率活动次数')
        plt.xlabel('月份')
        plt.ylabel('次数')
        plt.xticks(rotation=45)
        
        # 3. 活动类型分布
        activity_types = analysis_result["activity_types"]
        types = list(activity_types.keys())
        type_counts = list(activity_types.values())
        
        plt.subplot(2, 2, 3)
        plt.pie(type_counts, labels=types, autopct='%1.1f%%')
        plt.title('异常心率活动类型分布')
        
        # 4. 半年平均最大心率
        half_years = sorted(analysis_result["half_yearly_averages"].keys())
        avg_hrs = [analysis_result["half_yearly_averages"][period] for period in half_years]
        
        plt.subplot(2, 2, 4)
        plt.plot(half_years, avg_hrs, marker='o')
        plt.title('半年平均最大心率变化')
        plt.xlabel('半年周期')
        plt.ylabel('平均最大心率 (BPM)')
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig('hr_anomaly_analysis.png')
        print("分析图表已保存为 hr_anomaly_analysis.png")
    except Exception as e:
        print(f"生成图表时出错: {str(e)}")
        print("继续输出分析结果...")


def analyze_time_after_exercise():
    """
    分析异常心率出现的时间与运动的关系
    """
    print("\n关于异常心率出现时间与运动的关系分析:")
    print("=====================================")
    print("从现有数据中，我们无法直接确定异常心率出现的具体时间点")
    print("和运动结束后的时间间隔，因为数据中只包含活动的日期，")
    print("没有具体的开始时间、结束时间和异常心率出现的具体时刻。")
    print("\n然而，基于一般运动生理学知识：")
    print("1. 最大心率通常出现在运动过程中强度最大的阶段")
    print("2. 运动后心率应该逐渐恢复到静息水平")
    print("3. 异常高的心率（>200 BPM）更可能出现在运动过程中，")
    print("   而非运动后恢复阶段")
    print("\n建议：")
    print("- 查看具体活动的详细数据，了解心率变化曲线")
    print("- 注意异常心率出现的运动阶段（如冲刺、爬坡等）")
    print("- 关注运动时的环境因素（如高温、高湿度）")
    print("- 考虑设备因素，确保心率监测设备佩戴正确")


def main():
    """
    主函数
    """
    print("=" * 80)
    print("心率异常活动分析工具")
    print("=" * 80)
    
    # 加载数据
    data = load_anomalies("hr_anomalies.json")
    if not data:
        return
    
    # 分析数据
    analysis_result = analyze_frequency(data)
    if not analysis_result:
        return
    
    # 打印分析结果
    print("\n分析结果:")
    print("-" * 60)
    print(f"总异常活动数: {analysis_result['total_anomalies']}")
    print(f"时间范围: {analysis_result['time_range']['start']} 至 {analysis_result['time_range']['end']}")
    print(f"平均间隔天数: {analysis_result['average_interval_days']:.1f}")
    print(f"\n心率统计:")
    print(f"  最低: {analysis_result['max_hr_stats']['min']} BPM")
    print(f"  最高: {analysis_result['max_hr_stats']['max']} BPM")
    print(f"  平均: {analysis_result['max_hr_stats']['average']:.1f} BPM")
    
    print(f"\n年度分布:")
    for year, count in sorted(analysis_result['yearly_counts'].items()):
        print(f"  {year}: {count} 次")
    
    print(f"\n最近6个月分布:")
    for month, count in zip(analysis_result['recent_months'], analysis_result['recent_counts']):
        print(f"  {month}: {count} 次")
    
    print(f"\n活动类型分布:")
    for activity_type, count in analysis_result['activity_types'].items():
        print(f"  {activity_type}: {count} 次")
    
    print(f"\n季节分布:")
    for season, count in analysis_result['seasonal_counts'].items():
        print(f"  {season}: {count} 次")
    
    # 分析频率趋势
    print(f"\n频率趋势分析:")
    print("-" * 60)
    
    # 计算每年的异常次数变化
    years = sorted(analysis_result['yearly_counts'].keys())
    counts = [analysis_result['yearly_counts'][year] for year in years]
    
    if len(counts) > 1:
        # 计算增长率
        growth_rates = []
        for i in range(1, len(counts)):
            if counts[i-1] > 0:
                rate = (counts[i] - counts[i-1]) / counts[i-1] * 100
            else:
                rate = 100 if counts[i] > 0 else 0
            growth_rates.append(rate)
        
        print(f"年度异常次数变化:")
        for i, (year, rate) in enumerate(zip(years[1:], growth_rates)):
            prev_year = years[i]
            trend = "增加" if rate > 0 else "减少"
            print(f"  {prev_year} → {year}: {trend} {abs(rate):.1f}%")
        
        # 分析最近趋势
        recent_counts = analysis_result['recent_counts']
        if len(recent_counts) > 1:
            recent_trend = "增加" if recent_counts[-1] > recent_counts[0] else "减少"
            print(f"\n最近6个月趋势: {recent_trend}")
    
    # 分析异常心率出现时间与运动的关系
    analyze_time_after_exercise()
    
    # 可视化数据
    try:
        visualize_data(analysis_result)
    except Exception as e:
        print(f"\n可视化失败: {str(e)}")
        print("继续输出分析结果...")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
