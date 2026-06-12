#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
攀岩训练记录与分析工具
记录攀岩训练数据，跟踪进度，分析提升趋势
"""
import json
import argparse
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

LOG_FILE = "climbing_log.json"

def load_log():
    """加载攀岩记录"""
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"climbs": [], "projects": [], "goals": []}
    except json.JSONDecodeError:
        print("错误：日志文件格式不正确")
        return {"climbs": [], "projects": [], "goals": []}

def save_log(log):
    """保存攀岩记录"""
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def add_climb(log, date, gym, grade, type_climb, notes=""):
    """添加攀岩记录"""
    climb = {
        "date": date,
        "gym": gym,
        "grade": grade,
        "type": type_climb,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    log["climbs"].append(climb)
    save_log(log)
    print(f"✅ 已添加攀岩记录: {date} {gym} {grade} ({type_climb})")

def add_project(log, name, grade, status="in_progress"):
    """添加攀岩项目"""
    project = {
        "name": name,
        "grade": grade,
        "status": status,
        "start_date": datetime.now().strftime('%Y-%m-%d'),
        "attempts": 0,
        "completed": False
    }
    log["projects"].append(project)
    save_log(log)
    print(f"✅ 已添加攀岩项目: {name} ({grade})")

def add_goal(log, description, target_date, target_grade=""):
    """添加攀岩目标"""
    goal = {
        "description": description,
        "target_date": target_date,
        "target_grade": target_grade,
        "created_date": datetime.now().strftime('%Y-%m-%d'),
        "completed": False
    }
    log["goals"].append(goal)
    save_log(log)
    print(f"✅ 已添加攀岩目标: {description}")

def analyze_progress(log):
    """分析攀岩进度"""
    climbs = log.get("climbs", [])
    if not climbs:
        print("暂无攀岩记录")
        return
    
    print("\n" + "="*80)
    print("攀岩训练进度分析")
    print("="*80)
    
    total_climbs = len(climbs)
    unique_dates = len(set(c["date"] for c in climbs))
    print(f"总攀岩次数: {total_climbs}")
    print(f"攀岩天数: {unique_dates}")
    
    grade_counts = {}
    for climb in climbs:
        grade = climb["grade"]
        grade_counts[grade] = grade_counts.get(grade, 0) + 1
    
    print("\n【难度分布】")
    for grade in sorted(grade_counts.keys()):
        count = grade_counts[grade]
        percentage = (count / total_climbs) * 100
        print(f"  {grade}: {count}次 ({percentage:.1f}%)")
    
    recent_climbs = sorted(climbs, key=lambda x: x["date"], reverse=True)[:10]
    print("\n【最近攀岩记录】")
    for climb in recent_climbs:
        print(f"  {climb['date']} | {climb['gym']} | {climb['grade']} | {climb['type']}")
    
    if log.get("projects"):
        print("\n【进行中的项目】")
        for project in log["projects"]:
            if project["status"] == "in_progress":
                print(f"  {project['name']} ({project['grade']}) - 尝试次数: {project['attempts']}")
    
    if log.get("goals"):
        print("\n【攀岩目标】")
        for goal in log["goals"]:
            status = "✅" if goal["completed"] else "🔄"
            print(f"  {status} {goal['description']} (目标日期: {goal['target_date']})")

def list_climbs(log):
    """列出所有攀岩记录"""
    climbs = log.get("climbs", [])
    if not climbs:
        print("暂无攀岩记录")
        return
    
    sorted_climbs = sorted(climbs, key=lambda x: x["date"], reverse=True)
    
    print("\n" + "="*80)
    print("攀岩记录列表")
    print("="*80)
    print(f"{'日期':<12} {'场馆':<15} {'难度':<8} {'类型':<10} {'备注'}")
    print("-"*80)
    
    for climb in sorted_climbs:
        print(f"{climb['date']:<12} {climb['gym']:<15} {climb['grade']:<8} {climb['type']:<10} {climb['notes']}")

def main():
    parser = argparse.ArgumentParser(description='攀岩训练记录与分析工具')
    subparsers = parser.add_subparsers(dest='command')
    
    add_parser = subparsers.add_parser('add', help='添加攀岩记录')
    add_parser.add_argument('--date', '-d', default=datetime.now().strftime('%Y-%m-%d'), help='日期 (YYYY-MM-DD)')
    add_parser.add_argument('--gym', '-g', required=True, help='攀岩场馆')
    add_parser.add_argument('--grade', '-gr', required=True, help='攀岩难度 (如 5.10a, V4)')
    add_parser.add_argument('--type', '-t', choices=['lead', 'bouldering', 'toprope', 'speed'], required=True, help='攀岩类型')
    add_parser.add_argument('--notes', '-n', default="", help='备注')
    
    project_parser = subparsers.add_parser('project', help='添加攀岩项目')
    project_parser.add_argument('--name', '-n', required=True, help='项目名称')
    project_parser.add_argument('--grade', '-gr', required=True, help='目标难度')
    
    goal_parser = subparsers.add_parser('goal', help='添加攀岩目标')
    goal_parser.add_argument('--description', '-d', required=True, help='目标描述')
    goal_parser.add_argument('--target-date', '-t', required=True, help='目标日期')
    goal_parser.add_argument('--target-grade', '-gr', default="", help='目标难度')
    
    subparsers.add_parser('list', help='列出所有攀岩记录')
    subparsers.add_parser('analyze', help='分析攀岩进度')
    
    args = parser.parse_args()
    
    log = load_log()
    
    if args.command == 'add':
        add_climb(log, args.date, args.gym, args.grade, args.type, args.notes)
    elif args.command == 'project':
        add_project(log, args.name, args.grade)
    elif args.command == 'goal':
        add_goal(log, args.description, args.target_date, args.target_grade)
    elif args.command == 'list':
        list_climbs(log)
    elif args.command == 'analyze':
        analyze_progress(log)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()