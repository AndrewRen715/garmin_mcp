#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试佳明国内区和国际区连接
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

try:
    from garminconnect import Garmin
    garmin_available = True
except ImportError:
    print("错误: 未安装garminconnect库")
    sys.exit(1)

def test_region(is_cn):
    """测试指定区域的连接"""
    region_name = "中国区" if is_cn else "国际区"
    token_path = "~/.garminconnect_cn" if is_cn else "~/.garminconnect"
    
    print("\n测试 {} (is_cn={})...".format(region_name, is_cn))
    
    try:
        garmin = Garmin(is_cn=is_cn)
        expanded_path = os.path.expanduser(token_path)
        garmin.login(expanded_path)
        print("  ✓ 登录成功")
        
        # 获取用户信息
        user = garmin.get_user_profile()
        if user:
            print("  ✓ 获取用户信息成功")
            print("    用户ID: {}".format(user.get('userId')))
            print("    显示名: {}".format(user.get('displayName')))
        
        # 获取活动
        activities = garmin.get_activities(0, 10)
        if activities:
            print("  ✓ 获取活动成功，共 {} 条活动".format(len(activities)))
            for a in activities[:3]:
                date = a.get('startTimeLocal', '').split(' ')[0]
                print("    - {}: {} ({})".format(date, a.get('activityName'), a.get('activityType', {}).get('typeKey')))
        else:
            print("  ✓ 无活动记录")
        
        return True
        
    except Exception as e:
        print("  ✗ 连接失败: {}".format(e))
        return False

def main():
    print("=" * 60)
    print("Garmin Connect 双区域连接测试")
    print("=" * 60)
    
    print("\n注意: 此测试需要提前保存好两个区域的token")
    print("中国区token路径: ~/.garminconnect_cn")
    print("国际区token路径: ~/.garminconnect")
    
    # 测试中国区
    cn_success = test_region(True)
    
    # 测试国际区
    global_success = test_region(False)
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("中国区: {}".format("成功" if cn_success else "失败"))
    print("国际区: {}".format("成功" if global_success else "失败"))
    print("=" * 60)

if __name__ == "__main__":
    main()