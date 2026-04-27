#!/usr/bin/env python3
"""
Garmin Connect 中国区 - 近30天训练量分析
自动使用已存储的token，不需要交互式输入
"""

import sys
import os
import json
from datetime import datetime, timedelta, timezone

# 尝试导入 garmin_mcp
try:
    from garmin_mcp import init_api
    USE_GARMIN_MCP = True
except ImportError:
    USE_GARMIN_MCP = False

def analyze_activities(client):
    """分析近30天活动"""
    now = datetime.now()
    start_date = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = now.strftime("%Y-%m-%d")
    
    print(f"\n📊 分析区间: {start_date} → {end_date}")
    print("=" * 60)
    
    # 获取活动列表
    try:
        activities = client.get_activities_by_date(start_date, end_date)
    except Exception as e:
        print(f"get_activities_by_date 失败: {e}")
        try:
            activities = client.get_activities(0, 100)
        except Exception as e2:
            print(f"get_activities 也失败: {e2}")
            return
    
    if not activities:
        print("没有找到活动数据")
        return
    
    print(f"共找到 {len(activities)} 条活动记录\n")
    
    # 统计数据
    stats = {
        'running': {'count': 0, 'distance': 0, 'duration': 0, 'elevation': 0},
        'trail': {'count': 0, 'distance': 0, 'duration': 0, 'elevation': 0},
        'cycling': {'count': 0, 'distance': 0, 'duration': 0},
        'strength': {'count': 0, 'duration': 0},
        'climbing': {'count': 0, 'duration': 0},
        'other': {'count': 0, 'duration': 0},
    }
    
    weekly_distance = {}  # week_num -> km
    
    print(f"{'日期':<12} {'类型':<20} {'距离(km)':<10} {'时长(min)':<12} {'爬升(m)':<10} {'配速':<10}")
    print("-" * 80)
    
    for act in activities:
        try:
            # 基础字段
            act_type = str(act.get('activityType', {}).get('typeKey', 'other')).lower()
            start_time = act.get('startTimeLocal', act.get('startTimeGMT', ''))[:10]
            distance_m = float(act.get('distance', 0) or 0)
            duration_s = float(act.get('duration', act.get('elapsedDuration', 0)) or 0)
            elevation = float(act.get('elevationGain', 0) or 0)
            avg_pace = act.get('averageSpeed', 0)
            name = act.get('activityName', '')
            
            distance_km = distance_m / 1000
            duration_min = duration_s / 60
            
            # 配速
            if avg_pace and avg_pace > 0 and 'run' in act_type:
                pace_sec = 1000 / avg_pace  # sec/km
                pace_str = f"{int(pace_sec//60)}'{int(pace_sec%60)}"
            else:
                pace_str = "-"
            
            # 分类
            if 'trail' in act_type or 'trail' in name.lower():
                cat = 'trail'
            elif 'run' in act_type:
                cat = 'running'
            elif 'cycl' in act_type or 'bike' in act_type:
                cat = 'cycling'
            elif 'strength' in act_type or 'gym' in act_type:
                cat = 'strength'
            elif 'climb' in act_type or 'bouldering' in act_type.lower():
                cat = 'climbing'
            else:
                cat = 'other'
            
            stats[cat]['count'] += 1
            if 'distance' in stats[cat]:
                stats[cat]['distance'] += distance_km
            if 'duration' in stats[cat]:
                stats[cat]['duration'] += duration_min
            if 'elevation' in stats[cat]:
                stats[cat]['elevation'] += elevation
            
            # 按周统计跑量
            if cat in ('running', 'trail') and distance_km > 0:
                try:
                    dt = datetime.strptime(start_time, "%Y-%m-%d")
                    week = dt.isocalendar()[1]
                    weekly_distance[week] = weekly_distance.get(week, 0) + distance_km
                except:
                    pass
            
            type_display = act_type[:18]
            print(f"{start_time:<12} {type_display:<20} {distance_km:<10.1f} {duration_min:<12.0f} {elevation:<10.0f} {pace_str:<10}")
        except Exception as e:
            print(f"解析活动出错: {e}, data: {str(act)[:100]}")
    
    # 汇总
    print("\n" + "=" * 60)
    print("📈 近30天训练汇总")
    print("=" * 60)
    
    total_run = stats['running']['distance'] + stats['trail']['distance']
    total_sessions = sum(v['count'] for v in stats.values())
    
    print(f"总训练次数: {total_sessions} 次")
    print(f"跑步: {stats['running']['count']}次, {stats['running']['distance']:.1f}km, {stats['running']['duration']:.0f}min")
    print(f"越野: {stats['trail']['count']}次, {stats['trail']['distance']:.1f}km, 爬升{stats['trail']['elevation']:.0f}m")
    print(f"骑行: {stats['cycling']['count']}次, {stats['cycling']['distance']:.1f}km")
    print(f"力量: {stats['strength']['count']}次, {stats['strength']['duration']:.0f}min")
    print(f"攀岩: {stats['climbing']['count']}次, {stats['climbing']['duration']:.0f}min")
    print(f"其他: {stats['other']['count']}次")
    print(f"\n总跑量: {total_run:.1f} km")
    print(f"总爬升: {stats['trail']['elevation'] + stats['running']['elevation']:.0f} m")
    
    if weekly_distance:
        print(f"\n周跑量分布:")
        for week in sorted(weekly_distance.keys()):
            bar = "█" * int(weekly_distance[week] / 2)
            print(f"  第{week}周: {weekly_distance[week]:.1f}km {bar}")
    
    # 保存原始数据
    with open('garmin_activities_raw.json', 'w', encoding='utf-8') as f:
        json.dump(activities, f, ensure_ascii=False, indent=2, default=str)
    print(f"\n✓ 原始数据已保存到 garmin_activities_raw.json")


def main():
    client = None
    
    if USE_GARMIN_MCP:
        print("使用 garmin_mcp 初始化...")
        os.environ['GARMIN_CN'] = 'true'
        # 尝试从已有 token 加载，不需要重新登录
        cn_tokenstore = os.path.expanduser(os.getenv("GARMINTOKENS_CN", "~/.garminconnect_cn"))
        try:
            from garmin_mcp import init_api
            # 传空密码，让它用存储的 token
            if os.path.exists(cn_tokenstore):
                print(f"从 {cn_tokenstore} 加载已存储的 token...")
            # 直接使用已存储的token，不需要交互式输入
            client = init_api("", "", is_cn=True)
        except Exception as e:
            print(f"garmin_mcp 初始化失败: {e}")
    
    if not client:
        print("❌ 无法初始化 Garmin 客户端，请确认 garmin_mcp 已安装")
        return
    
    analyze_activities(client)


if __name__ == "__main__":
    main()
