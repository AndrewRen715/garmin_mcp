"""Script to create a marathon training plan and add it to Garmin"""
import json
import os
import sys
import argparse
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

# Default configuration values
DEFAULT_MARATHON_DATE = '2026-10-01'
DEFAULT_MARATHON_TIME = '3:30:00'
DEFAULT_TRAINING_DURATION = 12

# Set environment variables if not already set
os.environ.setdefault('GARMIN_CN', 'true')

# Parse command line arguments
parser = argparse.ArgumentParser(description='Create a marathon training plan')
parser.add_argument('--target-date', type=str, default=DEFAULT_MARATHON_DATE,
                    help='Target marathon date (YYYY-MM-DD format)')
parser.add_argument('--target-time', type=str, default=DEFAULT_MARATHON_TIME,
                    help='Target finish time (HH:MM:SS format)')
parser.add_argument('--duration', type=int, default=DEFAULT_TRAINING_DURATION,
                    help='Training plan duration in weeks')
args = parser.parse_args()

# Validate date format
try:
    datetime.strptime(args.target_date, '%Y-%m-%d')
except ValueError:
    print(f"错误：目标日期格式无效，应为YYYY-MM-DD格式")
    sys.exit(1)

# Validate logical correctness
TARGET_DATE = datetime.strptime(args.target_date, '%Y-%m-%d')

# 1. Target date should not be in the past
if TARGET_DATE.date() < datetime.now().date():
    print("错误：目标日期不能早于当前日期")
    sys.exit(1)

# 2. Training duration should be reasonable (4-20 weeks)
if not (4 <= args.duration <= 20):
    print("错误：训练时长应在4-20周之间")
    sys.exit(1)

# 3. Target time validation (format and range)
try:
    # Validate time format
    datetime.strptime(args.target_time, '%H:%M:%S')
    
    # Validate time range (2-6 hours)
    hours, minutes, seconds = map(int, args.target_time.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    if not (7200 <= total_seconds <= 21600):  # 2-6 hours
        print("错误：目标时间应在2-6小时之间")
        sys.exit(1)
    
    # Calculate target pace per km
    pace_seconds_per_km = total_seconds / 42.195
    TARGET_PACE = f'{int(pace_seconds_per_km//60)}:{int(pace_seconds_per_km%60):02d}/公里'
except ValueError:
    print("错误：目标时间格式无效，应为HH:MM:SS格式")
    sys.exit(1)

# Initialize Garmin API with empty credentials (will use saved tokens)
print("Initializing Garmin API...")
is_cn = os.getenv('GARMIN_CN', 'true').lower() == 'true'
garmin_client = init_api(None, None, is_cn=is_cn)

if not garmin_client:
    print("Error: Failed to initialize Garmin API.")
    sys.exit(1)

# Define training plan parameters
START_DATE = datetime.now()  # Start from today
PLAN_DURATION = args.duration  # Training plan duration in weeks
TARGET_TIME = args.target_time  # Target finish time

print(f"Creating marathon training plan for {TARGET_DATE.strftime('%Y-%m-%d')}")
print(f"Target finish time: {TARGET_TIME}")
print(f"Plan duration: {PLAN_DURATION} weeks")
print()

# Calculate training plan dates
training_days = []
current_date = START_DATE
while current_date < TARGET_DATE:
    # Skip Sundays for long runs (will be scheduled separately)
    if current_date.weekday() != 6:
        training_days.append(current_date)
    current_date += timedelta(days=1)

# Define training plan structure
training_plan = {
    "target_race": "梦想小镇马拉松",
    "target_date": TARGET_DATE.strftime('%Y-%m-%d'),
    "target_time": TARGET_TIME,
    "start_date": START_DATE.strftime('%Y-%m-%d'),
    "end_date": (TARGET_DATE - timedelta(days=3)).strftime('%Y-%m-%d'),  # Taper before race
    "workouts": []
}

# Define workout types and their frequencies
workout_types = {
    "easy_run": {
        "frequency": 2,  # Twice a week
        "duration": "30-45分钟",
        "pace": "轻松跑，心率在有氧区间",
        "description": "恢复性轻松跑，保持心率在Z1-Z2区间"
    },
    "tempo_run": {
        "frequency": 1,  # Once a week
        "duration": "20-30分钟",
        "pace": "tempo pace，比目标马拉松配速快5-10秒/公里",
        "description": "乳酸阈值训练，提升持续配速能力"
    },
    "interval_training": {
        "frequency": 1,  # Once a week
        "duration": "20-30分钟",
        "pace": "间歇跑，高强度",
        "description": "短距离高强度间歇，提升最大摄氧量"
    },
    "long_run": {
        "frequency": 1,  # Once a week (Sundays)
        "duration": "逐渐增加",
        "pace": "长距离跑，比目标马拉松配速慢10-20秒/公里",
        "description": "耐力训练，逐渐增加距离"
    },
    "cross_training": {
        "frequency": 1,  # Once a week
        "duration": "30-45分钟",
        "pace": "游泳、骑行或力量训练",
        "description": "交叉训练，避免过度使用损伤"
    },
    "rest": {
        "frequency": 1,  # Once a week
        "duration": "0分钟",
        "pace": "完全休息",
        "description": "充分休息，促进恢复"
    }
}

# Generate long runs (Sundays)
long_run_dates = []
current_date = START_DATE
while current_date < TARGET_DATE:
    if current_date.weekday() == 6:  # Sunday
        long_run_dates.append(current_date)
    current_date += timedelta(days=1)

# Create long run workouts
long_run_distances = [10, 12, 15, 18, 20, 22, 16, 10]  # Gradually increase, then taper
for i, date in enumerate(long_run_dates[:len(long_run_distances)]):
    distance = long_run_distances[i]
    workout = {
        "date": date.strftime('%Y-%m-%d'),
        "day_of_week": date.strftime('%A'),
        "type": "long_run",
        "distance": distance,
        "duration": f"{distance * 6:.0f}-{distance * 7:.0f}分钟",  # Estimate based on pace
        "pace": "比目标马拉松配速慢10-20秒/公里",
        "description": f"长距离跑 {distance}公里，保持稳定配速"
    }
    training_plan["workouts"].append(workout)

# Create other workouts
workout_schedule = ["easy_run", "tempo_run", "easy_run", "interval_training", "cross_training", "rest"]
current_workout = 0

for date in training_days:
    # Skip if this date is already a long run
    if date.weekday() == 6:
        continue
    
    # Skip if we're within 3 days of the race (taper)
    if (TARGET_DATE - date).days < 3:
        continue
    
    workout_type = workout_schedule[current_workout % len(workout_schedule)]
    current_workout += 1
    
    # Calculate distance based on workout type
    if workout_type == "easy_run":
        distance = 6
    elif workout_type == "tempo_run":
        distance = 8
    elif workout_type == "interval_training":
        distance = 6
    elif workout_type == "cross_training":
        distance = 0
    else:  # rest
        distance = 0
    
    workout = {
        "date": date.strftime('%Y-%m-%d'),
        "day_of_week": date.strftime('%A'),
        "type": workout_type,
        "distance": distance,
        "duration": workout_types[workout_type]["duration"],
        "pace": workout_types[workout_type]["pace"],
        "description": f"{workout_type.replace('_', ' ').title()}: {workout_types[workout_type]['description']}"
    }
    training_plan["workouts"].append(workout)

# Add race day
race_workout = {
    "date": TARGET_DATE.strftime('%Y-%m-%d'),
    "day_of_week": TARGET_DATE.strftime('%A'),
    "type": "race",
    "distance": 42.195,
    "duration": TARGET_TIME,
    "pace": f"目标配速：{TARGET_PACE}",
    "description": "梦想小镇马拉松比赛日"
}
training_plan["workouts"].append(race_workout)

# Sort workouts by date
training_plan["workouts"].sort(key=lambda x: x["date"])

# Print training plan
print("=" * 80)
print("MARATHON TRAINING PLAN")
print("=" * 80)
print(f"Target Race: {training_plan['target_race']}")
print(f"Target Date: {training_plan['target_date']}")
print(f"Target Time: {training_plan['target_time']}")
print(f"Plan Duration: {training_plan['start_date']} to {training_plan['end_date']}")
print()
print("WORKOUT SCHEDULE:")
print("-" * 80)

for workout in training_plan["workouts"]:
    print(f"{workout['date']} ({workout['day_of_week']}):")
    print(f"  Type: {workout['type'].replace('_', ' ').title()}")
    if workout['distance'] > 0:
        print(f"  Distance: {workout['distance']} km")
    print(f"  Duration: {workout['duration']}")
    print(f"  Pace: {workout['pace']}")
    print(f"  Description: {workout['description']}")
    print()

# Save training plan to JSON file
with open('marathon_training_plan.json', 'w', encoding='utf-8') as f:
    json.dump(training_plan, f, indent=2, ensure_ascii=False)

print("Training plan saved to marathon_training_plan.json")
print("=" * 80)

# Now try to add workouts to Garmin
print("\nAdding workouts to Garmin...")
try:
    # Check if we're connected by getting user profile
    user_profile = garmin_client.get_user_profile()
    print(f"Connected to Garmin as {user_profile['displayName']}")
    
    # For now, we'll create a simple workout and try to add it
    # Note: The garminconnect library may not support workout creation directly
    # This is a placeholder for future implementation
    
    print("\nChecking if workout creation is supported...")
    
    # Check if the Garmin client has workout-related methods
    workout_methods = [method for method in dir(garmin_client) if 'workout' in method.lower()]
    print(f"Available workout-related methods: {workout_methods}")
    
    # For demonstration purposes, we'll just show how many workouts we'd add
    workouts_to_add = [w for w in training_plan['workouts'] if w['type'] != 'rest' and w['type'] != 'race']
    print(f"\nWould add {len(workouts_to_add)} workouts to Garmin.")
    
    print("\nTraining plan creation complete!")
    print("\nTo add these workouts to your Garmin device:")
    print("1. Open Garmin Connect on your computer or mobile device")
    print("2. Navigate to Training > Workouts")
    print("3. Click 'Create Workout' and manually add each workout from the generated plan")
    print("4. Sync your Garmin device to download the workouts")
    print("\nAlternatively, you can use Garmin Connect's Calendar feature to schedule your training sessions.")
    
except Exception as e:
    print(f"Error adding workouts to Garmin: {str(e)}")
    print("The training plan has been created and saved, but could not be added to Garmin automatically.")
    print("\nTo add these workouts to your Garmin device:")
    print("1. Open Garmin Connect on your computer or mobile device")
    print("2. Navigate to Training > Workouts")
    print("3. Click 'Create Workout' and manually add each workout from the generated plan")
    print("4. Sync your Garmin device to download the workouts")
    print("\nAlternatively, you can use Garmin Connect's Calendar feature to schedule your training sessions.")

