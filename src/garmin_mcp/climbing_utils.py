#!/usr/bin/env python3
"""
攀岩相关的工具函数
"""

from datetime import datetime

def format_duration(seconds):
    """格式化时长"""
    if seconds is None:
        return "N/A"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    if hours > 0:
        return f"{hours}h {minutes}min"
    return f"{minutes}min"

def get_climbing_activities(garmin_client, days=30):
    """
    获取最近的攀岩活动
    
    Args:
        garmin_client: Garmin API 客户端实例
        days: 获取最近多少天的活动，默认30天
        
    Returns:
        list: 攀岩相关活动列表，每个活动是一个字典
    """
    activities = []
    start = 0
    limit = 50
    
    while True:
        page = garmin_client.get_activities(start, limit)
        if not page:
            break
        activities.extend(page)
        start += limit
        if len(page) < limit:
            break
    
    cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)
    climbing_activities = []
    
    for activity in activities:
        activity_time = activity.get('startTimeGMT', '')
        if activity_time:
            try:
                ts = datetime.fromisoformat(activity_time.replace('Z', '+00:00')).timestamp()
                if ts < cutoff_date:
                    continue
            except:
                pass
        
        activity_type = activity.get('activityType', {}).get('typeKey', '')
        activity_name = activity.get('activityName', '').lower()
        
        if activity_type in ['indoor_climbing', 'rock_climbing', 'bouldering'] or \
           '攀岩' in activity_name or '抱石' in activity_name:
            start_time = activity.get('startTimeLocal', '')
            activity_date = start_time.split(' ')[0] if start_time else 'Unknown'
            
            climbing_activities.append({
                "id": activity.get('activityId'),
                "date": activity_date,
                "time": start_time,
                "name": activity.get('activityName', 'Unnamed'),
                "type": activity_type,
                "duration": activity.get('duration'),
                "duration_formatted": format_duration(activity.get('duration')),
                "avg_hr": activity.get('averageHR'),
                "max_hr": activity.get('maxHR'),
                "calories": activity.get('calories'),
                "elevation_gain": activity.get('elevationGain'),
            })
    
    return climbing_activities