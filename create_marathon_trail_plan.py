#!/usr/bin/env python3
"""
综合训练计划：同时准备杭州马拉松和西湖跑山赛
包含攀岩训练作为辅助训练
"""
import json
import argparse
from datetime import datetime, timedelta

MARATHON_DATE = "2026-11-01"
TRAIL_RACE_DATE = "2026-11-22"
MARATHON_LOCATION = "杭州"
TRAIL_RACE_LOCATION = "西湖"

def get_weekday(date_str, lang='zh'):
    """获取日期对应的星期几
    
    Args:
        date_str (str): 日期字符串，格式为 'YYYY-MM-DD'
        lang (str): 语言选项，'zh' 为中文，'en' 为英文
    
    Returns:
        str: 星期几
    """
    date = datetime.strptime(date_str, '%Y-%m-%d')
    weekdays_zh = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekdays_en = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    weekdays = weekdays_zh if lang == 'zh' else weekdays_en
    return weekdays[date.weekday()]

def create_combo_plan(start_date=None):
    """创建综合训练计划（马拉松 + 越野跑 + 攀岩）
    
    Args:
        start_date (str): 训练开始日期，格式为 'YYYY-MM-DD'，默认使用当前日期
    
    Returns:
        dict: 训练计划字典，如果日期格式无效则返回None
    """
    try:
        if start_date:
            today = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            today = datetime.now()
        current_date = today.strftime('%Y-%m-%d')
    except ValueError:
        print(f"错误: 无效的日期格式 '{start_date}'，请使用 YYYY-MM-DD 格式")
        return None
    
    days_until_marathon = (datetime.strptime(MARATHON_DATE, '%Y-%m-%d') - today).days
    days_until_trail = (datetime.strptime(TRAIL_RACE_DATE, '%Y-%m-%d') - today).days
    
    plan = {
        "current_date": current_date,
        "current_weekday": get_weekday(current_date),
        "races": [
            {
                "name": "杭州马拉松",
                "date": MARATHON_DATE,
                "weekday": get_weekday(MARATHON_DATE),
                "location": MARATHON_LOCATION,
                "type": "马拉松",
                "distance": "42.195公里",
                "days_until": days_until_marathon
            },
            {
                "name": "西湖跑山赛",
                "date": TRAIL_RACE_DATE,
                "weekday": get_weekday(TRAIL_RACE_DATE),
                "location": TRAIL_RACE_LOCATION,
                "type": "越野跑",
                "distance": "约30公里",
                "days_until": days_until_trail
            }
        ],
        "goals": [
            "完成杭州马拉松（目标完赛时间：3小时10分钟）",
            "完成西湖跑山赛（目标：4小时20分，去年为4小时40分，提升20分钟）",
            "保持攀岩训练（开了季卡，希望可以完成5.11a），提升全身力量和协调性",
            "综合每周训练量：5-7小时"
        ],
        "training_types": {
            "跑步": ["轻松跑", "节奏跑", "间歇跑", "长距离跑", "恢复跑"],
            "越野跑": ["山地跑", "爬升训练", "技术训练", "长距离越野"],
            "攀岩": ["室内攀岩", "户外攀岩", "力量训练", "指力训练"],
            "力量": ["核心训练", "下肢力量", "全身力量", "稳定性训练"],
            "恢复": ["拉伸", "瑜伽", "泡沫轴", "按摩"]
        },
        "weekly_plans": []
    }
    
    week1_start = today + timedelta(days=(7 - today.weekday()) % 7 - 7)
    week1 = {
        "week": "第1周",
        "start_date": week1_start.strftime('%Y-%m-%d'),
        "end_date": (week1_start + timedelta(days=6)).strftime('%Y-%m-%d'),
        "phase": "基础建立期",
        "focus": "建立训练习惯，评估当前状态",
        "weekly_plan": [
            {"date": (week1_start + timedelta(days=0)).strftime('%Y-%m-%d'), "day": "周一", "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "35分钟"}},
            {"date": (week1_start + timedelta(days=1)).strftime('%Y-%m-%d'), "day": "周二", "session1": {"type": "跑步", "content": "次长距离跑8公里（可替换为越野）", "duration": "55分钟"}},
            {"date": (week1_start + timedelta(days=2)).strftime('%Y-%m-%d'), "day": "周三", "session1": {"type": "攀岩", "content": "室内攀岩基础", "duration": "60分钟"}},
            {"date": (week1_start + timedelta(days=3)).strftime('%Y-%m-%d'), "day": "周四", "session1": {"type": "跑步", "content": "强度课：节奏跑6公里", "duration": "40分钟"}},
            {"date": (week1_start + timedelta(days=4)).strftime('%Y-%m-%d'), "day": "周五", "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "35分钟"}},
            {"date": (week1_start + timedelta(days=5)).strftime('%Y-%m-%d'), "day": "周六", "session1": {"type": "跑步", "content": "长距离跑10公里（可替换为越野）", "duration": "70分钟"}},
            {"date": (week1_start + timedelta(days=6)).strftime('%Y-%m-%d'), "day": "周日", "session1": {"type": "恢复", "content": "瑜伽/拉伸", "duration": "45分钟"}}
        ]
    }
    
    week2 = {
        "week": "第2周",
        "phase": "基础建立期",
        "focus": "增加跑步距离，引入攀岩专项",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "跑步", "content": "次长距离跑10公里（可替换为越野）", "duration": "70分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "难度攀岩训练", "duration": "75分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：间歇跑6x400米", "duration": "45分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "力量", "content": "下肢力量训练", "duration": "50分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "越野跑", "content": "长距离越野12公里", "duration": "90分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "泡沫轴放松", "duration": "30分钟"}}
        ]
    }
    
    week3 = {
        "week": "第3周",
        "phase": "基础建立期",
        "focus": "长距离跑入门，攀岩进阶",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑7公里", "duration": "45分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "越野跑", "content": "次长距离越野10公里", "duration": "80分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "耐力攀岩训练", "duration": "90分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：节奏跑8公里", "duration": "55分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "35分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "跑步", "content": "长距离跑15公里（可替换为越野）", "duration": "110分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "完全休息或轻度活动"}}
        ]
    }
    
    week4 = {
        "week": "第4周",
        "phase": "强度提升期",
        "focus": "增加训练强度，越野技术训练",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "跑步", "content": "次长距离跑12公里（可替换为越野）", "duration": "85分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "指力训练 + 耐力", "duration": "75分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：间歇跑8x200米", "duration": "40分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "力量", "content": "全身力量训练", "duration": "55分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "越野跑", "content": "长距离越野18公里", "duration": "150分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "按摩/拉伸", "duration": "45分钟"}}
        ]
    }
    
    week5 = {
        "week": "第5周",
        "phase": "强度提升期",
        "focus": "马拉松配速训练，攀岩难度提升",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑8公里", "duration": "50分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "越野跑", "content": "次长距离越野14公里", "duration": "120分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "户外攀岩体验", "duration": "120分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：马拉松配速跑10公里", "duration": "65分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "跑步", "content": "长距离跑20公里（可替换为越野）", "duration": "150分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "瑜伽", "duration": "60分钟"}}
        ]
    }
    
    week6 = {
        "week": "第6周",
        "phase": "强度提升期",
        "focus": "混合训练，适应多种地形",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑7公里", "duration": "45分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "跑步", "content": "次长距离跑14公里（可替换为越野）", "duration": "100分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "室内攀岩进阶", "duration": "90分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：节奏跑10公里", "duration": "65分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "力量", "content": "核心+下肢力量", "duration": "50分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "越野跑", "content": "长距离越野22公里", "duration": "180分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "完全休息"}}
        ]
    }
    
    week7 = {
        "week": "第7周",
        "phase": "峰值准备期",
        "focus": "马拉松长距离峰值",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "35分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "跑步", "content": "次长距离跑16公里（可替换为越野）", "duration": "115分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "指力+耐力综合", "duration": "75分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：间歇跑10x400米", "duration": "50分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "跑步", "content": "长距离跑25公里（可替换为越野）", "duration": "190分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "泡沫轴+拉伸", "duration": "45分钟"}}
        ]
    }
    
    week8 = {
        "week": "第8周",
        "phase": "峰值准备期",
        "focus": "越野长距离峰值",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "越野跑", "content": "次长距离越野18公里", "duration": "150分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "户外攀岩训练", "duration": "120分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：马拉松配速跑8公里", "duration": "55分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "35分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "越野跑", "content": "长距离越野28公里", "duration": "240分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "按摩", "duration": "60分钟"}}
        ]
    }
    
    week9 = {
        "week": "第9周",
        "phase": "减量调整期",
        "focus": "马拉松赛前调整",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "35分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "跑步", "content": "次长距离跑10公里（可替换为越野）", "duration": "70分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "轻度攀岩恢复", "duration": "60分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "跑步", "content": "强度课：节奏跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "力量", "content": "轻量全身训练", "duration": "35分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "跑步", "content": "长距离跑12公里（赛前模拟）", "duration": "85分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "完全休息"}}
        ]
    }
    
    week10 = {
        "week": "第10周",
        "phase": "马拉松比赛周",
        "focus": "保持状态，准备比赛",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑4公里", "duration": "28分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "恢复", "content": "瑜伽/拉伸", "duration": "45分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "力量", "content": "激活训练", "duration": "25分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "恢复", "content": "完全休息"}},
            {"date": "", "day": "周六", "session1": {"type": "准备", "content": "赛前准备：检查装备、热身"}},
            {"date": MARATHON_DATE, "day": get_weekday(MARATHON_DATE), "session1": {"type": "比赛", "content": "杭州马拉松 - 42.195公里"}}
        ]
    }
    
    week11 = {
        "week": "第11周",
        "phase": "恢复调整期",
        "focus": "马拉松后恢复",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "恢复", "content": "完全休息"}},
            {"date": "", "day": "周二", "session1": {"type": "恢复", "content": "轻度拉伸/步行"}},
            {"date": "", "day": "周三", "session1": {"type": "跑步", "content": "轻松慢跑3公里", "duration": "25分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "攀岩", "content": "轻度攀岩恢复", "duration": "60分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "跑步", "content": "轻松跑5公里", "duration": "35分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "越野跑", "content": "山地恢复跑10公里", "duration": "80分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "瑜伽"}}
        ]
    }
    
    week12 = {
        "week": "第12周",
        "phase": "越野赛前准备",
        "focus": "西湖跑山赛专项训练",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "越野跑", "content": "次长距离越野15公里", "duration": "125分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "力量耐力训练", "duration": "75分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "越野跑", "content": "强度课：爬升训练", "duration": "60分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "力量", "content": "核心+下肢力量", "duration": "50分钟"}},
            {"date": "", "day": "周六", "session1": {"type": "越野跑", "content": "西湖赛道模拟25公里", "duration": "200分钟"}},
            {"date": "", "day": "周日", "session1": {"type": "恢复", "content": "泡沫轴放松"}}
        ]
    }
    
    week13 = {
        "week": "第13周",
        "phase": "越野赛比赛周",
        "focus": "保持状态，准备比赛",
        "weekly_plan": [
            {"date": "", "day": "周一", "session1": {"type": "跑步", "content": "轻松跑4公里", "duration": "28分钟"}},
            {"date": "", "day": "周二", "session1": {"type": "跑步", "content": "轻松跑6公里", "duration": "40分钟"}},
            {"date": "", "day": "周三", "session1": {"type": "攀岩", "content": "技术复习", "duration": "60分钟"}},
            {"date": "", "day": "周四", "session1": {"type": "恢复", "content": "拉伸/泡沫轴", "duration": "30分钟"}},
            {"date": "", "day": "周五", "session1": {"type": "恢复", "content": "完全休息"}},
            {"date": "", "day": "周六", "session1": {"type": "准备", "content": "赛前准备：检查装备、热身"}},
            {"date": TRAIL_RACE_DATE, "day": get_weekday(TRAIL_RACE_DATE), "session1": {"type": "比赛", "content": "西湖跑山赛 - 约30公里"}}
        ]
    }
    
    plan["weekly_plans"] = [week1, week2, week3, week4, week5, week6, week7, week8, week9, week10, week11, week12, week13]
    
    plan["recommendations"] = [
        "每周训练量递增不超过10%，避免过度训练",
        "攀岩训练可根据个人能力调整难度和时长",
        "长距离跑步后及时补充水分和营养",
        "越野跑注意安全，携带必要装备",
        "保证每晚7-9小时的高质量睡眠",
        "比赛前一周减少训练强度，保持放松心态",
        "马拉松和越野赛之间留出充足恢复时间",
        "攀岩训练有助于提升核心力量和协调性"
    ]
    
    return plan

def main():
    parser = argparse.ArgumentParser(description='生成综合训练计划（杭州马拉松 + 西湖跑山赛 + 攀岩）')
    parser.add_argument('--start-date', '-s', type=str, default=None,
                        help='训练开始日期，格式为 YYYY-MM-DD，默认使用当前日期')
    args = parser.parse_args()
    
    plan = create_combo_plan(start_date=args.start_date)
    
    if plan is None:
        return
    
    print("=" * 80)
    print("综合训练计划")
    print("=" * 80)
    
    for race in plan['races']:
        print(f"{race['name']}: {race['date']} ({race['weekday']})")
        print(f"  地点: {race['location']}")
        print(f"  类型: {race['type']} ({race['distance']})")
        print(f"  剩余天数: {race['days_until']} 天")
        print()
    
    print("=" * 80)
    print("训练目标")
    print("=" * 80)
    for goal in plan['goals']:
        print(f"  - {goal}")
    
    print("\n" + "=" * 80)
    print("训练类型")
    print("=" * 80)
    for category, items in plan['training_types'].items():
        print(f"  {category}: {', '.join(items)}")
    
    print("\n" + "=" * 80)
    print("每周训练计划概览")
    print("=" * 80)
    for week in plan['weekly_plans']:
        print(f"{week['week']}: {week['phase']} - {week['focus']}")
    
    print("\n" + "=" * 80)
    print("训练建议")
    print("=" * 80)
    for rec in plan['recommendations']:
        print(f"  - {rec}")
    
    with open('marathon_trail_plan.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, ensure_ascii=False, indent=2)
    
    print(f"\n训练计划已保存到 marathon_trail_plan.json")

if __name__ == "__main__":
    main()