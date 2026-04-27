#!/usr/bin/env python3
"""
获取最近的活动记录
"""
import json

# 创建一个模拟的客户端来演示
class MockGarminClient:
    """模拟Garmin客户端，用于演示获取活动记录"""
    
    def get_activities(self, start=0, limit=20):
        """模拟获取活动记录"""
        # 模拟最近的活动数据
        mock_activities = [
            {
                "activityId": 1234567890,
                "activityName": "杭州市 - 轻松跑3K热身",
                "activityType": {"typeKey": "running"},
                "startTimeLocal": "2026-02-10T08:00:00.000Z",
                "distance": 8300,
                "duration": 3246,
                "movingDuration": 3000,
                "calories": 400,
                "averageHR": 143,
                "maxHR": 155,
                "steps": 10000,
                "ownerDisplayName": "User"
            },
            {
                "activityId": 1234567891,
                "activityName": "杭州市 - 轻松跑3K热身",
                "activityType": {"typeKey": "running"},
                "startTimeLocal": "2026-02-11T08:30:00.000Z",
                "distance": 6400,
                "duration": 2208,
                "movingDuration": 2000,
                "calories": 300,
                "averageHR": 138,
                "maxHR": 150,
                "steps": 8000,
                "ownerDisplayName": "User"
            },
            {
                "activityId": 1234567892,
                "activityName": "杭州市 跑步",
                "activityType": {"typeKey": "running"},
                "startTimeLocal": "2026-02-12T09:00:00.000Z",
                "distance": 3000,
                "duration": 1080,
                "movingDuration": 900,
                "calories": 150,
                "averageHR": 135,
                "maxHR": 145,
                "steps": 3500,
                "ownerDisplayName": "User"
            },
            {
                "activityId": 1234567893,
                "activityName": "杭州市 操场跑步",
                "activityType": {"typeKey": "running"},
                "startTimeLocal": "2026-02-12T09:30:00.000Z",
                "distance": 13000,
                "duration": 3168,
                "movingDuration": 3000,
                "calories": 600,
                "averageHR": 168,
                "maxHR": 175,
                "steps": 15000,
                "ownerDisplayName": "User"
            }
        ]
        
        return mock_activities

# 测试获取最近的活动记录
def test_get_activities():
    """测试获取最近的活动记录"""
    # 创建模拟客户端
    mock_client = MockGarminClient()
    
    # 获取最近的活动记录
    activities = mock_client.get_activities(0, 10)
    
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
    
    print(json.dumps(curated, indent=2, ensure_ascii=False))

# 运行测试
if __name__ == "__main__":
    test_get_activities()
