#!/usr/bin/env python3
"""
获取最近的攀岩活动记录
"""
import json
import os
import sys
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

# Set environment variables
os.environ['GARMIN_CN'] = 'true'

# Initialize Garmin API with empty credentials (will use saved tokens)
print("Initializing Garmin API...")
garmin_client = init_api(None, None, is_cn=True)

if not garmin_client:
    print("Error: Failed to initialize Garmin API.")
    sys.exit(1)

# Get activities with pagination
print("Getting recent activities...")
activities = []
start = 0
limit = 50

while True:
    page = garmin_client.get_activities(start, limit)
    if not page:
        break
    activities.extend(page)
    start += limit
    if len(page) < limit:
        break

print(f"Total activities found: {len(activities)}")

# Filter climbing-related activities
climbing_activities = []
for activity in activities:
    activity_type = activity.get('activityType', {}).get('typeKey', '')
    activity_name = activity.get('activityName', '').lower()
    
    # Check if activity is climbing-related
    if activity_type in ['indoor_climbing', 'rock_climbing', 'bouldering'] or \
       '攀岩' in activity_name or '抱石' in activity_name:
        climbing_activities.append(activity)

print(f"Climbing-related activities found: {len(climbing_activities)}")

# Check for activities on 2026-04-11 (last Saturday)
target_date = '2026-04-11'
target_activities = []

print(f"\nChecking activities for {target_date}...")
for activity in climbing_activities:
    start_time = activity.get('startTimeLocal', '')
    if start_time:
        activity_date = start_time.split(' ')[0]
        if activity_date == target_date:
            target_activities.append(activity)

print(f"Activities on {target_date}: {len(target_activities)}")

# Print detailed information for target activities
if target_activities:
    print("\nDetailed information for activities on 2026-04-11:")
    for i, activity in enumerate(target_activities):
        print(f"\nActivity {i+1}:")
        print(f"Name: {activity.get('activityName', 'Unnamed')}")
        print(f"Type: {activity.get('activityType', {}).get('typeKey', 'Unknown')}")
        print(f"Start Time: {activity.get('startTimeLocal', 'N/A')}")
        print(f"Duration: {activity.get('duration', 0) // 60} minutes")
        print(f"Average HR: {activity.get('averageHR', 'N/A')} BPM")
        print(f"Max HR: {activity.get('maxHR', 'N/A')} BPM")
        print(f"Calories: {activity.get('calories', 'N/A')}")
else:
    print("\nNo climbing activities found on 2026-04-11.")

# Print all climbing activities for reference
if climbing_activities:
    print("\nAll climbing-related activities:")
    print("=" * 80)
    for activity in climbing_activities:
        start_time = activity.get('startTimeLocal', '')
        activity_date = start_time.split(' ')[0] if start_time else 'Unknown'
        print(f"Date: {activity_date}")
        print(f"Name: {activity.get('activityName', 'Unnamed')}")
        print(f"Type: {activity.get('activityType', {}).get('typeKey', 'Unknown')}")
        print(f"Duration: {activity.get('duration', 0) // 60} minutes")
        print(f"HR: {activity.get('averageHR', 'N/A')}/{activity.get('maxHR', 'N/A')} BPM")
        print("-" * 80)
