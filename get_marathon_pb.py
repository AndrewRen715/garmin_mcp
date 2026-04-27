"""Script to get the best marathon and half marathon times in the last 6 months"""
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

# Calculate date range (last 6 months)
today = datetime.now()
end_date = today
start_date = today - timedelta(days=180)  # 6 months

print(f"\nGetting activities from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

# Get activities with pagination
try:
    activities = []
    start = 0
    limit = 20
    max_retries = 3
    retry_count = 0
    
    print("\nRetrieving activities...")
    
    while True:
        try:
            page = garmin_client.get_activities(start, limit)
            if not page:
                break
            activities.extend(page)
            start += limit
            if len(page) < limit:
                break
            retry_count = 0  # Reset retry count after successful request
        except Exception as e:
            retry_count += 1
            if retry_count > max_retries:
                print(f"✗ Error retrieving activities data after {max_retries} retries: {str(e)}")
                break
            print(f"⚠️  Network error, retrying ({retry_count}/{max_retries})...")
            import time
            time.sleep(2)  # Wait 2 seconds before retrying
    
    print(f"✓ Successfully retrieved {len(activities)} activities")
    
    # Filter activities by date range
    filtered_activities = []
    for activity in activities:
        start_time = activity.get('startTimeLocal', '')
        if start_time:
            activity_date = start_time.split(' ')[0]
            activity_datetime = datetime.strptime(activity_date, '%Y-%m-%d')
            if start_date <= activity_datetime <= end_date:
                filtered_activities.append(activity)
    
    print(f"✓ Filtered to {len(filtered_activities)} activities within the date range")
    
    # Filter for marathon and half marathon activities
    marathon_activities = []
    half_marathon_activities = []
    
    for activity in filtered_activities:
        activity_type = activity.get('activityType', {})
        if isinstance(activity_type, dict):
            type_key = activity_type.get('typeKey', '').lower()
        else:
            type_key = str(activity_type).lower()
        
        # Check if it's a marathon or half marathon
        # Also check by distance
        distance = activity.get('distance', 0) / 1000  # Convert to km
        
        # Marathon: ~42.195 km
        if 'marathon' in type_key or (distance >= 40 and distance <= 45):
            marathon_activities.append(activity)
        # Half marathon: ~21.0975 km
        elif 'half' in type_key and 'marathon' in type_key or (distance >= 20 and distance <= 22):
            half_marathon_activities.append(activity)
    
    print(f"✓ Found {len(marathon_activities)} marathon activities")
    print(f"✓ Found {len(half_marathon_activities)} half marathon activities")
    
    # Function to get activity details
    def get_activity_details(activity_id):
        try:
            return garmin_client.get_activity_details(activity_id)
        except Exception as e:
            print(f"✗ Error getting details for activity {activity_id}: {str(e)}")
            return None
    
    # Get best marathon time
    best_marathon = None
    best_marathon_time = float('inf')
    
    print("\nAnalyzing marathon activities...")
    for i, activity in enumerate(marathon_activities):
        print(f"Processing marathon activity {i+1}/{len(marathon_activities)}")
        activity_id = activity.get('activityId')
        print(f"Activity ID: {activity_id}")
        print(f"Activity name: {activity.get('activityName', 'Unnamed')}")
        print(f"Distance: {activity.get('distance', 0) / 1000:.2f} km")
        print(f"Duration: {activity.get('duration', 0)} seconds")
        
        # Try to use the duration from the summary first
        duration = activity.get('duration', 0)
        if duration > 0 and duration < best_marathon_time:
            best_marathon_time = duration
            best_marathon = activity
            print(f"Updated best marathon: {best_marathon.get('activityName', 'Unnamed')} with time {duration} seconds")
        
        # Then try to get detailed information
        if activity_id:
            details = get_activity_details(activity_id)
            if details:
                detailed_duration = details.get('duration', 0)
                if detailed_duration > 0 and detailed_duration < best_marathon_time:
                    best_marathon_time = detailed_duration
                    best_marathon = details
                    print(f"Updated best marathon with detailed info: {best_marathon.get('activityName', 'Unnamed')} with time {detailed_duration} seconds")
    
    # Get best half marathon time
    best_half_marathon = None
    best_half_marathon_time = float('inf')
    
    print("\nAnalyzing half marathon activities...")
    for i, activity in enumerate(half_marathon_activities):
        print(f"Processing half marathon activity {i+1}/{len(half_marathon_activities)}")
        activity_id = activity.get('activityId')
        print(f"Activity ID: {activity_id}")
        print(f"Activity name: {activity.get('activityName', 'Unnamed')}")
        print(f"Distance: {activity.get('distance', 0) / 1000:.2f} km")
        print(f"Duration: {activity.get('duration', 0)} seconds")
        
        # Try to use the duration from the summary first
        duration = activity.get('duration', 0)
        if duration > 0 and duration < best_half_marathon_time:
            best_half_marathon_time = duration
            best_half_marathon = activity
            print(f"Updated best half marathon: {best_half_marathon.get('activityName', 'Unnamed')} with time {duration} seconds")
        
        # Then try to get detailed information
        if activity_id:
            details = get_activity_details(activity_id)
            if details:
                detailed_duration = details.get('duration', 0)
                if detailed_duration > 0 and detailed_duration < best_half_marathon_time:
                    best_half_marathon_time = detailed_duration
                    best_half_marathon = details
                    print(f"Updated best half marathon with detailed info: {best_half_marathon.get('activityName', 'Unnamed')} with time {detailed_duration} seconds")
    
    # Function to format time from seconds
    def format_time(seconds):
        # Convert to integer to avoid formatting issues
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours}:{minutes:02d}:{secs:02d}"
    
    # Print results
    print("\n" + "=" * 80)
    print("BEST MARATHON AND HALF MARATHON TIMES")
    print("=" * 80)
    
    if best_marathon:
        print("\nBEST MARATHON:")
        print("-" * 80)
        print(f"Activity Name: {best_marathon.get('activityName', 'Unnamed')}")
        print(f"Date: {best_marathon.get('startTimeLocal', 'Unknown')}")
        print(f"Distance: {best_marathon.get('distance', 0) / 1000:.2f} km")
        print(f"Time: {format_time(best_marathon.get('duration', 0))}")
        print(f"Pace: {format_time(best_marathon.get('duration', 0) / (best_marathon.get('distance', 1) / 1000))} per km")
        print(f"Average Heart Rate: {best_marathon.get('averageHR', 'Unknown')} BPM")
    else:
        print("\nNo marathon activities found in the last 6 months.")
    
    if best_half_marathon:
        print("\nBEST HALF MARATHON:")
        print("-" * 80)
        print(f"Activity Name: {best_half_marathon.get('activityName', 'Unnamed')}")
        print(f"Date: {best_half_marathon.get('startTimeLocal', 'Unknown')}")
        print(f"Distance: {best_half_marathon.get('distance', 0) / 1000:.2f} km")
        print(f"Time: {format_time(best_half_marathon.get('duration', 0))}")
        print(f"Pace: {format_time(best_half_marathon.get('duration', 0) / (best_half_marathon.get('distance', 1) / 1000))} per km")
        print(f"Average Heart Rate: {best_half_marathon.get('averageHR', 'Unknown')} BPM")
    else:
        print("\nNo half marathon activities found in the last 6 months.")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    
    # Save results to file
    results = {
        'date_range': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'best_marathon': {
            'name': best_marathon.get('activityName', 'Unnamed') if best_marathon else None,
            'date': best_marathon.get('startTimeLocal', 'Unknown') if best_marathon else None,
            'distance': best_marathon.get('distance', 0) / 1000 if best_marathon else 0,
            'time': best_marathon.get('duration', 0) if best_marathon else 0,
            'formatted_time': format_time(best_marathon.get('duration', 0)) if best_marathon else None,
            'average_hr': best_marathon.get('averageHR', 'Unknown') if best_marathon else None
        } if best_marathon else None,
        'best_half_marathon': {
            'name': best_half_marathon.get('activityName', 'Unnamed') if best_half_marathon else None,
            'date': best_half_marathon.get('startTimeLocal', 'Unknown') if best_half_marathon else None,
            'distance': best_half_marathon.get('distance', 0) / 1000 if best_half_marathon else 0,
            'time': best_half_marathon.get('duration', 0) if best_half_marathon else 0,
            'formatted_time': format_time(best_half_marathon.get('duration', 0)) if best_half_marathon else None,
            'average_hr': best_half_marathon.get('averageHR', 'Unknown') if best_half_marathon else None
        } if best_half_marathon else None
    }
    
    with open('marathon_pbs.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print("\nResults saved to marathon_pbs.json")
    
except Exception as e:
    print(f"Error getting marathon data: {str(e)}")
    import traceback
    traceback.print_exc()
