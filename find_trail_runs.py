#!/usr/bin/env python3
"""
Find trail running activities sorted by elevation gain
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def find_trail_running_activities():
    """Find trail running activities sorted by elevation gain"""
    print("Searching for trail running activities...")
    
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
    
    # Get activities
    print("\nGetting running activities...")
    
    try:
        # Get recent activities (limit to 100)
        activities = garmin_client.get_activities(0, 100)
        print(f"Found {len(activities)} activities in total")
        
        # Filter for running activities
        running_activities = []
        
        for activity in activities:
            # Check activity type
            activity_type = activity.get('activityType', {}).get('typeKey')
            if activity_type == 'running':
                running_activities.append(activity)
        
        print(f"Filtered to {len(running_activities)} running activities")
        
        # Sort by elevation gain (descending)
        running_activities.sort(key=lambda x: x.get('elevationGain', 0), reverse=True)
        
        # Show top 20 activities by elevation gain
        print(f"\nTop 20 running activities by elevation gain:")
        
        for i, activity in enumerate(running_activities[:20]):
            activity_id = activity.get('activityId')
            activity_name = activity.get('activityName')
            start_time = activity.get('startTimeLocal')
            distance = activity.get('distance', 0) / 1000  # convert to km
            elevation_gain = activity.get('elevationGain', 0)
            duration = activity.get('duration', 0) / 60  # convert to minutes
            location = activity.get('locationName', 'Unknown')
            
            # Calculate elevation per km
            elevation_per_km = elevation_gain / distance if distance > 0 else 0
            
            print(f"\n{i+1}. Activity ID: {activity_id}")
            print(f"   Name: {activity_name}")
            print(f"   Date: {start_time}")
            print(f"   Distance: {distance:.2f} km")
            print(f"   Elevation gain: {elevation_gain:.0f} meters")
            print(f"   Elevation per km: {elevation_per_km:.1f} m/km")
            print(f"   Duration: {duration:.1f} minutes")
            print(f"   Location: {location}")
            
            # Check if this might be the trail run
            if distance >= 20 and elevation_gain >= 1000:
                print(f"   ⚠ Possible trail running activity!")
        
        # Also search for activities with "杭州" or "trail" in name
        print("\n" + "=" * 60)
        print("Activities with location keywords:")
        print("=" * 60)
        
        keyword_activities = []
        keywords = ["杭州", "trail", "越野", "标毅", "Hangzhou"]
        
        for activity in running_activities:
            activity_name = activity.get('activityName', '').lower()
            location = activity.get('locationName', '').lower()
            
            for keyword in keywords:
                if keyword.lower() in activity_name or keyword.lower() in location:
                    keyword_activities.append(activity)
                    break
        
        if keyword_activities:
            for i, activity in enumerate(keyword_activities[:10]):
                activity_id = activity.get('activityId')
                activity_name = activity.get('activityName')
                start_time = activity.get('startTimeLocal')
                distance = activity.get('distance', 0) / 1000  # convert to km
                elevation_gain = activity.get('elevationGain', 0)
                location = activity.get('locationName', 'Unknown')
                
                print(f"\n{i+1}. Activity ID: {activity_id}")
                print(f"   Name: {activity_name}")
                print(f"   Date: {start_time}")
                print(f"   Distance: {distance:.2f} km")
                print(f"   Elevation gain: {elevation_gain:.0f} meters")
                print(f"   Location: {location}")
        else:
            print("No activities found with location keywords")
            
    except Exception as e:
        print(f"Error searching activities: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        find_trail_running_activities()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
