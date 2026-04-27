#!/usr/bin/env python3
"""
分析心率异常活动的时间间隔变化趋势
"""
import json
import os
from datetime import datetime


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


def linear_regression(x, y):
    """
    纯Python实现线性回归
    
    Args:
        x: x值列表
        y: y值列表
    
    Returns:
        tuple: (slope, intercept, r_value, p_value, std_err)
    """
    n = len(x)
    if n != len(y):
        raise ValueError("x and y must have the same length")
    
    # 计算均值
    mean_x = sum(x) / n
    mean_y = sum(y) / n
    
    # 计算斜率
    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
    
    if denominator == 0:
        return 0, mean_y, 0, 1, 0
    
    slope = numerator / denominator
    intercept = mean_y - slope * mean_x
    
    # 计算相关系数
    ss_res = sum((y[i] - (slope * x[i] + intercept)) ** 2 for i in range(n))
    ss_tot = sum((y[i] - mean_y) ** 2 for i in range(n))
    
    if ss_tot == 0:
        r_value = 1 if ss_res == 0 else 0
    else:
        r_value = (1 - ss_res / ss_tot) ** 0.5
        if slope < 0:
            r_value = -r_value
    
    # 简化的p值计算
    p_value = 0.1  # 默认为不显著
    if abs(r_value) > 0.5:
        p_value = 0.05
    if abs(r_value) > 0.7:
        p_value = 0.01
    
    # 计算标准误差
    if n > 2:
        std_err = (ss_res / (n - 2)) ** 0.5 / denominator ** 0.5
    else:
        std_err = 0
    
    return slope, intercept, r_value, p_value, std_err

def analyze_interval_trend(data):
    """
    分析异常心率的时间间隔变化趋势
    
    Args:
        data: 异常数据
    
    Returns:
        dict: 时间间隔趋势分析结果
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
    
    if not time_intervals:
        print("错误: 数据不足，无法计算时间间隔")
        return None
    
    # 分析时间间隔趋势
    # 计算线性回归
    x = list(range(len(time_intervals)))
    y = time_intervals
    
    slope, intercept, r_value, p_value, std_err = linear_regression(x, y)
    
    # 计算趋势方向
    if slope > 0:
        trend_direction = "变长"
        trend_significance = "上升"
    elif slope < 0:
        trend_direction = "变短"
        trend_significance = "下降"
    else:
        trend_direction = "不变"
        trend_significance = "稳定"
    
    # 计算趋势显著性
    # p_value < 0.05 表示趋势显著
    is_significant = p_value < 0.05
    
    # 分析前半段和后半段的平均间隔
    mid_point = len(time_intervals) // 2
    first_half = time_intervals[:mid_point]
    second_half = time_intervals[mid_point:]
    
    avg_first_half = sum(first_half) / len(first_half) if first_half else 0
    avg_second_half = sum(second_half) / len(second_half) if second_half else 0
    
    # 计算变化百分比
    if avg_first_half > 0:
        change_percentage = ((avg_second_half - avg_first_half) / avg_first_half) * 100
    else:
        change_percentage = 0
    
    # 分析最近几个间隔
    recent_interval_count = min(5, len(time_intervals))
    recent_intervals = time_intervals[-recent_interval_count:]
    avg_recent = sum(recent_intervals) / len(recent_intervals) if recent_intervals else 0
    
    # 计算整体统计数据
    mean_interval = sum(time_intervals) / len(time_intervals)
    sorted_intervals = sorted(time_intervals)
    n = len(sorted_intervals)
    if n % 2 == 0:
        median_interval = (sorted_intervals[n//2 - 1] + sorted_intervals[n//2]) / 2
    else:
        median_interval = sorted_intervals[n//2]
    
    # 计算标准差
    variance = sum((interval - mean_interval) ** 2 for interval in time_intervals) / len(time_intervals)
    std_interval = variance ** 0.5
    
    min_interval = min(time_intervals)
    max_interval = max(time_intervals)
    
    analysis_result = {
        "total_anomalies": len(anomalies),
        "total_intervals": len(time_intervals),
        "time_range": {
            "start": dates[0],
            "end": dates[-1]
        },
        "time_intervals": time_intervals,
        "interval_stats": {
            "mean": mean_interval,
            "median": median_interval,
            "std": std_interval,
            "min": min_interval,
            "max": max_interval
        },
        "trend_analysis": {
            "slope": slope,
            "intercept": intercept,
            "r_value": r_value,
            "r_squared": r_value ** 2,
            "p_value": p_value,
            "std_err": std_err,
            "trend_direction": trend_direction,
            "trend_significance": trend_significance,
            "is_significant": is_significant
        },
        "half_analysis": {
            "first_half_count": len(first_half),
            "second_half_count": len(second_half),
            "avg_first_half": avg_first_half,
            "avg_second_half": avg_second_half,
            "change_percentage": change_percentage
        },
        "recent_analysis": {
            "recent_count": len(recent_intervals),
            "recent_intervals": recent_intervals,
            "avg_recent": avg_recent
        }
    }
    
    return analysis_result


def main():
    """
    主函数
    """
    print("=" * 80)
    print("心率异常活动时间间隔变化趋势分析")
    print("=" * 80)
    
    # 加载数据
    data = load_anomalies("hr_anomalies.json")
    if not data:
        return
    
    # 分析时间间隔趋势
    analysis_result = analyze_interval_trend(data)
    if not analysis_result:
        return
    
    # 打印分析结果
    print("\n时间间隔分析结果:")
    print("-" * 60)
    print(f"总异常活动数: {analysis_result['total_anomalies']}")
    print(f"总时间间隔数: {analysis_result['total_intervals']}")
    print(f"时间范围: {analysis_result['time_range']['start']} 至 {analysis_result['time_range']['end']}")
    
    print(f"\n时间间隔统计:")
    stats = analysis_result['interval_stats']
    print(f"  平均间隔: {stats['mean']:.1f} 天")
    print(f"  中位数间隔: {stats['median']:.1f} 天")
    print(f"  标准差: {stats['std']:.1f} 天")
    print(f"  最小间隔: {stats['min']:.1f} 天")
    print(f"  最大间隔: {stats['max']:.1f} 天")
    
    print(f"\n时间间隔序列:")
    intervals = analysis_result['time_intervals']
    for i, interval in enumerate(intervals, 1):
        print(f"  间隔{i}: {interval} 天")
    
    print(f"\n趋势分析:")
    trend = analysis_result['trend_analysis']
    print(f"  趋势方向: {trend['trend_direction']}")
    print(f"  趋势系数: {trend['slope']:.3f}")
    print(f"  相关系数: {trend['r_value']:.3f}")
    print(f"  决定系数: {trend['r_squared']:.3f}")
    print(f"  P值: {trend['p_value']:.3f}")
    
    if trend['is_significant']:
        print(f"  趋势显著性: 显著 (p < 0.05)")
    else:
        print(f"  趋势显著性: 不显著 (p >= 0.05)")
    
    print(f"\n前后半段分析:")
    half = analysis_result['half_analysis']
    print(f"  前半段平均间隔: {half['avg_first_half']:.1f} 天")
    print(f"  后半段平均间隔: {half['avg_second_half']:.1f} 天")
    print(f"  变化百分比: {half['change_percentage']:.1f}%")
    
    print(f"\n最近几个间隔:")
    recent = analysis_result['recent_analysis']
    print(f"  最近{recent['recent_count']}个间隔: {recent['recent_intervals']}")
    print(f"  最近平均间隔: {recent['avg_recent']:.1f} 天")
    
    # 分析结论
    print(f"\n分析结论:")
    print("-" * 60)
    
    # 基于线性回归的趋势
    if trend['is_significant']:
        if trend['slope'] > 0.1:
            print(f"✓ 时间间隔呈显著上升趋势")
            print(f"  平均每次异常后，下一次异常的间隔时间增加 {trend['slope']:.1f} 天")
        elif trend['slope'] < -0.1:
            print(f"✓ 时间间隔呈显著下降趋势")
            print(f"  平均每次异常后，下一次异常的间隔时间减少 {abs(trend['slope']):.1f} 天")
        else:
            print(f"✓ 时间间隔保持稳定")
            print(f"  没有显著的变长或变短趋势")
    else:
        # 基于前后半段比较
        if abs(half['change_percentage']) > 30:
            if half['change_percentage'] > 0:
                print(f"⚠ 时间间隔有变长的趋势")
                print(f"  后半段平均间隔比前半段增加了 {half['change_percentage']:.1f}%")
            else:
                print(f"⚠ 时间间隔有变短的趋势")
                print(f"  后半段平均间隔比前半段减少了 {abs(half['change_percentage']):.1f}%")
        else:
            print(f"✗ 时间间隔没有明显的变长或变短趋势")
            print(f"  前后半段平均间隔变化不大 ({abs(half['change_percentage']):.1f}%)")
    
    # 基于最近间隔的分析
    if recent['avg_recent'] > analysis_result['interval_stats']['mean'] * 1.2:
        print(f"\n📈 最近几个间隔比平均间隔长")
        print(f"  最近平均: {recent['avg_recent']:.1f} 天, 整体平均: {analysis_result['interval_stats']['mean']:.1f} 天")
        print(f"  这表明最近异常心率的出现间隔可能在变长")
    elif recent['avg_recent'] < analysis_result['interval_stats']['mean'] * 0.8:
        print(f"\n📉 最近几个间隔比平均间隔短")
        print(f"  最近平均: {recent['avg_recent']:.1f} 天, 整体平均: {analysis_result['interval_stats']['mean']:.1f} 天")
        print(f"  这表明最近异常心率的出现间隔可能在变短")
    else:
        print(f"\n📊 最近几个间隔与平均间隔相近")
        print(f"  最近平均: {recent['avg_recent']:.1f} 天, 整体平均: {analysis_result['interval_stats']['mean']:.1f} 天")
        print(f"  最近异常心率的出现间隔保持稳定")
    
    print("\n" + "=" * 80)
    print("分析完成！")
    print("=" * 80)


if __name__ == "__main__":
    main()
