#!/usr/bin/env python3
"""
获取佳明最新的训练数据并安排最近的恢复训练
"""
import json
import os
import sys
from datetime import datetime, timedelta

# 尝试导入garminconnect库
try:
    from garminconnect import Garmin
    garmin_available = True
except ImportError:
    garmin_available = False

def get_token_path():
    """
    获取token存储路径
    """
    return os.getenv("GARMINTOKENS") or "~/.garminconnect"

def token_exists():
    """
    检查token是否存在
    """
    token_path = get_token_path()
    expanded_path = os.path.expanduser(token_path)
    return os.path.exists(expanded_path)

def get_garmin_client():
    """
    获取Garmin客户端
    """
    if not garmin_available:
        print("错误: 未安装garminconnect库。请使用 'pip install garminconnect' 安装。")
        return None
    
    try:
        token_path = get_token_path()
        expanded_token_path = os.path.expanduser(token_path)
        
        # 首先尝试使用token登录
        if token_exists():
            print(f"尝试使用现有token登录: {expanded_token_path}")
            # 默认使用中国区
            garmin = Garmin(is_cn=True)
            garmin.login(expanded_token_path)
            print("使用token登录成功！")
        else:
            # 如果token不存在，要求用户输入凭据
            print("未找到现有token，需要输入凭据登录...")
            email = input("请输入您的Garmin Connect邮箱: ")
            password = input("请输入您的Garmin Connect密码: ")
            
            # 初始化Garmin客户端，默认使用中国区
            print("正在登录Garmin Connect中国区...")
            garmin = Garmin(email, password, is_cn=True)
            garmin.login()
            
            # 保存token
            print(f"正在保存token到: {expanded_token_path}")
            garmin.garth.dump(expanded_token_path)
            print("token保存成功，下次登录将自动使用！")
        
        return garmin
        
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

def get_latest_training_data(garmin_client, days=7):
    """
    获取最新的训练数据
    """
    try:
        # 获取最近的活动记录
        print("正在获取最近的活动记录...")
        activities = garmin_client.get_activities(0, 20)  # 获取最近20个活动
        
        if not activities:
            print("未找到活动记录")
            return None
        
        # 整理活动数据
        curated = {
            "count": len(activities),
            "activities": []
        }
        
        for a in activities:
            activity = {
                "id": a.get('activityId'),
                "name": a.get('activityName'),
                "type": a.get('activityType', {}).get('typeKey'),
                "start_time": a.get('startTimeLocal'),
                "distance_meters": a.get('distance'),
                "duration_seconds": a.get('duration'),
                "calories": a.get('calories'),
                "avg_hr_bpm": a.get('averageHR'),
                "max_hr_bpm": a.get('maxHR'),
                "steps": a.get('steps'),
            }
            # 移除None值
            activity = {k: v for k, v in activity.items() if v is not None}
            curated["activities"].append(activity)
        
        # 获取健康数据
        print("\n正在获取健康数据...")
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        health_data = {
            "date_range": f"{start_date} to {end_date}",
            "body_battery": [],
            "sleep": [],
            "heart_rate": [],
            "stress": []
        }
        
        # 获取身体电量数据
        try:
            print("获取身体电量数据...")
            body_battery = garmin_client.get_body_battery(start_date, end_date)
            if body_battery:
                health_data["body_battery"] = body_battery
                print(f"获取了{len(body_battery)}天的身体电量数据")
        except Exception as e:
            print(f"获取身体电量数据失败: {e}")
        
        # 获取睡眠数据
        try:
            print("获取睡眠数据...")
            sleep_data = garmin_client.get_sleep_data(end_date)
            if sleep_data:
                health_data["sleep"].append(sleep_data)
                print("获取了最新的睡眠数据")
        except Exception as e:
            print(f"获取睡眠数据失败: {e}")
        
        # 获取心率数据
        try:
            print("获取心率数据...")
            hr_data = garmin_client.get_heart_rates(end_date)
            if hr_data:
                health_data["heart_rate"].append(hr_data)
                print("获取了最新的心率数据")
        except Exception as e:
            print(f"获取心率数据失败: {e}")
        
        # 获取压力数据
        try:
            print("获取压力数据...")
            stress_data = garmin_client.get_stress_data(end_date)
            if stress_data:
                health_data["stress"].append(stress_data)
                print("获取了最新的压力数据")
        except Exception as e:
            print(f"获取压力数据失败: {e}")
        
        return {
            "activities": curated,
            "health_data": health_data
        }
        
    except Exception as e:
        print(f"获取训练数据失败: {str(e)}")
        return None

def analyze_training_status(health_data):
    """
    分析训练状态
    """
    analysis = {
        "recovery_score": 50,  # 默认值
        "sleep_quality": "中等",
        "body_battery_status": "中等",
        "stress_level": "中等",
        "recommendations": []
    }
    
    # 分析身体电量
    if health_data.get("body_battery"):
        latest_battery = health_data["body_battery"][-1] if health_data["body_battery"] else None
        if latest_battery:
            # 简化计算：基于最近的身体电量状态
            charged = latest_battery.get("charged", 0) or 0
            drained = latest_battery.get("drained", 0) or 0
            if charged > drained:
                analysis["body_battery_status"] = "良好"
                analysis["recovery_score"] += 15
            else:
                analysis["body_battery_status"] = "偏低"
                analysis["recovery_score"] -= 10
    
    # 分析睡眠数据
    if health_data.get("sleep"):
        latest_sleep = health_data["sleep"][0] if health_data["sleep"] else None
        if latest_sleep:
            sleep_score = latest_sleep.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value')
            if sleep_score:
                if sleep_score >= 80:
                    analysis["sleep_quality"] = "良好"
                    analysis["recovery_score"] += 15
                elif sleep_score >= 60:
                    analysis["sleep_quality"] = "中等"
                else:
                    analysis["sleep_quality"] = "较差"
                    analysis["recovery_score"] -= 10
    
    # 分析压力数据
    if health_data.get("stress"):
        latest_stress = health_data["stress"][0] if health_data["stress"] else None
        if latest_stress:
            avg_stress = latest_stress.get('avgStressLevel')
            if avg_stress:
                if avg_stress <= 30:
                    analysis["stress_level"] = "低"
                    analysis["recovery_score"] += 10
                elif avg_stress <= 50:
                    analysis["stress_level"] = "中等"
                else:
                    analysis["stress_level"] = "高"
                    analysis["recovery_score"] -= 10
    
    # 分析心率数据
    if health_data.get("heart_rate"):
        latest_hr = health_data["heart_rate"][0] if health_data["heart_rate"] else None
        if latest_hr:
            resting_hr = latest_hr.get('restingHeartRate')
            if resting_hr:
                # 假设正常静息心率在60-70之间
                if 60 <= resting_hr <= 70:
                    analysis["recovery_score"] += 10
                elif resting_hr > 80:
                    analysis["recovery_score"] -= 10
    
    # 确保恢复分数在0-100之间
    analysis["recovery_score"] = max(0, min(100, analysis["recovery_score"]))
    
    # 生成建议
    if analysis["recovery_score"] >= 80:
        analysis["recommendations"].append("您的恢复状态非常好，可以进行高强度训练。")
        analysis["recommendations"].append("建议：可以安排一次高质量的速度训练或长距离跑。")
    elif analysis["recovery_score"] >= 60:
        analysis["recommendations"].append("您的恢复状态良好，可以进行中等强度训练。")
        analysis["recommendations"].append("建议：可以安排一次轻松跑或中等强度的有氧训练。")
    elif analysis["recovery_score"] >= 40:
        analysis["recommendations"].append("您的恢复状态一般，建议进行低强度训练。")
        analysis["recommendations"].append("建议：可以安排一次非常轻松的恢复跑或交叉训练。")
    else:
        analysis["recommendations"].append("您的恢复状态较差，建议休息。")
        analysis["recommendations"].append("建议：今天完全休息，或进行非常轻度的活动如散步或瑜伽。")
    
    # 基于具体指标的建议
    if analysis["sleep_quality"] == "较差":
        analysis["recommendations"].append("注意：您的睡眠质量较差，建议改善睡眠环境和作息时间。")
    
    if analysis["body_battery_status"] == "偏低":
        analysis["recommendations"].append("注意：您的身体电量偏低，建议增加休息时间。")
    
    if analysis["stress_level"] == "高":
        analysis["recommendations"].append("注意：您的压力水平较高，建议进行放松活动如冥想或深呼吸。")
    
    return analysis

def plan_recovery_training(analysis, activities):
    """
    安排恢复训练
    """
    plan = {
        "recovery_score": analysis["recovery_score"],
        "recovery_level": "",
        "next_training": [],
        "recovery_strategies": []
    }
    
    # 确定恢复水平
    if analysis["recovery_score"] >= 80:
        plan["recovery_level"] = "完全恢复"
    elif analysis["recovery_score"] >= 60:
        plan["recovery_level"] = "良好恢复"
    elif analysis["recovery_score"] >= 40:
        plan["recovery_level"] = "部分恢复"
    else:
        plan["recovery_level"] = "需要休息"
    
    # 安排接下来的训练
    today = datetime.now()
    
    if analysis["recovery_score"] >= 80:
        # 完全恢复，可以安排高强度训练
        plan["next_training"].append({
            "date": (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            "type": "高强度训练",
            "description": "速度训练或间歇跑，时长45-60分钟"
        })
        plan["next_training"].append({
            "date": (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            "type": "中强度训练",
            "description": "节奏跑或法特莱克训练，时长60-75分钟"
        })
    elif analysis["recovery_score"] >= 60:
        # 良好恢复，可以安排中等强度训练
        plan["next_training"].append({
            "date": (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            "type": "中等强度训练",
            "description": "轻松跑或有氧训练，时长45-60分钟"
        })
        plan["next_training"].append({
            "date": (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            "type": "低强度训练",
            "description": "恢复跑或交叉训练，时长30-45分钟"
        })
    elif analysis["recovery_score"] >= 40:
        # 部分恢复，建议低强度训练
        plan["next_training"].append({
            "date": (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            "type": "低强度训练",
            "description": "非常轻松的恢复跑或步行，时长30分钟"
        })
        plan["next_training"].append({
            "date": (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            "type": "休息",
            "description": "完全休息或进行轻度伸展"
        })
    else:
        # 需要休息
        plan["next_training"].append({
            "date": (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            "type": "休息",
            "description": "完全休息，避免任何剧烈运动"
        })
        plan["next_training"].append({
            "date": (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            "type": "轻度活动",
            "description": "散步或瑜伽，时长20-30分钟"
        })
    
    # 恢复策略
    plan["recovery_strategies"].append("保证充足的睡眠（每晚7-9小时）")
    plan["recovery_strategies"].append("保持充足的水分摄入")
    plan["recovery_strategies"].append("摄入足够的蛋白质和营养物质")
    
    if analysis["sleep_quality"] == "较差":
        plan["recovery_strategies"].append("改善睡眠环境：保持房间黑暗、安静和凉爽")
        plan["recovery_strategies"].append("建立规律的睡眠时间表")
    
    if analysis["stress_level"] == "高":
        plan["recovery_strategies"].append("每天进行10-15分钟的冥想或深呼吸练习")
        plan["recovery_strategies"].append("考虑进行轻度的伸展或瑜伽来减轻压力")
    
    return plan

def main():
    """
    主函数
    """
    print("=" * 80)
    print("佳明训练数据获取与恢复训练安排")
    print("=" * 80)
    print("此工具将获取您的最新训练数据，并根据恢复状态安排恢复训练")
    print("=" * 80)
    
    # 检查garminconnect库是否可用
    if not garmin_available:
        print("\ngarminconnect库未安装，无法直接连接Garmin Connect。")
        print("请使用 'pip install garminconnect' 安装。")
        return
    
    # 获取Garmin客户端
    garmin_client = get_garmin_client()
    if not garmin_client:
        print("\n无法初始化Garmin客户端，程序退出。")
        return
    
    # 获取最新的训练数据
    training_data = get_latest_training_data(garmin_client)
    if not training_data:
        print("\n无法获取训练数据，程序退出。")
        return
    
    # 分析训练状态
    print("\n分析训练状态...")
    analysis = analyze_training_status(training_data["health_data"])
    
    # 安排恢复训练
    print("\n安排恢复训练...")
    recovery_plan = plan_recovery_training(analysis, training_data["activities"])
    
    # 输出结果
    print("\n" + "=" * 80)
    print("训练数据概览")
    print("=" * 80)
    print(f"最近活动数量: {training_data['activities']['count']}")
    if training_data['activities']['activities']:
        latest_activity = training_data['activities']['activities'][0]
        print(f"最近一次活动: {latest_activity['name']}")
        print(f"活动类型: {latest_activity['type']}")
        print(f"开始时间: {latest_activity['start_time']}")
        print(f"距离: {latest_activity['distance_meters']/1000:.2f} km")
        print(f"时长: {latest_activity['duration_seconds']//60} 分钟")
        if 'avg_hr_bpm' in latest_activity:
            print(f"平均心率: {latest_activity['avg_hr_bpm']} BPM")
    
    print("\n" + "=" * 80)
    print("恢复状态分析")
    print("=" * 80)
    print(f"恢复分数: {analysis['recovery_score']}/100")
    print(f"睡眠质量: {analysis['sleep_quality']}")
    print(f"身体电量状态: {analysis['body_battery_status']}")
    print(f"压力水平: {analysis['stress_level']}")
    
    print("\n" + "=" * 80)
    print("恢复建议")
    print("=" * 80)
    for recommendation in analysis['recommendations']:
        print(f"- {recommendation}")
    
    print("\n" + "=" * 80)
    print("恢复训练计划")
    print("=" * 80)
    print(f"恢复水平: {recovery_plan['recovery_level']}")
    
    print("\n接下来的训练安排:")
    for training in recovery_plan['next_training']:
        print(f"{training['date']}: {training['type']} - {training['description']}")
    
    print("\n恢复策略:")
    for strategy in recovery_plan['recovery_strategies']:
        print(f"- {strategy}")
    
    # 保存数据到JSON文件
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "training_data": training_data,
        "analysis": analysis,
        "recovery_plan": recovery_plan
    }
    
    with open('latest_training_data_and_recovery_plan.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n数据已保存到 latest_training_data_and_recovery_plan.json")

if __name__ == "__main__":
    main()
