#!/usr/bin/env python3
"""
Search for trail running activities in 2024
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def search_2024_trail_runs():
    """Search for trail running activities in 2024"""
    print("Searching for 2024 trail running activities...")
    
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
    
    # Define 2024 date range
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    print(f"\nSearching for activities from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Try to get activities by date range
        print("\nTrying to get activities by date range...")
        
        # Get activities in batches
        all_activities = []
        batch_size = 100
        start_index = 0
        
        # Try to get activities
        while True:
            print(f"Getting batch {start_index//batch_size + 1} (start={start_index})")
            activities = garmin_client.get_activities(start_index, batch_size)
            
            if not activities:
                break
            
            all_activities.extend(activities)
            start_index += batch_size
            
            # Break if we've got enough activities
            if len(all_activities) >= 500:
                break
        
        print(f"Found {len(all_activities)} activities in total")
        
        # Filter for 2024 activities
        activities_2024 = []
        for activity in all_activities:
            start_time = activity.get('startTimeLocal')
            if start_time:
                # Parse date from start time
                try:
                    activity_date = datetime.fromisoformat(start_time.replace(' ', 'T'))
                    if 2024 == activity_date.year:
                        activities_2024.append(activity)
                except:
                    pass
        
        print(f"Filtered to {len(activities_2024)} activities from 2024")
        
        # Filter for running and trail running activities
        running_activities = []
        for activity in activities_2024:
            activity_type = activity.get('activityType', {}).get('typeKey')
            if activity_type in ['running', 'trail_running']:
                running_activities.append(activity)
        
        print(f"Filtered to {len(running_activities)} running/trail running activities from 2024")
        
        # Sort by elevation gain (descending)
        running_activities.sort(key=lambda x: x.get('elevationGain', 0), reverse=True)
        
        # Show activities
        print(f"\n2024 running/trail running activities sorted by elevation gain:")
        
        trail_candidates = []
        
        for i, activity in enumerate(running_activities):
            activity_id = activity.get('activityId')
            activity_name = activity.get('activityName')
            start_time = activity.get('startTimeLocal')
            distance = activity.get('distance', 0) / 1000  # convert to km
            elevation_gain = activity.get('elevationGain', 0)
            duration = activity.get('duration', 0) / 60  # convert to minutes
            location = activity.get('locationName', 'Unknown')
            activity_type = activity.get('activityType', {}).get('typeKey')
            
            # Calculate elevation per km
            elevation_per_km = elevation_gain / distance if distance > 0 else 0
            
            # Check if this might be a trail run
            is_trail_candidate = False
            # Look specifically for 标毅线 in Hangzhou with 24+km and 1800m elevation gain
            if ('杭州' in location or 'Hangzhou' in location) and (
                (distance >= 20 and elevation_gain >= 1500) or 
                '标毅' in activity_name or 
                'biaoyi' in activity_name.lower()
            ):
                is_trail_candidate = True
                trail_candidates.append(activity)
                print(f"\n{i+1}. Activity ID: {activity_id}")
                print(f"   Name: {activity_name}")
                print(f"   Date: {start_time}")
                print(f"   Distance: {distance:.2f} km")
                print(f"   Elevation gain: {elevation_gain:.0f} meters")
                print(f"   Elevation per km: {elevation_per_km:.1f} m/km")
                print(f"   Duration: {duration:.1f} minutes")
                print(f"   Activity type: {activity_type}")
                print(f"   Location: {location}")
                # Highlight if it matches 标毅线 criteria
                if distance >= 24 and elevation_gain >= 1800 and '杭州' in location:
                    print(f"   ✅ POTENTIAL 标毅线 MATCH!")
                else:
                    print(f"   ⚠ Possible trail running activity!")
        
        # Also show activities with relevant keywords
        print("\n" + "=" * 60)
        print("2024 activities with relevant keywords:")
        print("=" * 60)
        
        keyword_activities = []
        keywords = ["杭州", "trail", "越野", "标毅", "Hangzhou", "mountain", "hill"]
        
        for activity in activities_2024:
            activity_name = activity.get('activityName', '').lower()
            location = activity.get('locationName', '').lower()
            
            for keyword in keywords:
                if keyword.lower() in activity_name or keyword.lower() in location:
                    keyword_activities.append(activity)
                    break
        
        if keyword_activities:
            for i, activity in enumerate(keyword_activities):
                activity_id = activity.get('activityId')
                activity_name = activity.get('activityName')
                start_time = activity.get('startTimeLocal')
                distance = activity.get('distance', 0) / 1000  # convert to km
                elevation_gain = activity.get('elevationGain', 0)
                activity_type = activity.get('activityType', {}).get('typeKey')
                location = activity.get('locationName', 'Unknown')
                
                print(f"\n{i+1}. Activity ID: {activity_id}")
                print(f"   Name: {activity_name}")
                print(f"   Date: {start_time}")
                print(f"   Distance: {distance:.2f} km")
                print(f"   Elevation gain: {elevation_gain:.0f} meters")
                print(f"   Activity type: {activity_type}")
                print(f"   Location: {location}")
        else:
            print("No activities found with relevant keywords")
        
        # Summary
        print("\n" + "=" * 60)
        print("SEARCH SUMMARY")
        print("=" * 60)
        print(f"Total activities searched: {len(all_activities)}")
        print(f"2024 activities: {len(activities_2024)}")
        print(f"2024 running activities: {len(running_activities)}")
        print(f"Trail run candidates: {len(trail_candidates)}")
        print(f"Keyword matches: {len(keyword_activities)}")
        
        if trail_candidates:
            print("\n✓ Found potential trail running activities!")
        else:
            print("\n✗ No trail running activities found in 2024")
            
    except Exception as e:
        print(f"Error searching activities: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        search_2024_trail_runs()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
