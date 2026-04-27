#!/usr/bin/env python3
"""
Check specific activity details by ID
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def check_specific_activity(activity_id):
    """Check specific activity details"""
    print(f"Checking activity details for ID: {activity_id}")
    
    # Initialize Garmin client using tokens
    print("Initializing Garmin Connect client...")
    try:
        # Try China region first
        garmin_cn = Garmin(is_cn=True)
        garmin_cn.login("~/.garminconnect_cn")
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
    
    print(f"\nUsing {region} region for activity lookup...")
    
    try:
        # Get activity details
        print(f"\nFetching activity details for ID: {activity_id}...")
        activity_details = garmin_client.get_activity(activity_id)
        
        if activity_details:
            print("\n" + "=" * 60)
            print("ACTIVITY DETAILS")
            print("=" * 60)
            
            # Extract key details
            activity_name = activity_details.get('activityName', 'Unknown')
            start_time = activity_details.get('startTimeLocal', 'Unknown')
            distance = activity_details.get('distance', 0) / 1000  # convert to km
            elevation_gain = activity_details.get('elevationGain', 0)
            duration = activity_details.get('duration', 0) / 60  # convert to minutes
            activity_type = activity_details.get('activityType', {}).get('typeKey', 'Unknown')
            location = activity_details.get('locationName', 'Unknown')
            
            # Calculate elevation per km
            elevation_per_km = elevation_gain / distance if distance > 0 else 0
            
            # Check if this matches 标毅线 criteria
            is_biaoyi_candidate = False
            if ('杭州' in location or 'Hangzhou' in location) and \
               distance >= 24 and elevation_gain >= 1800:
                is_biaoyi_candidate = True
            
            # Display details
            print(f"Activity ID: {activity_id}")
            print(f"Name: {activity_name}")
            print(f"Date: {start_time}")
            print(f"Distance: {distance:.2f} km")
            print(f"Elevation gain: {elevation_gain:.0f} meters")
            print(f"Elevation per km: {elevation_per_km:.1f} m/km")
            print(f"Duration: {duration:.1f} minutes")
            print(f"Activity type: {activity_type}")
            print(f"Location: {location}")
            
            if is_biaoyi_candidate:
                print("\n✅ This activity matches 标毅线 criteria!")
                print("   - Location: Hangzhou")
                print("   - Distance: 24+ km")
                print("   - Elevation gain: 1800+ meters")
            else:
                print("\n⚠ This activity does not match 标毅线 criteria")
                
            # Additional details
            print("\n" + "=" * 60)
            print("ADDITIONAL DETAILS")
            print("=" * 60)
            print(f"Activity type: {activity_details.get('activityType', {}).get('typeKey', 'Unknown')}")
            print(f"Calories: {activity_details.get('calories', 'Unknown')}")
            print(f"Average heart rate: {activity_details.get('averageHR', 'Unknown')} bpm")
            print(f"Max heart rate: {activity_details.get('maxHR', 'Unknown')} bpm")
            print(f"Average pace: {activity_details.get('averagePace', 'Unknown')} min/km")
            print(f"Average speed: {activity_details.get('averageSpeed', 'Unknown')} m/s")
            print(f"Weather conditions: {activity_details.get('weatherConditions', 'Unknown')}")
            
            # Check if it's from 2024
            if start_time:
                try:
                    activity_date = datetime.fromisoformat(start_time.replace(' ', 'T'))
                    if activity_date.year == 2024:
                        print("\n✅ This activity is from 2024!")
                    else:
                        print(f"\n⚠ This activity is from {activity_date.year}, not 2024")
                except:
                    pass
        else:
            print("\n✗ Failed to get activity details")
            
    except Exception as e:
        print(f"Error fetching activity details: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        # Activity ID from the URL
        activity_id = "420601500"
        check_specific_activity(activity_id)
        
        # Also check if there are other activities with similar IDs
        print("\n" + "=" * 60)
        print("CHECKING SIMILAR ACTIVITY IDS")
        print("=" * 60)
        
        # Try to get activities around this ID range
        # First, let's get more activities to find this specific one
        print("\nGetting more activities to find the specific activity...")
        
        # Try China region first
        garmin_cn = Garmin(is_cn=True)
        garmin_cn.login("~/.garminconnect_cn")
        
        # Get activities in larger batches
        all_activities = []
        batch_size = 100
        start_index = 0
        max_activities = 1000  # Get more activities
        
        while len(all_activities) < max_activities:
            print(f"Getting extended batch {start_index//batch_size + 1} (start={start_index})")
            activities = garmin_cn.get_activities(start_index, batch_size)
            
            if not activities:
                break
            
            all_activities.extend(activities)
            start_index += batch_size
            
            # Check if we found the activity
            for activity in activities:
                if activity.get('activityId') == activity_id:
                    print(f"\n✅ Found activity ID {activity_id} in batch {start_index//batch_size}!")
                    activity_name = activity.get('activityName')
                    start_time = activity.get('startTimeLocal')
                    distance = activity.get('distance', 0) / 1000
                    elevation_gain = activity.get('elevationGain', 0)
                    print(f"Activity: {activity_name}")
                    print(f"Date: {start_time}")
                    print(f"Distance: {distance:.2f} km")
                    print(f"Elevation: {elevation_gain:.0f} m")
                    break
            
            if len(all_activities) >= max_activities:
                break
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
