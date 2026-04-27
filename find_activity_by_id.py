#!/usr/bin/env python3
"""
Find specific activity by ID with detailed debugging
"""

import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def find_activity_by_id(target_activity_id):
    """Find specific activity by ID"""
    print(f"Searching for activity ID: {target_activity_id}")
    
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
        return
    
    print(f"\nUsing {region} region for search...")
    
    try:
        # Get activities in batches to find the specific one
        batch_size = 100
        start_index = 0
        max_batches = 20  # Try up to 20 batches (2000 activities)
        found_activity = None
        
        print(f"\nSearching through activities in batches of {batch_size}...")
        
        for batch_num in range(max_batches):
            current_start = start_index + (batch_num * batch_size)
            print(f"Batch {batch_num + 1}: start={current_start}")
            
            try:
                activities = garmin_client.get_activities(current_start, batch_size)
                
                if not activities:
                    print(f"No more activities found at batch {batch_num + 1}")
                    break
                
                print(f"  Found {len(activities)} activities in this batch")
                
                # Check each activity in this batch
                for activity in activities:
                    activity_id = activity.get('activityId')
                    
                    if activity_id == target_activity_id:
                        print(f"\n🎉 FOUND ACTIVITY ID {target_activity_id}!")
                        found_activity = activity
                        
                        # Print all available details
                        print("\n" + "=" * 60)
                        print("ACTIVITY DETAILS")
                        print("=" * 60)
                        
                        # Print all keys in the activity dict
                        print("All available keys:")
                        for key, value in activity.items():
                            if isinstance(value, dict):
                                print(f"  {key}: {type(value)}")
                                # Print nested dict keys
                                for nested_key, nested_value in value.items():
                                    print(f"    {nested_key}: {nested_value}")
                            else:
                                print(f"  {key}: {value}")
                        
                        # Extract and print key details
                        print("\n" + "=" * 60)
                        print("KEY DETAILS")
                        print("=" * 60)
                        
                        activity_name = activity.get('activityName', 'Unknown')
                        start_time = activity.get('startTimeLocal', 'Unknown')
                        distance = activity.get('distance', 0) / 1000  # convert to km
                        elevation_gain = activity.get('elevationGain', 0)
                        duration = activity.get('duration', 0) / 60  # convert to minutes
                        activity_type = activity.get('activityType', {}).get('typeKey', 'Unknown')
                        location = activity.get('locationName', 'Unknown')
                        
                        print(f"Activity ID: {activity_id}")
                        print(f"Name: {activity_name}")
                        print(f"Start Time: {start_time}")
                        print(f"Distance: {distance:.2f} km")
                        print(f"Elevation gain: {elevation_gain:.0f} meters")
                        print(f"Duration: {duration:.1f} minutes")
                        print(f"Activity type: {activity_type}")
                        print(f"Location: {location}")
                        
                        # Check if it's 标毅线
                        if '标毅' in activity_name:
                            print("\n✅ This is the 标毅线 trail run!")
                        
                        # Check if it matches 标毅线 criteria
                        if distance >= 24 and elevation_gain >= 1800 and '杭州' in location:
                            print("\n✅ This matches 标毅线 criteria!")
                        
                        return
                        
            except Exception as e:
                print(f"  Error getting batch {batch_num + 1}: {e}")
                continue
        
        if not found_activity:
            print(f"\n❌ Activity ID {target_activity_id} not found in {max_batches * batch_size} activities")
            
    except Exception as e:
        print(f"Error searching activities: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        # Activity ID from the URL
        target_activity_id = "420601500"
        find_activity_by_id(target_activity_id)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
