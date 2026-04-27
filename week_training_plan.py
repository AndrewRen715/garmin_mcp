#!/usr/bin/env python3
"""
为梦想小镇半程马拉松制定赛前训练计划
基于西湖半马的表现分析
"""

import datetime

# 计算日期
today = datetime.date.today()
race_day = today + datetime.timedelta(days=(6 - today.weekday()))  # 本周日

print("梦想小镇半程马拉松赛前训练计划")
print("=" * 60)
print(f"今天日期: {today}")
print(f"比赛日期: {race_day}")
print(f"距离比赛还有: {(race_day - today).days} 天")
print("=" * 60)
print()

# 训练计划
plan = [
    {
        "date": today,
        "day": today.strftime("%A"),
        "type": "恢复跑",
        "distance": "4-6 km",
        "pace": "轻松配速（6:00-6:30 /km）",
        "description": "西湖半马后的恢复跑，保持轻松，主要目的是促进血液循环，加速恢复"
    },
    {
        "date": today + datetime.timedelta(days=1),
        "day": (today + datetime.timedelta(days=1)).strftime("%A"),
        "type": "交叉训练",
        "distance": "30-45 分钟",
        "pace": "中等强度",
        "description": "游泳、骑自行车或椭圆机训练，保持心肺功能，同时给跑步肌肉休息"
    },
    {
        "date": today + datetime.timedelta(days=2),
        "day": (today + datetime.timedelta(days=2)).strftime("%A"),
        "type": "节奏跑",
        "distance": "8-10 km",
        "pace": "马拉松配速（5:00-5:15 /km）",
        "description": "保持稳定的马拉松配速，提高配速稳定性，为比赛做准备"
    },
    {
        "date": today + datetime.timedelta(days=3),
        "day": (today + datetime.timedelta(days=3)).strftime("%A"),
        "type": "休息日",
        "distance": "0 km",
        "pace": "-",
        "description": "完全休息，让身体充分恢复"
    },
    {
        "date": today + datetime.timedelta(days=4),
        "day": (today + datetime.timedelta(days=4)).strftime("%A"),
        "type": "轻松跑",
        "distance": "6-8 km",
        "pace": "轻松配速（6:00-6:30 /km）",
        "description": "保持轻松，维持跑步感觉，避免疲劳"
    },
    {
        "date": today + datetime.timedelta(days=5),
        "day": (today + datetime.timedelta(days=5)).strftime("%A"),
        "type": "赛前调整",
        "distance": "3-4 km",
        "pace": "轻松配速 + 短距离冲刺",
        "description": "轻松跑为主，加入2-3个100米的冲刺，激活肌肉，为比赛做最后准备"
    },
    {
        "date": today + datetime.timedelta(days=6),
        "day": (today + datetime.timedelta(days=6)).strftime("%A"),
        "type": "比赛日",
        "distance": "21.1 km",
        "pace": "目标配速（4:50-5:00 /km）",
        "description": "梦想小镇半程马拉松比赛"
    }
]

# 输出训练计划
for day in plan:
    print(f"{day['date']} ({day['day']})")
    print(f"类型: {day['type']}")
    print(f"距离: {day['distance']}")
    print(f"配速: {day['pace']}")
    print(f"说明: {day['description']}")
    print("-" * 60)
    print()

# 比赛策略建议
print("比赛策略建议")
print("=" * 60)
print("1. 起跑策略: 前3公里保持略慢于目标配速，避免起跑过快消耗过多体力")
print("2. 配速控制: 保持稳定配速，特别是在平坦路段，避免忽快忽慢")
print("3. 爬升处理: 遇到爬升时适当调整配速，采用小步高频的方式，保持节奏")
print("4. 补给策略: 每5公里补充水分，10公里后可考虑能量胶")
print("5. 心理调节: 保持积极心态，特别是在15公里后，关注呼吸和步频")
print("6. 冲刺策略: 最后2公里可适当加速，发挥最大潜力")
print()

# 基于西湖半马的针对性建议
print("基于西湖半马表现的针对性建议")
print("=" * 60)
print("1. 配速稳定性: 保持4:50-5:00的稳定配速，避免像西湖半马第13公里那样的大幅波动")
print("2. 爬升策略: 提前了解梦想小镇赛道的爬升点，做好心理准备，采用更科学的爬升技巧")
print("3. 心率管理: 保持在A强度（156-165 BPM），避免长时间处于I强度（165+ BPM）")
print("4. 热身充分: 比赛前进行充分的热身，包括动态拉伸和短距离冲刺")
print("5. 营养准备: 比赛前一天适当增加碳水化合物摄入，保证充足的能量储备")
print()

print("祝比赛顺利，取得理想成绩！")
