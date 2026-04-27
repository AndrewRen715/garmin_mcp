import sys
import os
import json
sys.path.insert(0, 'src')

# Set up Python path and environment variables
os.environ['PYTHONPATH'] = 'src'

from garmin_mcp import init_api
import asyncio

async def main():
    """Get details of the most recent running activity"""
    print("Getting details of the most recent running activity...")
    
    # Initialize API with saved tokens
    garmin_client = init_api(None, None, True)  # is_cn=True for China region
    
    if not garmin_client:
        print("Failed to initialize Garmin client")
        return
    
    print("Garmin client initialized successfully")
    
    # Get recent activities
    try:
        print("\nGetting recent activities...")
        activities = garmin_client.get_activities(0, 20)  # Get first 20 activities (newest first)
        
        if not activities:
            print("No activities found")
            return
        
        print(f"Found {len(activities)} recent activities")
        
        # Filter for running activities
        running_activities = [activity for activity in activities if activity.get('activityType', {}).get('typeKey') == 'running']
        
        if not running_activities:
            print("No running activities found")
            return
        
        print(f"Found {len(running_activities)} running activities")
        
        # Get the most recent running activity
        most_recent = running_activities[0]
        activity_id = most_recent.get('activityId')
        activity_name = most_recent.get('activityName')
        start_time = most_recent.get('startTimeLocal')
        
        print(f"\nMost recent running activity:")
        print(f"ID: {activity_id}")
        print(f"Name: {activity_name}")
        print(f"Start time: {start_time}")
        
        # Get detailed activity information
        print("\nGetting detailed activity information...")
        activity_details = garmin_client.get_activity(activity_id)
        
        if not activity_details:
            print("Failed to get activity details")
            return
        
        print("Activity details retrieved successfully")
        
        # Extract summary data
        summary = activity_details.get('summaryDTO', {})
        activity_type = activity_details.get('activityTypeDTO', {})
        
        print("\n" + "=" * 80)
        print("RUNNING ACTIVITY DETAILS")
        print("=" * 80)
        
        # Basic information
        print(f"\nActivity Name: {activity_name}")
        print(f"Activity Type: {activity_type.get('typeKey', 'Unknown')}")
        print(f"Start Time: {start_time}")
        print(f"Activity ID: {activity_id}")
        
        # Distance and duration
        distance = summary.get('distance', 0) / 1000  # Convert to kilometers
        duration = summary.get('duration', 0) / 60  # Convert to minutes
        avg_speed = summary.get('averageSpeed', 0) * 3.6  # Convert to km/h
        
        print(f"\nDistance: {distance:.2f} km")
        print(f"Duration: {duration:.2f} minutes")
        print(f"Average Pace: {duration/distance:.2f} min/km" if distance > 0 else "Average Pace: N/A")
        print(f"Average Speed: {avg_speed:.2f} km/h")
        
        # Heart rate
        avg_hr = summary.get('averageHR', 0)
        max_hr = summary.get('maxHR', 0)
        min_hr = summary.get('minHR', 0)
        
        print(f"\nHeart Rate:")
        print(f"Average: {avg_hr} bpm")
        print(f"Maximum: {max_hr} bpm")
        print(f"Minimum: {min_hr} bpm")
        
        # Calories
        calories = summary.get('calories', 0)
        print(f"\nCalories: {calories} kcal")
        
        # Training effect
        training_effect = summary.get('trainingEffect', 0)
        anaerobic_effect = summary.get('anaerobicTrainingEffect', 0)
        
        print(f"\nTraining Effect:")
        print(f"Overall: {training_effect}")
        print(f"Anaerobic: {anaerobic_effect}")
        
        # Intensity minutes
        moderate_minutes = summary.get('moderateIntensityMinutes', 0)
        vigorous_minutes = summary.get('vigorousIntensityMinutes', 0)
        
        print(f"\nIntensity Minutes:")
        print(f"Moderate: {moderate_minutes} minutes")
        print(f"Vigorous: {vigorous_minutes} minutes")
        print(f"Total: {moderate_minutes + vigorous_minutes} minutes")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"Error getting running activity details: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
