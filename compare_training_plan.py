#!/usr/bin/env python3
"""
对比佳明实际训练数据与训练计划，分析差距并提供调整建议
"""
import json
import sys
import argparse
from datetime import datetime, timedelta

def load_plan(filepath):
    """加载训练计划"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：未找到训练计划文件 {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"错误：训练计划文件格式不正确")
        return None

def load_garmin_data(filepath):
    """加载佳明训练数据"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"错误：未找到佳明数据文件 {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"错误：佳明数据文件格式不正确")
        return None

def analyze_week(plan, garmin_data, week_num):
    """分析指定周的训练完成情况"""
    if week_num < 1 or week_num > len(plan['weekly_plans']):
        print(f"错误：周数 {week_num} 超出计划范围")
        return
    
    week_plan = plan['weekly_plans'][week_num - 1]
    print(f"\n{'='*80}")
    print(f"第{week_num}周训练分析 ({week_plan['phase']})")
    print(f"重点: {week_plan['focus']}")
    print('='*80)
    
    plan_distance = 0
    actual_distance = 0
    plan_duration = 0
    actual_duration = 0
    
    print("\n【计划训练】")
    for day in week_plan['weekly_plan']:
        day_name = day['day']
        session = day.get('session1', {})
        content = session.get('content', '')
        duration = session.get('duration', '0分钟')
        
        if '跑步' in session.get('type', '') or '越野' in session.get('type', ''):
            duration_min = int(duration.replace('分钟', '').strip()) if '分钟' in duration else 0
            plan_duration += duration_min
            
            if '公里' in content:
                km = float(content.split('公里')[0].replace('长距离跑', '').replace('次长距离跑', '').replace('轻松跑', '').replace('节奏跑', '').replace('间歇跑', '').replace('越野', '').replace('跑', '').replace('（可替换为越野）', '').replace('（赛前模拟）', '').strip())
                plan_distance += km
        
        print(f"  {day_name}: {session.get('type', '')} - {content} ({duration})")
    
    print("\n【实际训练】")
    if garmin_data:
        week_start = datetime.strptime(week_plan['start_date'], '%Y-%m-%d')
        week_end = datetime.strptime(week_plan['end_date'], '%Y-%m-%d') if 'end_date' in week_plan else week_start + timedelta(days=6)
        
        for activity in garmin_data:
            if 'startTimeLocal' in activity:
                try:
                    activity_date = datetime.strptime(activity['startTimeLocal'][:10], '%Y-%m-%d')
                    if week_start <= activity_date <= week_end:
                        act_type = activity.get('activityType', {}).get('typeKey', '未知')
                        distance = activity.get('distance', 0) / 1000
                        duration = activity.get('duration', 0) / 60
                        
                        actual_distance += distance
                        actual_duration += duration
                        
                        print(f"  {activity_date.strftime('%m-%d')}: {act_type} - {distance:.1f}公里 ({duration:.0f}分钟)")
                except:
                    pass
    else:
        print("  无数据")
    
    print("\n【差距分析】")
    distance_diff = actual_distance - plan_distance
    duration_diff = actual_duration - plan_duration
    
    print(f"  距离目标: {plan_distance:.1f}公里 | 实际完成: {actual_distance:.1f}公里 | {'+' if distance_diff > 0 else ''}{distance_diff:.1f}公里")
    print(f"  时长目标: {plan_duration}分钟 | 实际完成: {actual_duration:.0f}分钟 | {'+' if duration_diff > 0 else ''}{duration_diff:.0f}分钟")
    
    if distance_diff < -5:
        print(f"  ⚠️  距离差距较大，建议下周适当增加训练量")
    elif distance_diff > 10:
        print(f"  ⚠️  本周训练量超额，注意恢复")
    
    return {
        'week': week_num,
        'phase': week_plan['phase'],
        'plan_distance': plan_distance,
        'actual_distance': actual_distance,
        'distance_diff': distance_diff,
        'plan_duration': plan_duration,
        'actual_duration': actual_duration,
        'duration_diff': duration_diff
    }

def generate_report(plan, garmin_data):
    """生成完整的训练对比报告"""
    print("="*80)
    print("训练计划对比分析报告")
    print("="*80)
    print(f"当前日期: {plan.get('current_date', '未知')}")
    print(f"计划目标: {plan.get('goals', [])[0] if plan.get('goals') else '未知'}")
    print()
    
    all_analysis = []
    for week_num in range(1, len(plan['weekly_plans']) + 1):
        analysis = analyze_week(plan, garmin_data, week_num)
        if analysis:
            all_analysis.append(analysis)
    
    print("\n" + "="*80)
    print("综合分析")
    print("="*80)
    
    total_plan_distance = sum(a['plan_distance'] for a in all_analysis)
    total_actual_distance = sum(a['actual_distance'] for a in all_analysis)
    total_distance_diff = sum(a['distance_diff'] for a in all_analysis)
    
    print(f"总计划距离: {total_plan_distance:.1f}公里")
    print(f"总实际距离: {total_actual_distance:.1f}公里")
    print(f"总差距: {'+' if total_distance_diff > 0 else ''}{total_distance_diff:.1f}公里")
    
    avg_diff = total_distance_diff / len(all_analysis) if all_analysis else 0
    if avg_diff < -3:
        print("\n💡 建议：整体训练量低于计划，可适当增加训练强度或频率")
    elif avg_diff > 5:
        print("\n💡 建议：整体训练量高于计划，注意恢复和伤病预防")
    else:
        print("\n💡 建议：训练量与计划基本吻合，继续保持")

def main():
    parser = argparse.ArgumentParser(description='对比佳明实际训练数据与训练计划')
    parser.add_argument('--plan', '-p', default='marathon_trail_plan.json', help='训练计划文件路径')
    parser.add_argument('--data', '-d', default='garmin_activities_raw.json', help='Garmin数据文件路径')
    args = parser.parse_args()
    
    plan = load_plan(args.plan)
    garmin_data = load_garmin_data(args.data)
    
    if not plan:
        return
    
    generate_report(plan, garmin_data)

if __name__ == "__main__":
    main()