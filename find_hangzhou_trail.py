#!/usr/bin/env python3
"""
Find Hangzhou trail running activity (标毅线) by distance and elevation gain
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def find_hangzhou_trail_activity():
    """Find Hangzhou trail running activity with specific criteria"""
    print("Searching for Hangzhou trail running activity (标毅线)...")
    
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
    
    # Define search criteria
    min_distance = 24.0  # km
    max_distance = 30.0  # km
    min_elevation = 1600  # meters
    max_elevation = 2000  # meters
    location_keyword = "杭州"
    activity_types = ["running", "trail_running"]  # Include both types
    
    print(f"\nSearch criteria:")
    print(f"  Distance: {min_distance}-{max_distance} km")
    print(f"  Elevation gain: {min_elevation}-{max_elevation} meters")
    print(f"  Location: containing '{location_keyword}'")
    print(f"  Activity types: {', '.join(activity_types)}")
    print(f"  Year: 2024")
    
    # Get activities in batches
    print("\nGetting activities in batches...")
    
    try:
        # Get activities in batches
        all_activities = []
        batch_size = 100
        start_index = 0
        max_activities = 500
        
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
        
        # Filter activities by criteria
        filtered_activities = []
        
        for activity in all_activities:
            # Check activity type
            activity_type = activity.get('activityType', {}).get('typeKey')
            if activity_type not in activity_types:
                continue
            
            # Check year (2024)
            start_time = activity.get('startTimeLocal')
            if start_time:
                try:
                    activity_date = datetime.fromisoformat(start_time.replace(' ', 'T'))
                    if activity_date.year != 2024:
                        continue
                except:
                    continue
            else:
                continue
            
            # Check distance
            distance = activity.get('distance', 0) / 1000  # convert to km
            if not (min_distance <= distance <= max_distance):
                continue
            
            # Check elevation gain
            elevation_gain = activity.get('elevationGain', 0)
            if not (min_elevation <= elevation_gain <= max_elevation):
                continue
            
            # Check location
            activity_name = activity.get('activityName', '')
            description = activity.get('description', '')
            location = activity.get('locationName', '')
            
            if location_keyword in activity_name or location_keyword in description or location_keyword in location:
                filtered_activities.append(activity)
        
        print(f"\nFound {len(filtered_activities)} activities matching criteria:")
        
        if filtered_activities:
            for i, activity in enumerate(filtered_activities):
                activity_id = activity.get('activityId')
                activity_name = activity.get('activityName')
                start_time = activity.get('startTimeLocal')
                distance = activity.get('distance', 0) / 1000  # convert to km
                elevation_gain = activity.get('elevationGain', 0)
                duration = activity.get('duration', 0) / 60  # convert to minutes
                location = activity.get('locationName', 'Unknown')
                activity_type = activity.get('activityType', {}).get('typeKey')
                
                print(f"\n{i+1}. Activity ID: {activity_id}")
                print(f"   Name: {activity_name}")
                print(f"   Date: {start_time}")
                print(f"   Distance: {distance:.2f} km")
                print(f"   Elevation gain: {elevation_gain:.0f} meters")
                print(f"   Duration: {duration:.1f} minutes")
                print(f"   Activity type: {activity_type}")
                print(f"   Location: {location}")
                
                # Check if it's specifically 标毅线
                if '标毅' in activity_name:
                    print("   ✅ This is likely the 标毅线 trail run!")
                
                # Get detailed activity data for more information
                try:
                    detailed_activity = garmin_client.get_activity(activity_id)
                    if detailed_activity:
                        # Check for course name or other details
                        course_name = detailed_activity.get('course', {}).get('courseName')
                        if course_name:
                            print(f"   Course: {course_name}")
                        
                        # Check for weather data
                        weather = detailed_activity.get('weatherData', {})
                        if weather:
                            temperature = weather.get('temperature')
                            if temperature:
                                print(f"   Weather: {temperature}°C")
                except Exception as e:
                    print(f"   Error getting detailed activity: {e}")
        else:
            print("No activities found matching the criteria.")
            
            # Try broader search
            print("\nTrying broader search criteria...")
            broader_filtered = []
            
            for activity in all_activities:
                # Check activity type
                activity_type = activity.get('activityType', {}).get('typeKey')
                if activity_type not in activity_types:
                    continue
                
                # Check year (2024)
                start_time = activity.get('startTimeLocal')
                if start_time:
                    try:
                        activity_date = datetime.fromisoformat(start_time.replace(' ', 'T'))
                        if activity_date.year != 2024:
                            continue
                    except:
                        continue
                else:
                    continue
                
                # Broader distance range
                distance = activity.get('distance', 0) / 1000  # convert to km
                if not (20 <= distance <= 35):
                    continue
                
                # Broader elevation range
                elevation_gain = activity.get('elevationGain', 0)
                if not (1500 <= elevation_gain <= 2500):
                    continue
                
                # Check for Hangzhou location or 标毅 keyword
                activity_name = activity.get('activityName', '')
                location = activity.get('locationName', '')
                
                if location_keyword in activity_name or location_keyword in location or '标毅' in activity_name:
                    broader_filtered.append(activity)
            
            print(f"Found {len(broader_filtered)} activities with broader criteria:")
            if broader_filtered:
                for i, activity in enumerate(broader_filtered[:10]):  # Show top 10
                    activity_id = activity.get('activityId')
                    activity_name = activity.get('activityName')
                    start_time = activity.get('startTimeLocal')
                    distance = activity.get('distance', 0) / 1000  # convert to km
                    elevation_gain = activity.get('elevationGain', 0)
                    location = activity.get('locationName', 'Unknown')
                    activity_type = activity.get('activityType', {}).get('typeKey')
                    
                    print(f"\n{i+1}. Activity ID: {activity_id}")
                    print(f"   Name: {activity_name}")
                    print(f"   Date: {start_time}")
                    print(f"   Distance: {distance:.2f} km")
                    print(f"   Elevation gain: {elevation_gain:.0f} meters")
                    print(f"   Activity type: {activity_type}")
                    print(f"   Location: {location}")
                    
                    if '标毅' in activity_name:
                        print("   ✅ Contains '标毅' keyword!")
            else:
                print("No activities found with broader criteria.")
                
                # Show all 2024 trail running activities
                print("\nShowing all 2024 trail running activities:")
                trail_2024 = []
                
                for activity in all_activities:
                    activity_type = activity.get('activityType', {}).get('typeKey')
                    if activity_type not in activity_types:
                        continue
                    
                    start_time = activity.get('startTimeLocal')
                    if start_time:
                        try:
                            activity_date = datetime.fromisoformat(start_time.replace(' ', 'T'))
                            if activity_date.year == 2024:
                                trail_2024.append(activity)
                        except:
                            pass
                
                print(f"Found {len(trail_2024)} trail running activities in 2024:")
                for i, activity in enumerate(trail_2024[:10]):
                    activity_name = activity.get('activityName')
                    start_time = activity.get('startTimeLocal')
                    distance = activity.get('distance', 0) / 1000  # convert to km
                    elevation_gain = activity.get('elevationGain', 0)
                    location = activity.get('locationName', 'Unknown')
                    
                    print(f"   {i+1}. {start_time}: {activity_name} - {distance:.2f} km, {elevation_gain:.0f}m elevation, Location: {location}")
                
    except Exception as e:
        print(f"Error searching activities: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        find_hangzhou_trail_activity()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
