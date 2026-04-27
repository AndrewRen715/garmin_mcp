#!/usr/bin/env python3
"""
Get training data for the last 6 weeks (2025-12-20 to today) from Garmin Connect
"""

import sys
import datetime
from datetime import timedelta

sys.path.insert(0, 'src')

from garminconnect import Garmin

def get_training_data_6weeks():
    """Get training data for the last 6 weeks from Garmin Connect"""
    print("Getting training data for the last 6 weeks from Garmin Connect...")
    print()
    
    # Define date range
    end_date = datetime.datetime.now().date()
    start_date = datetime.date(2025, 12, 20)
    
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total days: {(end_date - start_date).days + 1}")
    print()
    
    # Initialize Garmin client using tokens
    try:
        # Try China region first
        garmin_cn = Garmin(is_cn=True)
        garmin_cn.login("~/.garminconnect")
        print("✓ China region client initialized (using tokens)")
        garmin_client = garmin_cn
        region = "China"
    except Exception as e:
        print(f"✗ Failed to initialize China region client: {e}")
        try:
            # Fallback to global region
            garmin_global = Garmin(is_cn=False)
            garmin_global.login("~/.garminconnect")
            print("✓ Global region client initialized (using tokens)")
            garmin_client = garmin_global
            region = "Global"
        except Exception as e:
            print(f"✗ Failed to initialize global region client: {e}")
            return
    
    print(f"\nUsing {region} region for data retrieval...")
    print()
    
    # Get activities
    try:
        print("Getting activities...")
        # Get activities with a reasonable limit
        activities = garmin_client.get_activities(limit=100)
        print(f"Found {len(activities)} total activities")
        
        # Filter activities by date range
        filtered_activities = []
        for activity in activities:
            activity_date_str = activity.get('startTimeLocal', '')[:10]
            if activity_date_str:
                activity_date = datetime.datetime.strptime(activity_date_str, '%Y-%m-%d').date()
                if start_date <= activity_date <= end_date:
                    filtered_activities.append(activity)
        
        print(f"Filtered to {len(filtered_activities)} activities in date range")
        print()
        
        if not filtered_activities:
            print("No activities found in the specified date range.")
            return
        
        # Display activities in table format
        print("Training Data (2025-12-20 to today):")
        print("=" * 140)
        print(f"{'Date':<12} {'Type':<15} {'Distance':<10} {'Duration':<10} {'Pace':<10} {'Elevation':<10} {'Calories':<10} {'Avg HR':<8} {'Name':<30}")
        print("=" * 140)
        
        total_distance = 0
        total_duration = 0
        total_calories = 0
        total_elevation = 0
        
        for activity in filtered_activities:
            # Extract activity data
            activity_date = activity.get('startTimeLocal', '')[:10]
            activity_type = activity.get('activityType', {}).get('typeKey', 'Unknown')
            distance = activity.get('distance', 0) / 1000  # convert to km
            duration = activity.get('duration', 0) / 60  # convert to minutes
            calories = activity.get('calories', 0)
            elevation_gain = activity.get('elevationGain', 0)
            
            # Try multiple fields for heart rate data
            avg_hr = activity.get('averageHeartRate', 0)
            if avg_hr == 0:
                avg_hr = activity.get('avgHeartRate', 0)
            if avg_hr == 0:
                # Try getting from summaryDTO if available
                summary = activity.get('summaryDTO', {})
                avg_hr = summary.get('averageHeartRate', 0)
                if avg_hr == 0:
                    avg_hr = summary.get('avgHeartRate', 0)
            
            activity_name = activity.get('activityName', 'Unnamed Activity')[:29]
            
            # Calculate pace (min/km)
            pace = duration / distance if distance > 0 else 0
            pace_str = f"{int(pace//1)}:{int((pace%1)*60):02d}" if pace > 0 else "N/A"
            
            # Format values
            distance_str = f"{distance:.2f} km"
            duration_str = f"{duration:.1f} min"
            calories_str = f"{calories:.0f}"
            elevation_str = f"{elevation_gain:.0f} m"
            hr_str = f"{avg_hr:.0f}" if avg_hr > 0 else "N/A"
            
            # Print row
            print(f"{activity_date:<12} {activity_type:<15} {distance_str:<10} {duration_str:<10} {pace_str:<10} {elevation_str:<10} {calories_str:<10} {hr_str:<8} {activity_name:<30}")
            
            # Accumulate totals
            total_distance += distance
            total_duration += duration
            total_calories += calories
            total_elevation += elevation_gain
        
        print("=" * 140)
        
        # Calculate average pace for running activities
        running_activities = [a for a in filtered_activities if a.get('activityType', {}).get('typeKey', '') in ['running', 'trail_running', 'track_running']]
        running_distance = sum(a.get('distance', 0)/1000 for a in running_activities)
        running_duration = sum(a.get('duration', 0)/60 for a in running_activities)
        avg_running_pace = running_duration / running_distance if running_distance > 0 else 0
        avg_running_pace_str = f"{int(avg_running_pace//1)}:{int((avg_running_pace%1)*60):02d}" if avg_running_pace > 0 else "N/A"
        
        # Print summary
        print("Summary:")
        print(f"Total activities: {len(filtered_activities)}")
        print(f"Total distance: {total_distance:.2f} km")
        print(f"Total duration: {total_duration:.1f} minutes ({total_duration/60:.1f} hours)")
        print(f"Total calories: {total_calories:.0f}")
        print(f"Total elevation gain: {total_elevation:.0f} meters")
        if running_activities:
            print(f"Running activities: {len(running_activities)}")
            print(f"Running distance: {running_distance:.2f} km")
            print(f"Average running pace: {avg_running_pace_str} min/km")
        print()
        
    except Exception as e:
        print(f"Error getting training data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_training_data_6weeks()
