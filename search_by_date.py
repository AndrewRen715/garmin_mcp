#!/usr/bin/env python3
"""
Search for activities by specific date range (around 2024-10-08)
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def search_by_date_range():
    """Search for activities around 2024-10-08"""
    print("Searching for activities around 2024-10-08 (标毅线 trail run)...")
    
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
    
    print(f"\nUsing {region} region for search...")
    
    # Define date range around 2024-10-08 (expanded range)
    target_date = datetime(2024, 10, 8)
    start_date = target_date - timedelta(days=10)
    end_date = target_date + timedelta(days=10)
    
    print(f"\nSearching for activities from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Target time: {target_date.strftime('%Y-%m-%d')} around 12:19")
    
    try:
        # Get activities in batches
        all_activities = []
        batch_size = 100
        start_index = 0
        max_activities = 1000
        
        while len(all_activities) < max_activities:
            print(f"Getting batch {start_index//batch_size + 1} (start={start_index})")
            activities = garmin_client.get_activities(start_index, batch_size)
            
            if not activities:
                break
            
            all_activities.extend(activities)
            start_index += batch_size
            
            if len(all_activities) >= max_activities:
                break
        
        print(f"Found {len(all_activities)} activities in total")
        
        # Filter activities by date range
        date_filtered = []
        
        for activity in all_activities:
            start_time = activity.get('startTimeLocal')
            if start_time:
                try:
                    activity_date = datetime.fromisoformat(start_time.replace(' ', 'T'))
                    if start_date <= activity_date <= end_date:
                        date_filtered.append((activity_date, activity))
                except:
                    pass
        
        # Sort by date
        date_filtered.sort(key=lambda x: x[0])
        
        print(f"\nFound {len(date_filtered)} activities in date range:")
        
        if date_filtered:
            for i, (activity_date, activity) in enumerate(date_filtered):
                activity_id = activity.get('activityId')
                activity_name = activity.get('activityName')
                start_time = activity.get('startTimeLocal')
                distance = activity.get('distance', 0) / 1000  # convert to km
                elevation_gain = activity.get('elevationGain', 0)
                duration = activity.get('duration', 0) / 60  # convert to minutes
                activity_type = activity.get('activityType', {}).get('typeKey')
                location = activity.get('locationName', 'Unknown')
                
                print(f"\n{i+1}. Activity ID: {activity_id}")
                print(f"   Name: {activity_name}")
                print(f"   Date: {start_time}")
                print(f"   Distance: {distance:.2f} km")
                print(f"   Elevation gain: {elevation_gain:.0f} meters")
                print(f"   Duration: {duration:.1f} minutes")
                print(f"   Activity type: {activity_type}")
                print(f"   Location: {location}")
                
                # Check for 标毅线 criteria
                is_biaoyi_candidate = False
                if (distance >= 20 and elevation_gain >= 1500) or '标毅' in activity_name:
                    is_biaoyi_candidate = True
                    print("   ⚠ Potential 标毅线 candidate!")
                
                # Check if it's close to the target time
                time_diff = abs(activity_date - target_date)
                if time_diff.total_seconds() < 3600:  # Within 1 hour
                    print(f"   ✅ Close to target time (difference: {time_diff})")
        else:
            print("No activities found in the specified date range.")
            
            # Show all 2024 activities for October
            print("\nShowing all 2024 October activities:")
            oct_2024 = []
            
            for activity in all_activities:
                start_time = activity.get('startTimeLocal')
                if start_time:
                    try:
                        activity_date = datetime.fromisoformat(start_time.replace(' ', 'T'))
                        if activity_date.year == 2024 and activity_date.month == 10:
                            oct_2024.append((activity_date, activity))
                    except:
                        pass
            
            oct_2024.sort(key=lambda x: x[0])
            print(f"Found {len(oct_2024)} activities in October 2024:")
            
            for i, (activity_date, activity) in enumerate(oct_2024[:15]):  # Show first 15
                activity_name = activity.get('activityName')
                start_time = activity.get('startTimeLocal')
                distance = activity.get('distance', 0) / 1000  # convert to km
                elevation_gain = activity.get('elevationGain', 0)
                activity_type = activity.get('activityType', {}).get('typeKey')
                location = activity.get('locationName', 'Unknown')
                
                print(f"   {i+1}. {start_time}: {activity_name} - {distance:.2f} km, {elevation_gain:.0f}m, {activity_type}, {location}")
                
                if '标毅' in activity_name:
                    print("   ✅ Contains '标毅' keyword!")
                
    except Exception as e:
        print(f"Error searching activities: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        search_by_date_range()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
