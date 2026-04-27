#!/usr/bin/env python3
"""
分析最近的跑步活动并获取每公里分段数据
"""

import json
import sys
import os
from datetime import datetime
from garminconnect import Garmin

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

def get_user_credentials():
    """Get user credentials from environment variables"""
    email = os.environ.get("GARMIN_EMAIL")
    password = os.environ.get("GARMIN_PASSWORD")
    is_cn = os.environ.get("GARMIN_CN", "true").lower() == "true"
    
    if not email or not password:
        print("错误: 请设置GARMIN_EMAIL和GARMIN_PASSWORD环境变量")
        print("或者直接在脚本中输入您的凭据")
        email = input("请输入您的Garmin邮箱: ")
        password = input("请输入您的Garmin密码: ")
        cn_input = input("是否使用中国区账号? (y/n): ")
        is_cn = cn_input.lower() == "y"
    
    return email, password, is_cn

def get_mfa():
    """Get MFA code from user input"""
    return input("请输入MFA验证码: ")

def init_garmin_client():
    """Initialize Garmin client using token or credentials"""
    print("初始化Garmin客户端...")
    
    # Try using init_api from garmin_mcp first
    try:
        garmin_client = init_api(None, None, is_cn=True)
        print("使用 garmin_mcp 初始化成功")
        return garmin_client
    except Exception as e:
        print(f"使用 garmin_mcp 初始化失败: {e}")
        print("尝试使用 Garmin 库初始化...")
        
        # Token store path
        tokenstore = os.getenv("GARMINTOKENS") or "~/.garminconnect"
        tokenstore = os.path.expanduser(tokenstore)
        
        try:
            # First try to login using existing tokens
            print(f"尝试使用token文件登录: {tokenstore}")
            garmin_client = Garmin()
            garmin_client.login(tokenstore)
            print("使用token登录成功")
            return garmin_client
        except Exception as e:
            print(f"使用token登录失败: {str(e)}")
            print("尝试使用凭据登录...")
            
            # If token login fails, try with credentials
            email, password, is_cn = get_user_credentials()
            
            try:
                garmin_client = Garmin(email=email, password=password, is_cn=is_cn, prompt_mfa=get_mfa)
                garmin_client.login()
                # Save tokens for future use
                garmin_client.garth.dump(tokenstore)
                print("使用凭据登录成功，已保存token")
                return garmin_client
            except Exception as e:
                print(f"错误: 初始化Garmin客户端失败: {str(e)}")
                return None

def get_recent_running_activities(garmin_client, limit=50):
    """Get recent running activities"""
    print(f"\n获取最近的{limit}个跑步活动...")
    try:
        activities = garmin_client.get_activities(0, limit)
        
        if not activities:
            print("错误: 没有找到活动")
            return []
        
        # Filter running activities
        running_activities = []
        for activity in activities:
            activity_type = activity.get('activityType', {}).get('typeKey')
            if activity_type and ('running' in activity_type.lower() or 'trail' in activity_type.lower()):
                running_activities.append(activity)
        
        if not running_activities:
            print("错误: 没有找到跑步活动")
            return []
        
        print(f"找到 {len(running_activities)} 个跑步活动")
        
        # 打印所有找到的活动
        print("\n找到的活动:")
        print("-" * 80)
        for i, activity in enumerate(running_activities):
            activity_name = activity.get('activityName')
            start_time = activity.get('startTimeLocal')
            activity_id = activity.get('activityId')
            activity_type = activity.get('activityType', {}).get('typeKey')
            distance = activity.get('distance', 0) / 1000 if activity.get('distance') else 0
            print(f"{i+1}. {activity_name} - {start_time} - {activity_type} - {distance:.2f} km - ID: {activity_id}")
        
        return running_activities
    except Exception as e:
        print(f"错误获取活动: {str(e)}")
        return []

def find_activity_by_date(activities, target_date):
    """Find an activity by date"""
    for activity in activities:
        start_time = activity.get('startTimeLocal')
        if not start_time:
            start_time = activity.get('summaryDTO', {}).get('startTimeLocal')
        if start_time:
            try:
                if 'T' in start_time:
                    activity_date = start_time.split('T')[0]
                else:
                    activity_date = start_time.split(' ')[0]
                if activity_date == target_date:
                    return activity
            except Exception as e:
                pass
    return None

def get_user_hr_data(garmin_client, recent_activities=None):
    """Get user's max heart rate and resting heart rate"""
    
    print("\n获取用户心率数据...")
    
    max_hr = None
    resting_hr = None
    
    try:
        # First, try to get max HR from recent activities (more reliable)
        if recent_activities:
            print("从最近活动中获取最大心率...")
            max_hr_values = []
            for activity in recent_activities:
                if activity.get('maxHR'):
                    max_hr_values.append(activity.get('maxHR'))
            
            if max_hr_values:
                max_hr = max(max_hr_values)
                print(f"从活动获取: 最大心率={max_hr} BPM")
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Try to get heart rate data from health stats
        print("从健康数据中获取心率信息...")
        try:
            hr_data = garmin_client.get_heart_rates(today)
            
            if hr_data:
                health_max_hr = hr_data.get('maxHeartRate')
                health_resting_hr = hr_data.get('restingHeartRate')
                
                print(f"从健康数据获取: 最大心率={health_max_hr} BPM, 静息心率={health_resting_hr} BPM")
                
                # Only use health data if we don't have better data from activities
                if not max_hr and health_max_hr:
                    max_hr = health_max_hr
                if not resting_hr and health_resting_hr:
                    resting_hr = health_resting_hr
        except Exception as e:
            print(f"获取心率数据失败: {str(e)}")
        
        # If still no resting HR, try to estimate it
        if not resting_hr:
            # Estimate resting HR based on common values
            resting_hr = 60
            print(f"估计静息心率: {resting_hr} BPM")
        
        return max_hr, resting_hr
        
    except Exception as e:
        print(f"错误获取心率数据: {str(e)}")
        return None, None

def calculate_custom_zones(max_hr, resting_hr, method="hrr"):
    """Calculate custom HR zones based on the provided chart"""
    
    if not max_hr:
        return None
    
    # Define zones based on the chart
    zones = []
    
    if method == "hrr" and resting_hr:
        # Calculate using Heart Rate Reserve (Karvonen formula)
        hrr = max_hr - resting_hr
        print(f"\n使用储备心率法计算 (HRR = {hrr} BPM):")
        
        zones = [
            {
                "name": "E强度 (轻松跑区间)",
                "min_pct": 0.59,
                "max_pct": 0.74,
                "min": int(resting_hr + (hrr * 0.59)),
                "max": int(resting_hr + (hrr * 0.74)),
                "intensity": "Easy"
            },
            {
                "name": "M强度 (马拉松配速区间)",
                "min_pct": 0.74,
                "max_pct": 0.84,
                "min": int(resting_hr + (hrr * 0.74)),
                "max": int(resting_hr + (hrr * 0.84)),
                "intensity": "Marathon"
            },
            {
                "name": "T强度 (乳酸阈值区间)",
                "min_pct": 0.84,
                "max_pct": 0.88,
                "min": int(resting_hr + (hrr * 0.84)),
                "max": int(resting_hr + (hrr * 0.88)),
                "intensity": "Threshold"
            },
            {
                "name": "A强度 (无氧耐力区间)",
                "min_pct": 0.88,
                "max_pct": 0.95,
                "min": int(resting_hr + (hrr * 0.88)),
                "max": int(resting_hr + (hrr * 0.95)),
                "intensity": "Anaerobic"
            },
            {
                "name": "I强度 (最大摄氧区间)",
                "min_pct": 0.95,
                "max_pct": 1.00,
                "min": int(resting_hr + (hrr * 0.95)),
                "max": max_hr,
                "intensity": "Interval"
            }
        ]
    else:
        # Calculate using Max HR percentage method
        print(f"\n使用最大心率百分比法计算:")
        
        zones = [
            {
                "name": "E强度 (轻松跑区间)",
                "min_pct": 0.59,
                "max_pct": 0.74,
                "min": int(max_hr * 0.59),
                "max": int(max_hr * 0.74),
                "intensity": "Easy"
            },
            {
                "name": "M强度 (马拉松配速区间)",
                "min_pct": 0.74,
                "max_pct": 0.84,
                "min": int(max_hr * 0.74),
                "max": int(max_hr * 0.84),
                "intensity": "Marathon"
            },
            {
                "name": "T强度 (乳酸阈值区间)",
                "min_pct": 0.84,
                "max_pct": 0.88,
                "min": int(max_hr * 0.84),
                "max": int(max_hr * 0.88),
                "intensity": "Threshold"
            },
            {
                "name": "A强度 (无氧耐力区间)",
                "min_pct": 0.88,
                "max_pct": 0.95,
                "min": int(max_hr * 0.88),
                "max": int(max_hr * 0.95),
                "intensity": "Anaerobic"
            },
            {
                "name": "I强度 (最大摄氧区间)",
                "min_pct": 0.95,
                "max_pct": 1.00,
                "min": int(max_hr * 0.95),
                "max": max_hr,
                "intensity": "Interval"
            }
        ]
    
    return zones

def get_km_splits(garmin_client, activity_id):
    """Get per-kilometer splits for an activity"""
    print("\n获取每公里分段数据...")
    
    if hasattr(garmin_client, 'garth'):
        # Try laps endpoint
        endpoint = f"activity-service/activity/{activity_id}/laps"
        try:
            response = garmin_client.garth.get("connectapi", endpoint)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ 获取数据成功")
                
                if 'lapDTOs' in data:
                    laps = data['lapDTOs']
                    print(f"找到 {len(laps)} 个分段")
                    
                    # Filter for per-kilometer splits
                    km_splits = []
                    for i, lap in enumerate(laps):
                        distance = lap.get('distance', 0) / 1000
                        if 0.9 <= distance <= 1.1:
                            pace_min = lap.get('duration', 0) / 60 / distance if distance > 0 else 0
                            pace_minutes = int(pace_min)
                            pace_seconds = int((pace_min - pace_minutes) * 60)
                            pace_str = f"{pace_minutes}:{pace_seconds:02d}"
                            km_splits.append({
                                        'km': i+1,
                                        'distance': distance,
                                        'time': lap.get('duration', 0) / 60,
                                        'pace': (lap.get('duration', 0) / 60) / distance if distance > 0 else 0,
                                        'pace_str': pace_str,
                                        'avg_hr': lap.get('averageHR', 0),
                                        'max_hr': lap.get('maxHR', 0),
                                        'elevation_gain': lap.get('elevationGain', 0)
                                    })
                    
                    if km_splits:
                        print(f"\n识别到 {len(km_splits)} 个每公里分段:")
                        print("公里 | 距离(km) | 时间(min) | 配速(min/km) | 心率(BPM) | 爬升(m)")
                        print("-" * 80)
                        
                        for split in km_splits:
                            print(f"{split['km']:3d} | {split['distance']:9.2f} | {split['time']:9.2f} | {split['pace_str']:11s} | {split['avg_hr']:8.1f} | {split['elevation_gain']:6.0f}")
                        
                        return km_splits
                    else:
                        print("未找到每公里分段")
                        return []
                else:
                    print("无lapDTOs数据")
                    return []
            else:
                print(f"获取失败: 状态码 {response.status_code}")
                return []
        except Exception as e:
            print(f"错误: {e}")
            return []
    else:
        print("garth客户端不可用")
        return []

def analyze_running_activity(activity_id, garmin_client, custom_zones, max_hr, resting_hr, method="hrr"):
    """Analyze a running activity using custom HR zones"""
    
    print(f"\n分析活动 ID: {activity_id}")
    print("=" * 80)
    
    try:
        # Get activity details
        activity = garmin_client.get_activity(activity_id)
        if not activity:
            print("错误: 无法获取活动详情")
            return None
        
        # Get activity name and type
        activity_name = activity.get('activityName')
        activity_type = activity.get('activityTypeDTO', {}).get('typeKey')
        
        print(f"活动名称: {activity_name}")
        print(f"活动类型: {activity_type}")
        print(f"开始时间: {activity.get('summaryDTO', {}).get('startTimeLocal')}")
        
        # Get activity HR data
        hr_zones_data = None
        try:
            hr_zones_data = garmin_client.get_activity_hr_in_timezones(activity_id)
        except Exception as e:
            print(f"获取心率区间数据失败: {str(e)}")
        
        # Analyze HR zones
        print("\n心率区间分析:")
        print("=" * 80)
        
        # Print custom zones
        print("\n自定义心率区间 (基于提供的图表):")
        for zone in custom_zones:
            print(f"{zone['name']}: {zone['min']}-{zone['max']} BPM ({zone['min_pct']*100:.0f}%-{zone['max_pct']*100:.0f}% {"储备心率" if method == "hrr" else "最大心率"})")
        
        # Get time in zones data
        time_in_zones = []
        if hr_zones_data:
            if isinstance(hr_zones_data, list):
                # If it's a list, try to find the timeInZones data
                for item in hr_zones_data:
                    if isinstance(item, dict) and 'timeInZones' in item:
                        time_in_zones = item.get('timeInZones', [])
                        break
            elif isinstance(hr_zones_data, dict):
                # If it's a dict, get timeInZones directly
                time_in_zones = hr_zones_data.get('timeInZones', [])
        
        if time_in_zones:
            print("\n各区间时间分布:")
            print("-" * 80)
            
            total_time = sum([tz.get('seconds', 0) for tz in time_in_zones if isinstance(tz, dict)])
            
            for tz in time_in_zones:
                if isinstance(tz, dict):
                    zone_num = tz.get('zone')
                    seconds = tz.get('seconds', 0)
                    minutes = seconds / 60
                    percentage = (seconds / total_time * 100) if total_time > 0 else 0
                    
                    # Find corresponding custom zone
                    custom_zone = None
                    if 1 <= zone_num <= len(custom_zones):
                        custom_zone = custom_zones[zone_num - 1]
                    
                    if custom_zone:
                        print(f"{custom_zone['name']}: {minutes:.1f} 分钟 ({percentage:.1f}%)")
                    else:
                        print(f"区间 {zone_num}: {minutes:.1f} 分钟 ({percentage:.1f}%)")
            
            print(f"\n总时间: {total_time / 60:.1f} 分钟")
        else:
            print("\n无法获取各区间时间分布数据")
        
        # Get activity summary
        summary = activity.get('summaryDTO', {})
        avg_hr = summary.get('averageHR')
        max_hr_activity = summary.get('maxHR')
        distance = summary.get('distance')
        duration = summary.get('duration')
        calories = summary.get('calories')
        avg_speed = summary.get('averageSpeed')
        
        print("\n活动摘要:")
        print("=" * 80)
        print(f"平均心率: {avg_hr} BPM")
        print(f"最大心率: {max_hr_activity} BPM")
        print(f"距离: {distance / 1000:.2f} km")
        print(f"时长: {duration / 60:.1f} 分钟")
        print(f"卡路里: {calories}")
        if avg_speed:
            pace_min = 60 / (avg_speed * 3.6)
            pace_minutes = int(pace_min)
            pace_seconds = int((pace_min - pace_minutes) * 60)
            pace_str = f"{pace_minutes}:{pace_seconds:02d}"
            print(f"平均配速: {pace_str} 分钟/km")
        
        # Calculate average intensity
        if avg_hr:
            if method == "hrr" and resting_hr and max_hr:
                # Calculate using HRR method
                hrr = max_hr - resting_hr
                if hrr > 0:
                    avg_intensity_pct = ((avg_hr - resting_hr) / hrr) * 100
                    print(f"平均强度: {avg_intensity_pct:.1f}% 储备心率")
                    
                    # Determine intensity zone
                    for zone in custom_zones:
                        if zone['min_pct'] * 100 <= avg_intensity_pct < zone['max_pct'] * 100:
                            print(f"平均强度区间: {zone['name']}")
                            break
                else:
                    print("错误: 储备心率计算失败 (HRR = 0)")
            else:
                # Calculate using max HR method
                avg_intensity_pct = (avg_hr / max_hr) * 100
                print(f"平均强度: {avg_intensity_pct:.1f}% 最大心率")
                
                # Determine intensity zone
                for zone in custom_zones:
                    if zone['min_pct'] * 100 <= avg_intensity_pct < zone['max_pct'] * 100:
                        print(f"平均强度区间: {zone['name']}")
                        break
        
        return activity
    except Exception as e:
        print(f"错误分析活动: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def check_training_plan_compliance(activity):
    """检查当前活动是否符合训练计划"""
    print("\n训练计划合规性检查:")
    print("=" * 80)
    
    # 查找训练计划文件
    plan_files = [
        'marathon_training_plan.json',
        'race_prep_plan_final.json',
        'race_prep_plan_adjusted.json',
        'race_prep_and_recovery_plan.json'
    ]
    
    found_plan = None
    for plan_file in plan_files:
        if os.path.exists(plan_file):
            found_plan = plan_file
            break
    
    if not found_plan:
        print("未找到训练计划文件")
        print("请先使用 running-training-planner 技能生成训练计划")
        return
    
    print(f"找到训练计划: {found_plan}")
    
    # 读取训练计划
    try:
        with open(found_plan, 'r', encoding='utf-8') as f:
            plan_data = json.load(f)
    except Exception as e:
        print(f"读取训练计划失败: {str(e)}")
        return
    
    # 获取活动日期
    start_time = activity.get('startTimeLocal')
    if not start_time:
        # 尝试从summaryDTO中获取
        start_time = activity.get('summaryDTO', {}).get('startTimeLocal')
    if not start_time:
        print("无法获取活动开始时间")
        return
    
    # 解析活动日期
    try:
        # 处理不同格式的时间字符串
        if 'T' in start_time:
            # ISO格式: 2026-04-14T21:24:12.0
            activity_date = datetime.fromisoformat(start_time.replace('.0', '')).date()
        else:
            # 其他格式
            activity_date = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S').date()
    except Exception as e:
        print(f"解析活动时间失败: {str(e)}")
        return
    
    print(f"活动日期: {activity_date}")
    
    # 查找计划中对应日期的训练
    planned_workout = None
    for workout in plan_data.get('workouts', []):
        workout_date_str = workout.get('date')
        if workout_date_str:
            try:
                workout_date = datetime.fromisoformat(workout_date_str).date()
                if workout_date == activity_date:
                    planned_workout = workout
                    break
            except Exception as e:
                pass
    
    if not planned_workout:
        print("当前日期在训练计划中没有安排")
        return
    
    # 显示计划的训练
    print(f"\n计划训练:")
    print(f"类型: {planned_workout.get('type')}")
    print(f"距离: {planned_workout.get('distance')} km")
    print(f"时长: {planned_workout.get('duration')}")
    print(f"配速: {planned_workout.get('pace')}")
    print(f"描述: {planned_workout.get('description')}")
    
    # 获取活动实际数据
    summary = activity.get('summaryDTO', {})
    actual_distance = summary.get('distance', 0) / 1000  # 转换为公里
    actual_duration = summary.get('duration', 0) / 60  # 转换为分钟
    
    print(f"\n实际活动:")
    print(f"距离: {actual_distance:.2f} km")
    print(f"时长: {actual_duration:.1f} 分钟")
    
    # 检查合规性
    planned_distance = planned_workout.get('distance', 0)
    if planned_distance > 0:
        distance_diff = abs(actual_distance - planned_distance)
        distance_pct_diff = (distance_diff / planned_distance) * 100 if planned_distance > 0 else 0
        
        print(f"\n合规性检查:")
        if distance_pct_diff <= 10:
            print("✓ 距离符合计划要求")
        else:
            print(f"✗ 距离与计划有较大差异 (差异: {distance_pct_diff:.1f}%)")
    
    # 检查训练类型
    planned_type = planned_workout.get('type')
    actual_type = activity.get('activityType', {}).get('typeKey', '').lower()
    
    print(f"\n训练类型检查:")
    if 'run' in actual_type and 'run' in planned_type:
        print("✓ 训练类型符合计划要求")
    else:
        print(f"✗ 训练类型与计划不符 (计划: {planned_type}, 实际: {actual_type})")
    
    print("\n训练计划合规性检查完成")

def calculate_itra_performance_score(distance_km, elevation_gain, duration_min, age=30, gender='male'):
    """计算ITRA表现分"""
    # 根据ITRA官方方法，使用努力公里(effort kilometers)概念
    # 努力公里 = 距离(km) + 爬升(m)/100
    effort_km = distance_km + (elevation_gain / 100)
    
    # 计算速度 (km/h)
    speed = effort_km / (duration_min / 60)
    
    # ITRA表现分基于速度和努力公里
    # 参考ITRA的评分标准，分数范围从0到1000
    # 根据官方数据调整计算方法
    import math
    
    if speed <= 0:
        return 0
    
    # 基础分数计算
    # 使用对数函数来模拟ITRA的评分曲线
    # 参考官方数据：
    # - 精英男性：825+，精英女性：700+
    # - 中高级水平：500+
    # - 美国35-39岁男性平均：487
    # 调整参数使结果更符合实际分布
    base_score = 150 * math.log(speed) + 50
    
    # 距离调整
    # 更长距离的比赛需要更多耐力，给予适当加分
    distance_bonus = min(distance_km * 1.5, 80)  # 最多80分的距离奖励
    
    # 年龄和性别调整
    age_factor = 1.0
    if age > 30:
        age_factor = 1.0 + (age - 30) * 0.002  # 每增加一岁，分数增加0.2%
    
    gender_factor = 1.0
    if gender == 'female':
        gender_factor = 1.03  # 女性调整系数
    
    # 最终分数
    itra_score = (base_score + distance_bonus) * age_factor * gender_factor
    
    # 确保分数在合理范围内 (0-1000)
    itra_score = max(0, min(1000, itra_score))
    
    return round(itra_score, 2)

def main():
    """Main function"""
    
    print("分析最近的跑步活动并获取每公里分段数据")
    print("基于用户提供的图表设置")
    print("(支持中国区账号)")
    print("=" * 80)
    
    # Initialize Garmin client
    garmin_client = init_garmin_client()
    if not garmin_client:
        return
    
    # Get recent running activities
    running_activities = get_recent_running_activities(garmin_client)
    if not running_activities:
        return
    
    # Get user's HR data, using recent activities for better accuracy
    max_hr, resting_hr = get_user_hr_data(garmin_client, running_activities)
    
    if not max_hr:
        print("\n错误: 无法获取最大心率")
        print("请输入您的最大心率:")
        max_hr = int(input("最大心率: "))
    
    if not resting_hr:
        print("\n错误: 无法获取静息心率")
        print("请输入您的静息心率:")
        resting_hr = int(input("静息心率: "))
    
    print(f"\n使用的心率数据:")
    print(f"最大心率: {max_hr} BPM")
    print(f"静息心率: {resting_hr} BPM")
    
    # Calculate custom zones
    custom_zones = calculate_custom_zones(max_hr, resting_hr, method="hrr")
    
    if not custom_zones:
        print("\n错误: 无法计算自定义心率区间")
        return
    
    # 查找4.19日的黄龙100 27K活动
    huanglong_activity = find_activity_by_date(running_activities, "2026-04-19")
    
    if huanglong_activity:
        print("\n" + "=" * 80)
        print("分析4.19日黄龙100 27K活动")
        print("=" * 80)
        
        activity_id = huanglong_activity.get('activityId')
        activity_name = huanglong_activity.get('activityName')
        start_time = huanglong_activity.get('startTimeLocal')
        
        print(f"活动名称: {activity_name}")
        print(f"开始时间: {start_time}")
        print(f"活动ID: {activity_id}")
        
        # Get per-kilometer splits
        km_splits = get_km_splits(garmin_client, activity_id)
        
        # Save splits to file
        if km_splits:
            with open('huanglong_km_splits.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'activity': huanglong_activity,
                    'km_splits': km_splits
                }, f, indent=2, ensure_ascii=False)
            print("\n每公里分段数据已保存到 huanglong_km_splits.json")
        
        # Analyze the activity
        analyzed_activity = analyze_running_activity(activity_id, garmin_client, custom_zones, max_hr, resting_hr, method="hrr")
        
        # 计算ITRA表现分
        if analyzed_activity:
            summary = analyzed_activity.get('summaryDTO', {})
            distance = summary.get('distance', 0) / 1000  # 转换为公里
            duration = summary.get('duration', 0) / 60  # 转换为分钟
            # 尝试获取爬升数据
            elevation_gain = 0
            if 'elevationGain' in summary:
                elevation_gain = summary.get('elevationGain')
            elif 'elevationGain' in analyzed_activity:
                elevation_gain = analyzed_activity.get('elevationGain')
            elif 'elevationGain' in analyzed_activity.get('activitySummaryDTO', {}):
                elevation_gain = analyzed_activity.get('activitySummaryDTO', {}).get('elevationGain')
            
            # 显示爬升数据
            print(f"\n爬升数据: {elevation_gain} 米")
            
            itra_score = calculate_itra_performance_score(distance, elevation_gain, duration)
            print(f"\nITRA表现分估算: {itra_score}")
            
            # Check training plan compliance
            check_training_plan_compliance(analyzed_activity)
    else:
        print("\n未找到4.19日的活动")
    
    # 查找抱佛脚跑山赛活动
    baofojiao_activity = None
    for activity in running_activities:
        activity_name = activity.get('activityName', '').lower()
        if '抱佛脚' in activity_name or 'baofojiao' in activity_name or 'trail' in activity_name:
            baofojiao_activity = activity
            break
    
    if baofojiao_activity:
        print("\n" + "=" * 80)
        print("分析抱佛脚跑山赛活动")
        print("=" * 80)
        
        activity_id = baofojiao_activity.get('activityId')
        activity_name = baofojiao_activity.get('activityName')
        start_time = baofojiao_activity.get('startTimeLocal')
        
        print(f"活动名称: {activity_name}")
        print(f"开始时间: {start_time}")
        print(f"活动ID: {activity_id}")
        
        # Get per-kilometer splits
        km_splits = get_km_splits(garmin_client, activity_id)
        
        # Save splits to file
        if km_splits:
            with open('baofojiao_km_splits.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'activity': baofojiao_activity,
                    'km_splits': km_splits
                }, f, indent=2, ensure_ascii=False)
            print("\n每公里分段数据已保存到 baofojiao_km_splits.json")
        
        # Analyze the activity
        analyzed_activity = analyze_running_activity(activity_id, garmin_client, custom_zones, max_hr, resting_hr, method="hrr")
        
        # 计算ITRA表现分
        if analyzed_activity:
            summary = analyzed_activity.get('summaryDTO', {})
            distance = summary.get('distance', 0) / 1000  # 转换为公里
            duration = summary.get('duration', 0) / 60  # 转换为分钟
            # 尝试获取爬升数据
            elevation_gain = 0
            if 'elevationGain' in summary:
                elevation_gain = summary.get('elevationGain')
            elif 'elevationGain' in analyzed_activity:
                elevation_gain = analyzed_activity.get('elevationGain')
            elif 'elevationGain' in analyzed_activity.get('activitySummaryDTO', {}):
                elevation_gain = analyzed_activity.get('activitySummaryDTO', {}).get('elevationGain')
            
            # 显示爬升数据
            print(f"\n爬升数据: {elevation_gain} 米")
            
            itra_score = calculate_itra_performance_score(distance, elevation_gain, duration)
            print(f"\nITRA表现分估算: {itra_score}")
    else:
        print("\n未找到抱佛脚跑山赛活动")
    
    # 查找3.15日的越野赛活动
    march15_activity = find_activity_by_date(running_activities, "2026-03-15")
    
    if march15_activity:
        print("\n" + "=" * 80)
        print("分析3.15日越野赛活动")
        print("=" * 80)
        
        activity_id = march15_activity.get('activityId')
        activity_name = march15_activity.get('activityName')
        start_time = march15_activity.get('startTimeLocal')
        
        print(f"活动名称: {activity_name}")
        print(f"开始时间: {start_time}")
        print(f"活动ID: {activity_id}")
        
        # Get per-kilometer splits
        km_splits = get_km_splits(garmin_client, activity_id)
        
        # Save splits to file
        if km_splits:
            with open('march15_km_splits.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'activity': march15_activity,
                    'km_splits': km_splits
                }, f, indent=2, ensure_ascii=False)
            print("\n每公里分段数据已保存到 march15_km_splits.json")
        
        # Analyze the activity
        analyzed_activity = analyze_running_activity(activity_id, garmin_client, custom_zones, max_hr, resting_hr, method="hrr")
        
        # 计算ITRA表现分
        if analyzed_activity:
            summary = analyzed_activity.get('summaryDTO', {})
            distance = summary.get('distance', 0) / 1000  # 转换为公里
            duration = summary.get('duration', 0) / 60  # 转换为分钟
            # 尝试获取爬升数据
            elevation_gain = 0
            if 'elevationGain' in summary:
                elevation_gain = summary.get('elevationGain')
            elif 'elevationGain' in analyzed_activity:
                elevation_gain = analyzed_activity.get('elevationGain')
            elif 'elevationGain' in analyzed_activity.get('activitySummaryDTO', {}):
                elevation_gain = analyzed_activity.get('activitySummaryDTO', {}).get('elevationGain')
            
            # 显示爬升数据
            print(f"\n爬升数据: {elevation_gain} 米")
            
            itra_score = calculate_itra_performance_score(distance, elevation_gain, duration)
            print(f"\nITRA表现分估算: {itra_score}")
    else:
        print("\n未找到3.15日的活动")

if __name__ == "__main__":
    main()
