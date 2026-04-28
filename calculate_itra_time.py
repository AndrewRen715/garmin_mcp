#!/usr/bin/env python3
"""
根据42K完赛时间和ITRA分数，计算27K需要的完赛时间
"""

def calculate_27k_time(forty_two_k_time, forty_two_k_distance=42.0, twenty_seven_k_distance=27.0, 
                      forty_two_k_mountain_level=6, twenty_seven_k_mountain_level=4):
    """
    根据42K完赛时间，计算27K需要的完赛时间
    使用简单的比例计算，考虑距离缩短和山地等级差异
    
    参数:
        forty_two_k_time: 42K完赛时间（小时）
        forty_two_k_distance: 42K距离（公里）
        twenty_seven_k_distance: 27K距离（公里）
        forty_two_k_mountain_level: 42K山地等级
        twenty_seven_k_mountain_level: 27K山地等级
    
    返回:
        27K需要的完赛时间（小时）
    """
    # 计算42K的平均速度
    avg_speed_42k = forty_two_k_distance / forty_two_k_time
    
    # 考虑山地等级差异
    # 山地等级4比等级6容易，假设速度提升10%
    difficulty_adjustment = (forty_two_k_mountain_level / twenty_seven_k_mountain_level) ** 0.3
    
    # 短距离比赛通常速度稍快，假设27K的速度比42K快5%
    avg_speed_27k = avg_speed_42k * 1.05 * difficulty_adjustment
    
    # 计算27K的完赛时间
    twenty_seven_k_time = twenty_seven_k_distance / avg_speed_27k
    
    return twenty_seven_k_time

def calculate_itra_score_adjustment(distance_km, reference_score=510, reference_distance=42.0, 
                                  forty_two_k_mountain_level=6, twenty_seven_k_mountain_level=4):
    """
    根据距离和山地等级调整ITRA分数
    参考：ITRA分数与距离和难度相关
    """
    # 考虑距离和山地等级的调整
    distance_adjustment = (distance_km / reference_distance) ** 0.8
    difficulty_adjustment = (twenty_seven_k_mountain_level / forty_two_k_mountain_level) ** 0.5
    
    score_adjustment = distance_adjustment * difficulty_adjustment
    adjusted_score = reference_score * score_adjustment
    return adjusted_score

if __name__ == "__main__":
    # 42K数据
    forty_two_k_time = 7.0  # 7小时
    forty_two_k_score = 510
    forty_two_k_mountain_level = 6  # 42K山地等级
    twenty_seven_k_mountain_level = 4  # 27K山地等级
    
    # 计算27K需要的完赛时间
    twenty_seven_k_time = calculate_27k_time(forty_two_k_time, 
                                           forty_two_k_mountain_level=forty_two_k_mountain_level,
                                           twenty_seven_k_mountain_level=twenty_seven_k_mountain_level)
    
    # 转换为小时和分钟
    hours = int(twenty_seven_k_time)
    minutes = int((twenty_seven_k_time - hours) * 60)
    
    # 计算调整后的ITRA分数
    adjusted_score = calculate_itra_score_adjustment(27.0, forty_two_k_score,
                                                  forty_two_k_mountain_level=forty_two_k_mountain_level,
                                                  twenty_seven_k_mountain_level=twenty_seven_k_mountain_level)
    
    print(f"42K完赛时间: {int(forty_two_k_time)}小时{int((forty_two_k_time - int(forty_two_k_time)) * 60)}分钟")
    print(f"42K ITRA分数: {forty_two_k_score}")
    print(f"42K 山地等级: {forty_two_k_mountain_level}")
    print(f"27K 山地等级: {twenty_seven_k_mountain_level}")
    print(f"\n27K需要的完赛时间: {hours}小时{minutes}分钟")
    print(f"27K 估计ITRA分数: {round(adjusted_score, 2)}")
    
    # 提供更详细的分析
    print(f"\n详细分析:")
    print(f"42K平均速度: {round(42.0 / forty_two_k_time, 2)} km/h")
    print(f"27K估计平均速度: {round(27.0 / twenty_seven_k_time, 2)} km/h")
    
    # 提供不同配速下的完赛时间和分数估算
    print(f"\n不同配速下的27K完赛时间和ITRA分数估算:")
    print("配速(分钟/km) | 完赛时间 | 估计ITRA分数")
    print("-" * 40)
    
    # 考虑山地等级差异的分数计算
    for pace_min in [7.5, 8, 8.5, 9, 9.5, 10]:
        time_hours = (pace_min * 27) / 60
        hours_pace = int(time_hours)
        minutes_pace = int((time_hours - hours_pace) * 60)
        # 估算ITRA分数（考虑山地等级）
        speed = 60 / pace_min
        # 考虑山地等级差异
        difficulty_factor = (twenty_seven_k_mountain_level / forty_two_k_mountain_level) ** 0.5
        score_estimate = 510 * (speed / (42.0 / 7.0)) ** 0.7 * (27/42) ** 0.3 * difficulty_factor
        print(f"{pace_min}:00       | {hours_pace}h{minutes_pace}m | {round(score_estimate, 2)}")
