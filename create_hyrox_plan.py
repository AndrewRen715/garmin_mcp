#!/usr/bin/env python3
"""
为2026年7月6日Hyrox杭州比赛制定专门的训练计划
Hyrox: 8个功能性训练站点 + 8次1公里跑步
"""
import json
from datetime import datetime, timedelta

def get_weekday(date_str):
    """获取日期对应的星期几"""
    date = datetime.strptime(date_str, '%Y-%m-%d')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[date.weekday()]

def create_hyrox_plan():
    """创建Hyrox比赛训练计划"""
    today = datetime.now()
    current_date = today.strftime('%Y-%m-%d')
    
    # 比赛信息
    race_info = {
        "date": "2026-07-06",
        "location": "杭州",
        "type": "Hyrox",
        "description": "8个功能性训练站点 + 8次1公里跑步",
        "weekday": get_weekday("2026-07-06"),
        "days_until_race": (datetime.strptime("2026-07-06", '%Y-%m-%d') - today).days
    }
    
    # Hyrox比赛项目
    hyrox_stations = [
        {"order": 1, "name": "Wall Balls", "description": "墙壁球投掷"},
        {"order": 2, "name": "SkiErg", "description": "滑雪机"},
        {"order": 3, "name": "Sled Push", "description": "雪橇推"},
        {"order": 4, "name": "Sled Pull", "description": "雪橇拉"},
        {"order": 5, "name": "Burpee Box Jump Overs", "description": "波比跳箱"},
        {"order": 6, "name": "Rowing", "description": "划船机"},
        {"order": 7, "name": "Kettlebell Swings", "description": "壶铃摇摆"},
        {"order": 8, "name": "Dumbbell Lunges", "description": "哑铃弓步"},
        {"order": 9, "name": "Push-Ups", "description": "俯卧撑"},
        {"order": 10, "name": "Rope Climb", "description": "爬绳"}
    ]
    
    # 目标设定
    goals = {
        "cardio_goal": "1公里跑步配速达到5:00-5:30 min/km",
        "strength_goal": "完成所有功能性站点的标准次数",
        "endurance_goal": "完成全程比赛（约1小时15分钟）",
        "weekly_training_hours": 8-10
    }
    
    plan = {
        "current_date": current_date,
        "current_weekday": get_weekday(current_date),
        "race_info": race_info,
        "hyrox_stations": hyrox_stations,
        "goals": goals,
        "weekly_plans": []
    }
    
    # ==================== 第1周：4月29日-5月5日（基础建立）====================
    week1 = {
        "week": "第1周",
        "phase": "基础建立期",
        "start_date": "2026-04-29",
        "end_date": "2026-05-05",
        "focus": "建立跑步基础和功能性训练习惯",
        "weekly_plan": [
            {"date": "2026-04-29", "day": get_weekday("2026-04-29"),
             "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "30分钟"},
             "session2": {"type": "力量", "content": "全身力量基础训练", "duration": "45分钟"}},
            {"date": "2026-04-30", "day": get_weekday("2026-04-30"),
             "session1": {"type": "功能性", "content": "Wall Balls + Kettlebell Swings", "duration": "30分钟"}},
            {"date": "2026-05-01", "day": get_weekday("2026-05-01"),
             "session1": {"type": "跑步", "content": "节奏跑6公里", "duration": "40分钟"},
             "session2": {"type": "恢复", "content": "拉伸/泡沫轴", "duration": "20分钟"}},
            {"date": "2026-05-02", "day": get_weekday("2026-05-02"),
             "session1": {"type": "功能性", "content": "Rowing + SkiErg", "duration": "30分钟"}},
            {"date": "2026-05-03", "day": get_weekday("2026-05-03"),
             "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "30分钟"}},
            {"date": "2026-05-04", "day": get_weekday("2026-05-04"),
             "session1": {"type": "综合", "content": "1公里跑 + 功能性循环", "duration": "60分钟"}},
            {"date": "2026-05-05", "day": get_weekday("2026-05-05"),
             "session1": {"type": "休息", "content": "完全休息或轻度活动"}}
        ]
    }
    
    # ==================== 第2周：5月6日-5月12日（强度提升）====================
    week2 = {
        "week": "第2周",
        "phase": "基础建立期",
        "start_date": "2026-05-06",
        "end_date": "2026-05-12",
        "focus": "增加跑步距离和功能性训练强度",
        "weekly_plan": [
            {"date": "2026-05-06", "day": get_weekday("2026-05-06"),
             "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "35分钟"},
             "session2": {"type": "力量", "content": "下肢力量训练", "duration": "45分钟"}},
            {"date": "2026-05-07", "day": get_weekday("2026-05-07"),
             "session1": {"type": "功能性", "content": "Wall Balls + Burpees", "duration": "35分钟"}},
            {"date": "2026-05-08", "day": get_weekday("2026-05-08"),
             "session1": {"type": "跑步", "content": "间歇跑：6x400米", "duration": "45分钟"},
             "session2": {"type": "恢复", "content": "瑜伽", "duration": "30分钟"}},
            {"date": "2026-05-09", "day": get_weekday("2026-05-09"),
             "session1": {"type": "功能性", "content": "Rowing + Sled Push/Pull模拟", "duration": "40分钟"}},
            {"date": "2026-05-10", "day": get_weekday("2026-05-10"),
             "session1": {"type": "跑步", "content": "轻松跑7公里", "duration": "40分钟"}},
            {"date": "2026-05-11", "day": get_weekday("2026-05-11"),
             "session1": {"type": "综合", "content": "2x(1公里跑 + 功能性站点)", "duration": "80分钟"}},
            {"date": "2026-05-12", "day": get_weekday("2026-05-12"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第3周：5月13日-5月19日（专项强化）====================
    week3 = {
        "week": "第3周",
        "phase": "专项强化期",
        "start_date": "2026-05-13",
        "end_date": "2026-05-19",
        "focus": "针对Hyrox专项训练",
        "weekly_plan": [
            {"date": "2026-05-13", "day": get_weekday("2026-05-13"),
             "session1": {"type": "跑步", "content": "节奏跑8公里", "duration": "50分钟"},
             "session2": {"type": "力量", "content": "核心训练", "duration": "30分钟"}},
            {"date": "2026-05-14", "day": get_weekday("2026-05-14"),
             "session1": {"type": "功能性", "content": "完整Hyrox站点练习", "duration": "60分钟"}},
            {"date": "2026-05-15", "day": get_weekday("2026-05-15"),
             "session1": {"type": "跑步", "content": "间歇跑：8x200米", "duration": "40分钟"},
             "session2": {"type": "恢复", "content": "冷热敷", "duration": "20分钟"}},
            {"date": "2026-05-16", "day": get_weekday("2026-05-16"),
             "session1": {"type": "功能性", "content": "Sled Push/Pull + Lunges", "duration": "45分钟"}},
            {"date": "2026-05-17", "day": get_weekday("2026-05-17"),
             "session1": {"type": "跑步", "content": "轻松跑8公里", "duration": "50分钟"}},
            {"date": "2026-05-18", "day": get_weekday("2026-05-18"),
             "session1": {"type": "综合", "content": "4x(1公里跑 + 2个功能站点)", "duration": "90分钟"}},
            {"date": "2026-05-19", "day": get_weekday("2026-05-19"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第4周：5月20日-5月26日（耐力提升）====================
    week4 = {
        "week": "第4周",
        "phase": "专项强化期",
        "start_date": "2026-05-20",
        "end_date": "2026-05-26",
        "focus": "提升整体耐力",
        "weekly_plan": [
            {"date": "2026-05-20", "day": get_weekday("2026-05-20"),
             "session1": {"type": "跑步", "content": "轻松跑9公里", "duration": "55分钟"},
             "session2": {"type": "力量", "content": "全身力量", "duration": "45分钟"}},
            {"date": "2026-05-21", "day": get_weekday("2026-05-21"),
             "session1": {"type": "功能性", "content": "高强度功能循环", "duration": "45分钟"}},
            {"date": "2026-05-22", "day": get_weekday("2026-05-22"),
             "session1": {"type": "跑步", "content": "节奏跑10公里", "duration": "60分钟"},
             "session2": {"type": "恢复", "content": "按摩/拉伸", "duration": "25分钟"}},
            {"date": "2026-05-23", "day": get_weekday("2026-05-23"),
             "session1": {"type": "功能性", "content": "Rowing + SkiErg间歇", "duration": "40分钟"}},
            {"date": "2026-05-24", "day": get_weekday("2026-05-24"),
             "session1": {"type": "跑步", "content": "轻松跑9公里", "duration": "55分钟"}},
            {"date": "2026-05-25", "day": get_weekday("2026-05-25"),
             "session1": {"type": "综合", "content": "模拟Hyrox半程", "duration": "120分钟"}},
            {"date": "2026-05-26", "day": get_weekday("2026-05-26"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第5周：5月27日-6月2日（强度峰值）====================
    week5 = {
        "week": "第5周",
        "phase": "强度峰值期",
        "start_date": "2026-05-27",
        "end_date": "2026-06-02",
        "focus": "达到训练强度峰值",
        "weekly_plan": [
            {"date": "2026-05-27", "day": get_weekday("2026-05-27"),
             "session1": {"type": "跑步", "content": "间歇跑：10x400米", "duration": "50分钟"},
             "session2": {"type": "力量", "content": "下肢爆发力", "duration": "40分钟"}},
            {"date": "2026-05-28", "day": get_weekday("2026-05-28"),
             "session1": {"type": "功能性", "content": "完整Hyrox站点计时", "duration": "50分钟"}},
            {"date": "2026-05-29", "day": get_weekday("2026-05-29"),
             "session1": {"type": "跑步", "content": "轻松跑10公里", "duration": "60分钟"},
             "session2": {"type": "恢复", "content": "瑜伽", "duration": "30分钟"}},
            {"date": "2026-05-30", "day": get_weekday("2026-05-30"),
             "session1": {"type": "功能性", "content": "Sled训练 + Push-Ups", "duration": "45分钟"}},
            {"date": "2026-05-31", "day": get_weekday("2026-05-31"),
             "session1": {"type": "跑步", "content": "节奏跑12公里", "duration": "70分钟"}},
            {"date": "2026-06-01", "day": get_weekday("2026-06-01"),
             "session1": {"type": "综合", "content": "完整Hyrox模拟", "duration": "90-120分钟"}},
            {"date": "2026-06-02", "day": get_weekday("2026-06-02"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第6周：6月3日-6月9日（调整期）====================
    week6 = {
        "week": "第6周",
        "phase": "调整期",
        "start_date": "2026-06-03",
        "end_date": "2026-06-09",
        "focus": "适当降低强度，促进恢复",
        "weekly_plan": [
            {"date": "2026-06-03", "day": get_weekday("2026-06-03"),
             "session1": {"type": "跑步", "content": "轻松跑7公里", "duration": "45分钟"},
             "session2": {"type": "力量", "content": "轻量全身训练", "duration": "35分钟"}},
            {"date": "2026-06-04", "day": get_weekday("2026-06-04"),
             "session1": {"type": "功能性", "content": "轻度功能循环", "duration": "30分钟"}},
            {"date": "2026-06-05", "day": get_weekday("2026-06-05"),
             "session1": {"type": "跑步", "content": "节奏跑8公里", "duration": "50分钟"},
             "session2": {"type": "恢复", "content": "泡沫轴放松", "duration": "20分钟"}},
            {"date": "2026-06-06", "day": get_weekday("2026-06-06"),
             "session1": {"type": "功能性", "content": "Rowing + Kettlebell", "duration": "35分钟"}},
            {"date": "2026-06-07", "day": get_weekday("2026-06-07"),
             "session1": {"type": "跑步", "content": "轻松跑7公里", "duration": "45分钟"}},
            {"date": "2026-06-08", "day": get_weekday("2026-06-08"),
             "session1": {"type": "综合", "content": "短距离模拟", "duration": "60分钟"}},
            {"date": "2026-06-09", "day": get_weekday("2026-06-09"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第7周：6月10日-6月16日（再次强化）====================
    week7 = {
        "week": "第7周",
        "phase": "再次强化期",
        "start_date": "2026-06-10",
        "end_date": "2026-06-16",
        "focus": "最后的强度提升",
        "weekly_plan": [
            {"date": "2026-06-10", "day": get_weekday("2026-06-10"),
             "session1": {"type": "跑步", "content": "间歇跑：6x800米", "duration": "55分钟"},
             "session2": {"type": "力量", "content": "核心稳定性", "duration": "40分钟"}},
            {"date": "2026-06-11", "day": get_weekday("2026-06-11"),
             "session1": {"type": "功能性", "content": "高强度功能循环", "duration": "50分钟"}},
            {"date": "2026-06-12", "day": get_weekday("2026-06-12"),
             "session1": {"type": "跑步", "content": "轻松跑9公里", "duration": "55分钟"},
             "session2": {"type": "恢复", "content": "按摩", "duration": "25分钟"}},
            {"date": "2026-06-13", "day": get_weekday("2026-06-13"),
             "session1": {"type": "功能性", "content": "完整站点练习", "duration": "45分钟"}},
            {"date": "2026-06-14", "day": get_weekday("2026-06-14"),
             "session1": {"type": "跑步", "content": "节奏跑10公里", "duration": "60分钟"}},
            {"date": "2026-06-15", "day": get_weekday("2026-06-15"),
             "session1": {"type": "综合", "content": "完整Hyrox模拟", "duration": "90-110分钟"}},
            {"date": "2026-06-16", "day": get_weekday("2026-06-16"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第8周：6月17日-6月23日（减量期）====================
    week8 = {
        "week": "第8周",
        "phase": "减量期(Taper)",
        "start_date": "2026-06-17",
        "end_date": "2026-06-23",
        "focus": "减少训练量，保持状态",
        "weekly_plan": [
            {"date": "2026-06-17", "day": get_weekday("2026-06-17"),
             "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "35分钟"},
             "session2": {"type": "力量", "content": "轻量力量", "duration": "30分钟"}},
            {"date": "2026-06-18", "day": get_weekday("2026-06-18"),
             "session1": {"type": "功能性", "content": "轻度功能练习", "duration": "30分钟"}},
            {"date": "2026-06-19", "day": get_weekday("2026-06-19"),
             "session1": {"type": "跑步", "content": "节奏跑5公里", "duration": "30分钟"},
             "session2": {"type": "恢复", "content": "瑜伽/拉伸", "duration": "30分钟"}},
            {"date": "2026-06-20", "day": get_weekday("2026-06-20"),
             "session1": {"type": "功能性", "content": "模拟站点技术练习", "duration": "35分钟"}},
            {"date": "2026-06-21", "day": get_weekday("2026-06-21"),
             "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "30分钟"}},
            {"date": "2026-06-22", "day": get_weekday("2026-06-22"),
             "session1": {"type": "综合", "content": "技术微调 + 短距离", "duration": "45分钟"}},
            {"date": "2026-06-23", "day": get_weekday("2026-06-23"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第9周：6月24日-6月30日（赛前准备）====================
    week9 = {
        "week": "第9周",
        "phase": "赛前准备期",
        "start_date": "2026-06-24",
        "end_date": "2026-06-30",
        "focus": "保持状态，调整心理",
        "weekly_plan": [
            {"date": "2026-06-24", "day": get_weekday("2026-06-24"),
             "session1": {"type": "跑步", "content": "轻松跑4公里", "duration": "25分钟"},
             "session2": {"type": "力量", "content": "激活训练", "duration": "25分钟"}},
            {"date": "2026-06-25", "day": get_weekday("2026-06-25"),
             "session1": {"type": "功能性", "content": "技术复习", "duration": "25分钟"}},
            {"date": "2026-06-26", "day": get_weekday("2026-06-26"),
             "session1": {"type": "跑步", "content": "轻量节奏跑3公里", "duration": "20分钟"},
             "session2": {"type": "恢复", "content": "泡沫轴", "duration": "15分钟"}},
            {"date": "2026-06-27", "day": get_weekday("2026-06-27"),
             "session1": {"type": "功能性", "content": "简短功能循环", "duration": "20分钟"}},
            {"date": "2026-06-28", "day": get_weekday("2026-06-28"),
             "session1": {"type": "跑步", "content": "轻松跑3公里", "duration": "18分钟"}},
            {"date": "2026-06-29", "day": get_weekday("2026-06-29"),
             "session1": {"type": "综合", "content": "赛前热身练习", "duration": "30分钟"}},
            {"date": "2026-06-30", "day": get_weekday("2026-06-30"),
             "session1": {"type": "休息", "content": "完全休息"}}
        ]
    }
    
    # ==================== 第10周：7月1日-7月6日（比赛周）====================
    week10 = {
        "week": "第10周",
        "phase": "比赛周",
        "start_date": "2026-07-01",
        "end_date": "2026-07-06",
        "focus": "保持放松，准备比赛",
        "weekly_plan": [
            {"date": "2026-07-01", "day": get_weekday("2026-07-01"),
             "session1": {"type": "跑步", "content": "轻松跑3公里", "duration": "18分钟"},
             "session2": {"type": "力量", "content": "激活训练", "duration": "20分钟"}},
            {"date": "2026-07-02", "day": get_weekday("2026-07-02"),
             "session1": {"type": "功能性", "content": "技术微调", "duration": "20分钟"}},
            {"date": "2026-07-03", "day": get_weekday("2026-07-03"),
             "session1": {"type": "跑步", "content": "轻松跑2公里", "duration": "12分钟"},
             "session2": {"type": "恢复", "content": "按摩放松", "duration": "20分钟"}},
            {"date": "2026-07-04", "day": get_weekday("2026-07-04"),
             "session1": {"type": "休息", "content": "完全休息或轻度活动"}},
            {"date": "2026-07-05", "day": get_weekday("2026-07-05"),
             "session1": {"type": "准备", "content": "赛前准备：检查装备、热身练习"},
             "session2": {"type": "心理", "content": "心理准备，可视化比赛"}},
            {"date": "2026-07-06", "day": get_weekday("2026-07-06"),
             "session1": {"type": "比赛", "content": "HYROX杭州站 - 全力以赴！"}}
        ]
    }
    
    plan["weekly_plans"].extend([week1, week2, week3, week4, week5, week6, week7, week8, week9, week10])
    
    # 训练建议
    recommendations = [
        "每周训练量递增不超过10%，避免过度训练",
        "每次训练后进行充分的拉伸和恢复",
        "保持充足的水分摄入和蛋白质补充",
        "保证每晚7-9小时的高质量睡眠",
        "根据身体反馈调整训练强度",
        "训练前充分热身，训练后适当冷身",
        "重点加强核心力量和下肢稳定性",
        "跑步时注意姿势，避免受伤",
        "功能性训练注重动作质量而非数量",
        "比赛前一周减少训练强度，保持放松心态",
        "比赛当天提前到达，做好热身准备",
        "比赛中合理分配体力，不要一开始冲刺",
        "每个功能站点之间的1公里跑保持稳定配速",
        "注意呼吸节奏，保持积极心态"
    ]
    
    plan["recommendations"] = recommendations
    
    return plan

def main():
    print("=" * 80)
    print("Hyrox杭州站 - 专项训练计划")
    print("=" * 80)
    print(f"比赛日期: 2026年7月6日")
    print(f"当前日期: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"剩余天数: {(datetime.strptime('2026-07-06', '%Y-%m-%d') - datetime.now()).days} 天")
    print("=" * 80)
    
    plan = create_hyrox_plan()
    
    print("\n" + "=" * 80)
    print("计划概览")
    print("=" * 80)
    print(f"当前日期: {plan['current_date']} ({plan['current_weekday']})")
    print(f"\n比赛信息:")
    print(f"  日期: {plan['race_info']['date']} ({plan['race_info']['weekday']})")
    print(f"  地点: {plan['race_info']['location']}")
    print(f"  类型: {plan['race_info']['description']}")
    
    print("\n训练目标:")
    for key, value in plan['goals'].items():
        print(f"  - {value}")
    
    print("\nHyrox比赛站点:")
    for station in plan['hyrox_stations']:
        print(f"  {station['order']}. {station['name']} - {station['description']}")
    
    print("\n" + "=" * 80)
    print("每周训练计划")
    print("=" * 80)
    
    for week in plan['weekly_plans']:
        print(f"\n{week['week']} ({week['start_date']} - {week['end_date']})")
        print(f"阶段: {week['phase']}")
        print(f"重点: {week['focus']}")
        print("每日安排:")
        for day in week['weekly_plan']:
            sessions = []
            if 'session1' in day:
                sessions.append(f"{day['session1']['type']}: {day['session1']['content']}")
            if 'session2' in day:
                sessions.append(f"{day['session2']['type']}: {day['session2']['content']}")
            print(f"  {day['date']} ({day['day']}): {' | '.join(sessions)}")
    
    print("\n" + "=" * 80)
    print("训练建议")
    print("=" * 80)
    for rec in plan['recommendations']:
        print(f"- {rec}")
    
    with open('hyrox_training_plan.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print("\n训练计划已保存到 hyrox_training_plan.json")

if __name__ == "__main__":
    main()