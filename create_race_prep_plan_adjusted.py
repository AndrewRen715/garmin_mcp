#!/usr/bin/env python3
"""
为即将到来的越野赛制定训练计划，并为5月中的目标做准备（调整版：周六长距离，周四中高强度）
"""
import json
from datetime import datetime, timedelta

def get_weekday(date_str):
    """
    获取日期对应的星期几
    """
    date = datetime.strptime(date_str, '%Y-%m-%d')
    weekdays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    return weekdays[date.weekday()]

def create_race_prep_plan():
    """
    创建越野赛准备和恢复计划
    """
    # 基础信息
    today = datetime.now()
    current_date = today.strftime('%Y-%m-%d')
    
    # 比赛信息
    races = [
        {
            "date": "2026-04-12",
            "distance": 20,
            "elevation": 800,
            "description": "20KM越野赛，800米爬升",
            "weekday": get_weekday("2026-04-12")
        },
        {
            "date": "2026-04-19",
            "distance": 27,
            "elevation": 1100,
            "description": "27KM越野赛，1100米爬升",
            "weekday": get_weekday("2026-04-19")
        }
    ]
    
    # 目标：5月中恢复到周跑量50-60公里
    goal = {
        "target_weekly_mileage": "50-60公里",
        "target_date": "2026-05-15",
        "description": "恢复到周跑量50-60公里"
    }
    
    # 制定详细计划
    plan = {
        "current_date": current_date,
        "current_weekday": get_weekday(current_date),
        "races": races,
        "goal": goal,
        "weekly_plans": []
    }
    
    # 第1周：4月9日-4月14日（包含4.12比赛）
    week1 = {
        "week": "第1周",
        "start_date": "2026-04-09",
        "end_date": "2026-04-14",
        "total_distance": 35,
        "description": "为第一场越野赛做准备",
        "daily_plan": [
            {
                "date": "2026-04-09",
                "day": get_weekday("2026-04-09"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息，恢复体力"
            },
            {
                "date": "2026-04-10",
                "day": get_weekday("2026-04-10"),
                "type": "中高强度训练",
                "distance": 5,
                "description": "速度训练或间歇跑，30分钟"
            },
            {
                "date": "2026-04-11",
                "day": get_weekday("2026-04-11"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息，为比赛做准备"
            },
            {
                "date": "2026-04-12",
                "day": get_weekday("2026-04-12"),
                "type": "比赛",
                "distance": 20,
                "description": "20KM越野赛，800米爬升"
            },
            {
                "date": "2026-04-13",
                "day": get_weekday("2026-04-13"),
                "type": "恢复",
                "distance": 0,
                "description": "完全休息，肌肉恢复"
            },
            {
                "date": "2026-04-14",
                "day": get_weekday("2026-04-14"),
                "type": "恢复跑",
                "distance": 10,
                "description": "轻松恢复跑，45-60分钟"
            }
        ]
    }
    
    # 第2周：4月15日-4月21日（包含4.19比赛）
    week2 = {
        "week": "第2周",
        "start_date": "2026-04-15",
        "end_date": "2026-04-21",
        "total_distance": 40,
        "description": "为第二场越野赛做准备",
        "daily_plan": [
            {
                "date": "2026-04-15",
                "day": get_weekday("2026-04-15"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息，恢复体力"
            },
            {
                "date": "2026-04-16",
                "day": get_weekday("2026-04-16"),
                "type": "中高强度训练",
                "distance": 5,
                "description": "速度训练或间歇跑，30分钟"
            },
            {
                "date": "2026-04-17",
                "day": get_weekday("2026-04-17"),
                "type": "中强度训练",
                "distance": 8,
                "description": "丘陵跑或轻度爬升训练，45分钟"
            },
            {
                "date": "2026-04-18",
                "day": get_weekday("2026-04-18"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息，为比赛做准备"
            },
            {
                "date": "2026-04-19",
                "day": get_weekday("2026-04-19"),
                "type": "比赛",
                "distance": 27,
                "description": "27KM越野赛，1100米爬升"
            },
            {
                "date": "2026-04-20",
                "day": get_weekday("2026-04-20"),
                "type": "恢复",
                "distance": 0,
                "description": "完全休息，肌肉恢复"
            },
            {
                "date": "2026-04-21",
                "day": get_weekday("2026-04-21"),
                "type": "恢复跑",
                "distance": 10,
                "description": "轻松恢复跑，45-60分钟"
            }
        ]
    }
    
    # 第3周：4月22日-4月28日（赛后恢复）
    week3 = {
        "week": "第3周",
        "start_date": "2026-04-22",
        "end_date": "2026-04-28",
        "total_distance": 35,
        "description": "赛后恢复，开始逐步增加跑量",
        "daily_plan": [
            {
                "date": "2026-04-22",
                "day": get_weekday("2026-04-22"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息，恢复体力"
            },
            {
                "date": "2026-04-23",
                "day": get_weekday("2026-04-23"),
                "type": "恢复跑",
                "distance": 8,
                "description": "轻松跑，45分钟"
            },
            {
                "date": "2026-04-24",
                "day": get_weekday("2026-04-24"),
                "type": "中高强度训练",
                "distance": 10,
                "description": "速度训练或间歇跑，60分钟"
            },
            {
                "date": "2026-04-25",
                "day": get_weekday("2026-04-25"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-04-26",
                "day": get_weekday("2026-04-26"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-04-27",
                "day": get_weekday("2026-04-27"),
                "type": "长距离跑",
                "distance": 12,
                "description": "轻松长距离跑，75-90分钟"
            },
            {
                "date": "2026-04-28",
                "day": get_weekday("2026-04-28"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            }
        ]
    }
    
    # 第4周：4月29日-5月5日（增加跑量）
    week4 = {
        "week": "第4周",
        "start_date": "2026-04-29",
        "end_date": "2026-05-05",
        "total_distance": 45,
        "description": "增加跑量，接近目标",
        "daily_plan": [
            {
                "date": "2026-04-29",
                "day": get_weekday("2026-04-29"),
                "type": "恢复跑",
                "distance": 8,
                "description": "轻松跑，45分钟"
            },
            {
                "date": "2026-04-30",
                "day": get_weekday("2026-04-30"),
                "type": "中高强度训练",
                "distance": 10,
                "description": "速度训练或间歇跑，60分钟"
            },
            {
                "date": "2026-05-01",
                "day": get_weekday("2026-05-01"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-02",
                "day": get_weekday("2026-05-02"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-03",
                "day": get_weekday("2026-05-03"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-04",
                "day": get_weekday("2026-05-04"),
                "type": "长距离跑",
                "distance": 17,
                "description": "长距离跑，90-120分钟"
            },
            {
                "date": "2026-05-05",
                "day": get_weekday("2026-05-05"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            }
        ]
    }
    
    # 第5周：5月6日-5月12日（达到目标）
    week5 = {
        "week": "第5周",
        "start_date": "2026-05-06",
        "end_date": "2026-05-12",
        "total_distance": 55,
        "description": "达到目标周跑量",
        "daily_plan": [
            {
                "date": "2026-05-06",
                "day": get_weekday("2026-05-06"),
                "type": "恢复跑",
                "distance": 10,
                "description": "轻松跑，60分钟"
            },
            {
                "date": "2026-05-07",
                "day": get_weekday("2026-05-07"),
                "type": "中高强度训练",
                "distance": 12,
                "description": "速度训练或间歇跑，70分钟"
            },
            {
                "date": "2026-05-08",
                "day": get_weekday("2026-05-08"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-09",
                "day": get_weekday("2026-05-09"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-10",
                "day": get_weekday("2026-05-10"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-11",
                "day": get_weekday("2026-05-11"),
                "type": "长距离跑",
                "distance": 21,
                "description": "长距离跑，120-150分钟"
            },
            {
                "date": "2026-05-12",
                "day": get_weekday("2026-05-12"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            }
        ]
    }
    
    # 第6周：5月13日-5月19日（维持目标）
    week6 = {
        "week": "第6周",
        "start_date": "2026-05-13",
        "end_date": "2026-05-19",
        "total_distance": 60,
        "description": "维持目标周跑量",
        "daily_plan": [
            {
                "date": "2026-05-13",
                "day": get_weekday("2026-05-13"),
                "type": "恢复跑",
                "distance": 10,
                "description": "轻松跑，60分钟"
            },
            {
                "date": "2026-05-14",
                "day": get_weekday("2026-05-14"),
                "type": "中高强度训练",
                "distance": 12,
                "description": "速度训练或间歇跑，70分钟"
            },
            {
                "date": "2026-05-15",
                "day": get_weekday("2026-05-15"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-16",
                "day": get_weekday("2026-05-16"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-17",
                "day": get_weekday("2026-05-17"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            },
            {
                "date": "2026-05-18",
                "day": get_weekday("2026-05-18"),
                "type": "长距离跑",
                "distance": 25,
                "description": "长距离跑，150-180分钟"
            },
            {
                "date": "2026-05-19",
                "day": get_weekday("2026-05-19"),
                "type": "休息",
                "distance": 0,
                "description": "完全休息"
            }
        ]
    }
    
    # 添加所有周计划
    plan["weekly_plans"].append(week1)
    plan["weekly_plans"].append(week2)
    plan["weekly_plans"].append(week3)
    plan["weekly_plans"].append(week4)
    plan["weekly_plans"].append(week5)
    plan["weekly_plans"].append(week6)
    
    # 训练建议
    recommendations = [
        "在比赛前确保充分休息，避免过度训练",
        "比赛后给予身体足够的恢复时间，尤其是肌肉和关节",
        "逐步增加跑量，避免突然增加导致受伤",
        "保持充足的水分摄入和营养补充",
        "注意睡眠质量，保证每晚7-9小时的睡眠时间",
        "在长距离训练后进行适当的拉伸和恢复活动",
        "根据身体状况调整训练计划，如有不适及时休息",
        "比赛前一周减少训练强度，进行 taper",
        "比赛当天提前到达场地，做好热身准备",
        "比赛中注意配速，避免一开始跑得太快",
        "周四的中高强度训练可以包括间歇跑、速度训练或法特莱克训练",
        "周六的长距离跑应该保持轻松的配速，逐渐增加距离"
    ]
    
    plan["recommendations"] = recommendations
    
    return plan

def main():
    """
    主函数
    """
    print("=" * 80)
    print("越野赛准备与恢复训练计划")
    print("=" * 80)
    print("为即将到来的越野赛制定训练计划，并为5月中的目标做准备")
    print("=" * 80)
    
    # 创建训练计划
    plan = create_race_prep_plan()
    
    # 输出计划概览
    print("\n" + "=" * 80)
    print("计划概览")
    print("=" * 80)
    print(f"当前日期: {plan['current_date']} ({plan['current_weekday']})")
    print(f"目标: {plan['goal']['description']} (到{plan['goal']['target_date']})")
    
    print("\n即将到来的比赛:")
    for race in plan['races']:
        print(f"- {race['date']} ({race['weekday']}): {race['description']}")
    
    # 输出每周计划
    print("\n" + "=" * 80)
    print("详细训练计划")
    print("=" * 80)
    
    for week in plan['weekly_plans']:
        print(f"\n{week['week']} ({week['start_date']} - {week['end_date']})")
        print(f"总跑量: {week['total_distance']} 公里")
        print(f"描述: {week['description']}")
        print("每日计划:")
        for day in week['daily_plan']:
            print(f"  {day['date']} ({day['day']}): {day['type']} - {day['distance']} 公里 - {day['description']}")
    
    # 输出建议
    print("\n" + "=" * 80)
    print("训练建议")
    print("=" * 80)
    for recommendation in plan['recommendations']:
        print(f"- {recommendation}")
    
    # 保存计划到JSON文件
    with open('race_prep_plan_adjusted.json', 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2, ensure_ascii=False)
    
    print("\n计划已保存到 race_prep_plan_adjusted.json")

if __name__ == "__main__":
    main()
