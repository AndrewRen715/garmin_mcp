"""Script to get details of the most recent running activity"""
import json
import os
import sys
from datetime import datetime

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

print("Getting recent activities...")

# Get recent activities
try:
    activities = []
    start = 0
    limit = 20
    
    # Get activities with pagination
    while True:
        page = garmin_client.get_activities(start, limit)
        if not page:
            break
        activities.extend(page)
        start += limit
        if len(page) < limit:
            break
    
    if not activities:
        print("No activities found.")
        sys.exit(1)
    
    # Filter for running activities
    running_activities = []
    for activity in activities:
        activity_type = activity.get('activityType', {})
        if isinstance(activity_type, dict):
            type_key = activity_type.get('typeKey', '').lower()
        else:
            type_key = str(activity_type).lower()
        
        # Check if it's a running activity
        if 'run' in type_key or 'running' in type_key:
            running_activities.append(activity)
    
    if not running_activities:
        print("No running activities found.")
        sys.exit(1)
    
    # Sort by start time (most recent first)
    running_activities.sort(key=lambda x: x.get('startTimeLocal', ''), reverse=True)
    
    # Get the most recent running activity
    last_run = running_activities[0]
    activity_id = last_run.get('activityId')
    
    if not activity_id:
        print("No activity ID found for the most recent run.")
        sys.exit(1)
    
    print(f"\nFound most recent running activity: {last_run.get('activityName', 'Unnamed')}")
    print(f"Date: {last_run.get('startTimeLocal', 'Unknown')}")
    print(f"Activity ID: {activity_id}")
    
    # Get detailed activity data
    print("\nGetting detailed activity data...")
    detailed_activity = garmin_client.get_activity_details(activity_id)
    
    if not detailed_activity:
        print("No detailed activity data available.")
        sys.exit(1)
    
    # Print detailed information
    print("\n" + "=" * 80)
    print("MOST RECENT RUNNING ACTIVITY DETAILS")
    print("=" * 80)
    
    # Basic info
    print(f"Activity Name: {detailed_activity.get('activityName', 'Unnamed')}")
    print(f"Date: {detailed_activity.get('startTimeLocal', 'Unknown')}")
    print(f"Activity Type: {detailed_activity.get('activityType', {}).get('typeKey', 'Unknown')}")
    print()
    
    # Metrics
    print("METRICS")
    print("-" * 80)
    
    # Duration
    duration = detailed_activity.get('duration', 0)
    hours = duration // 3600
    minutes = (duration % 3600) // 60
    seconds = duration % 60
    print(f"Duration: {hours}:{minutes:02d}:{seconds:02d}")
    
    # Distance
    distance = detailed_activity.get('distance', 0) / 1000  # Convert to km
    print(f"Distance: {distance:.2f} km")
    
    # Average pace
    if distance > 0 and duration > 0:
        pace_seconds_per_km = duration / distance
        pace_minutes = int(pace_seconds_per_km // 60)
        pace_seconds = int(pace_seconds_per_km % 60)
        print(f"Average Pace: {pace_minutes}:{pace_seconds:02d} min/km")
    
    # Average speed
    if duration > 0:
        speed = (distance * 1000) / duration * 3.6  # Convert to km/h
        print(f"Average Speed: {speed:.2f} km/h")
    
    # Calories
    print(f"Calories: {detailed_activity.get('calories', 'Unknown')}")
    print()
    
    # Heart rate data
    print("HEART RATE DATA")
    print("-" * 80)
    print(f"Average Heart Rate: {detailed_activity.get('averageHR', 'Unknown')} BPM")
    print(f"Max Heart Rate: {detailed_activity.get('maxHR', 'Unknown')} BPM")
    
    # Heart rate zones
    hr_zones = detailed_activity.get('heartRateZones', [])
    if hr_zones:
        print("\nHeart Rate Zones:")
        for zone in hr_zones:
            zone_num = zone.get('zone', 'N/A')
            min_hr = zone.get('min', 'N/A')
            max_hr = zone.get('max', 'N/A')
            time = zone.get('time', 0) // 60  # Convert to minutes
            print(f"  Zone {zone_num}: {min_hr}-{max_hr} BPM - {time} minutes")
    else:
        print("No heart rate zone data available.")
    print()
    
    # Training load
    print("TRAINING LOAD")
    print("-" * 80)
    training_load = detailed_activity.get('trainingLoad', 'N/A')
    print(f"Training Load: {training_load}")
    
    # Training effect
    training_effect = detailed_activity.get('trainingEffect', 'N/A')
    if training_effect != 'N/A':
        print(f"Training Effect: {training_effect}")
    print()
    
    # Elevation data
    print("ELEVATION DATA")
    print("-" * 80)
    elevation_gain = detailed_activity.get('elevationGain', 'Unknown')
    elevation_loss = detailed_activity.get('elevationLoss', 'Unknown')
    print(f"Elevation Gain: {elevation_gain} m")
    print(f"Elevation Loss: {elevation_loss} m")
    print()
    
    # Weather data (if available)
    print("WEATHER DATA")
    print("-" * 80)
    weather = detailed_activity.get('weather', {})
    if weather:
        print(f"Temperature: {weather.get('temperature', 'Unknown')}°C")
        print(f"Humidity: {weather.get('humidity', 'Unknown')}%")
        print(f"Wind: {weather.get('wind', 'Unknown')}")
    else:
        print("No weather data available.")
    print()
    
    # Course data (if available)
    print("COURSE DATA")
    print("-" * 80)
    course = detailed_activity.get('course', {})
    if course:
        print(f"Course Name: {course.get('courseName', 'Unknown')}")
        print(f"Course Distance: {course.get('courseDistance', 'Unknown')} m")
    else:
        print("No course data available.")
    print()
    
    # Splits data (if available)
    print("SPLITS")
    print("-" * 80)
    splits = detailed_activity.get('splits', [])
    if splits:
        print("Split data available.")
        # Print first few splits as example
        for i, split in enumerate(splits[:5]):
            split_distance = split.get('distance', 0) / 1000  # Convert to km
            split_duration = split.get('duration', 0)
            split_minutes = split_duration // 60
            split_seconds = split_duration % 60
            print(f"Split {i+1}: {split_distance:.2f} km in {split_minutes}:{split_seconds:02d}")
        if len(splits) > 5:
            print(f"... and {len(splits) - 5} more splits")
    else:
        print("No splits data available.")
    print()
    
    # Save detailed data to file
    with open('last_run_details.json', 'w', encoding='utf-8') as f:
        json.dump(detailed_activity, f, indent=2, ensure_ascii=False)
    
    print("Detailed data saved to last_run_details.json")
    print("=" * 80)
    
except Exception as e:
    print(f"Error getting running activity details: {str(e)}")
    import traceback
    traceback.print_exc()
