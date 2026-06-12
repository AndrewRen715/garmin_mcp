#!/usr/bin/env python3
import sys
import os
import argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from garmin_mcp import init_api
import json

def main():
    parser = argparse.ArgumentParser(description='获取Garmin活动的每公里分段数据')
    parser.add_argument('--activity-id', '-a', type=int, default=585822791, help='Garmin活动ID')
    args = parser.parse_args()
    
    print('初始化Garmin客户端...')
    garmin_client = init_api(None, None, is_cn=True)
    
    activity_id = args.activity_id

    print(f'获取活动 {activity_id} 的每公里分段数据...')

    if hasattr(garmin_client, 'garth'):
        endpoint = f'activity-service/activity/{activity_id}/laps'
        try:
            response = garmin_client.garth.get('connectapi', endpoint)

            if response.status_code == 200:
                data = response.json()
                print('获取数据成功')

                if 'lapDTOs' in data:
                    laps = data['lapDTOs']
                    print(f'找到 {len(laps)} 个分段')

                    km_splits = []
                    for i, lap in enumerate(laps):
                        distance = lap.get('distance', 0) / 1000
                        if 0.9 <= distance <= 1.1:
                            km_splits.append({
                                'km': i+1,
                                'distance': round(distance, 2),
                                'time_sec': int(lap.get('duration', 0)),
                                'time_min': round(lap.get('duration', 0) / 60, 2),
                                'pace': round((lap.get('duration', 0) / 60) / distance, 2) if distance > 0 else 0,
                                'avg_hr': lap.get('averageHR', 0),
                                'max_hr': lap.get('maxHR', 0),
                                'elevation_gain': lap.get('elevationGain', 0),
                                'elevation_loss': lap.get('elevationLoss', 0)
                            })

                    if km_splits:
                        print(f'识别到 {len(km_splits)} 个每公里分段')
                        print()
                        print('公里 | 距离(km) | 时间     | 配速      | 心率   | 爬升')
                        print('-' * 75)

                        for split in km_splits:
                            mins = split['time_sec'] // 60
                            secs = split['time_sec'] % 60
                            pace_mins = int(split['pace'])
                            pace_secs = int((split['pace'] - pace_mins) * 60)
                            print(f"{split['km']:3d}  | {split['distance']:9.2f} | {mins}:{secs:02d}     | {pace_mins}:{pace_secs:02d}     | {split['avg_hr']:5.0f}  | {split['elevation_gain']:6.0f}")

                        with open('huanglong_27k_splits.json', 'w', encoding='utf-8') as f:
                            json.dump({'activity_id': activity_id, 'km_splits': km_splits}, f, indent=2, ensure_ascii=False)

                        print()
                        print('数据已保存到 huanglong_27k_splits.json')
                    else:
                        print('未找到每公里分段')
            else:
                print(f'获取失败: 状态码 {response.status_code}')
        except Exception as e:
            print(f'错误: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    main()