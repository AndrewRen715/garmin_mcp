#!/usr/bin/env python3
"""
Get actual activity segments from Garmin Connect API for the 2024-10-08 trail run activity
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, 'src')

from garminconnect import Garmin

def format_pace(minutes_per_km):
    """Format pace from minutes per km to min:sec per km"""
    if minutes_per_km <= 0:
        return "00:00"
    total_seconds = minutes_per_km * 60
    mins = int(total_seconds // 60)
    secs = int(total_seconds % 60)
    return f"{mins:02d}:{secs:02d}"

def get_activity_segments_actual():
    """Get actual activity segments from Garmin Connect API"""
    print("Getting actual activity segments from Garmin Connect API...")
    print("Activity: 杭州市 越野跑 (ID: 420601500)")
    print()
    
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
    
    print(f"\nUsing {region} region for data retrieval...")
    
    # Activity ID
    activity_id = "420601500"
    
    try:
            # Get detailed activity data
            print(f"\nGetting detailed activity data for ID: {activity_id}...")
            # Try different methods to get activity details
            
            # First try get_activity
            if hasattr(garmin_client, 'get_activity'):
                try:
                    activity = garmin_client.get_activity(activity_id)
                    print("✓ Using get_activity method")
                    print(f"  Response type: {type(activity)}")
                    print(f"  Has lapDTOList: {'lapDTOList' in activity}")
                    if 'lapDTOList' in activity:
                        print(f"  Number of laps: {len(activity['lapDTOList'])}")
                except Exception as e:
                    print(f"✗ Error with get_activity: {e}")
                    activity = None
            else:
                print("✗ get_activity method not available")
                activity = None
            
            # If no data, try get_activity_details
            if not activity and hasattr(garmin_client, 'get_activity_details'):
                try:
                    activity = garmin_client.get_activity_details(activity_id)
                    print("✓ Using get_activity_details method")
                    print(f"  Response type: {type(activity)}")
                    print(f"  Has lapDTOList: {'lapDTOList' in activity}")
                    if 'lapDTOList' in activity:
                        print(f"  Number of laps: {len(activity['lapDTOList'])}")
                except Exception as e:
                    print(f"✗ Error with get_activity_details: {e}")
                    activity = None
            
            # If no data, try get_activity_by_id
            if not activity and hasattr(garmin_client, 'get_activity_by_id'):
                try:
                    activity = garmin_client.get_activity_by_id(activity_id)
                    print("✓ Using get_activity_by_id method")
                    print(f"  Response type: {type(activity)}")
                    print(f"  Has lapDTOList: {'lapDTOList' in activity}")
                    if 'lapDTOList' in activity:
                        print(f"  Number of laps: {len(activity['lapDTOList'])}")
                except Exception as e:
                    print(f"✗ Error with get_activity_by_id: {e}")
                    activity = None
            
            # Check if we have any activity data
            if not activity:
                print(f"Error: No activity found with ID {activity_id}")
                return
            
            # Print response structure for debugging
            print("\nResponse structure:")
            print(f"Type: {type(activity)}")
            if isinstance(activity, dict):
                print(f"Keys: {list(activity.keys())}")
                # Check if we have any data in the response
                if 'splitSummaries' in activity:
                    print(f"splitSummaries length: {len(activity['splitSummaries'])}")
                    # Print first split to see structure
                    if activity['splitSummaries']:
                        first_split = activity['splitSummaries'][0]
                        print(f"First split keys: {list(first_split.keys())}")
                elif 'lapDTOList' in activity:
                    print(f"lapDTOList length: {len(activity['lapDTOList'])}")
                elif 'laps' in activity:
                    print(f"laps length: {len(activity['laps'])}")
                elif 'splits' in activity:
                    print(f"splits length: {len(activity['splits'])}")
                
                # Check summaryDTO for basic info
                if 'summaryDTO' in activity:
                    print(f"Has summaryDTO: True")
                
                # Check for other potential split/lap fields
                for key in activity.keys():
                    if any(substring in key.lower() for substring in ['split', 'lap']):
                        print(f"Found potential split/lap field: {key}")
            
            # Print basic activity information
            print("\nActivity Basic Information:")
            print(f"- Name: {activity.get('activityName')}")
            
            # Get info from summaryDTO if available
            summary = activity.get('summaryDTO', {})
            if summary:
                print(f"- Date: {summary.get('startTimeLocal')}")
                print(f"- Distance: {summary.get('distance', 0) / 1000:.2f} km")
                print(f"- Duration: {summary.get('duration', 0) / 60:.1f} minutes")
                print(f"- Elevation gain: {summary.get('elevationGain', 0):.0f} meters")
                distance_km = summary.get('distance', 1) / 1000
                duration_min = summary.get('duration', 0) / 60
                if distance_km > 0:
                    print(f"- Average pace: {duration_min / distance_km:.2f} min/km")
                else:
                    print(f"- Average pace: 0.00 min/km")
            else:
                print(f"- Date: {activity.get('startTimeLocal')}")
                print(f"- Distance: {activity.get('distance', 0) / 1000:.2f} km")
                print(f"- Duration: {activity.get('duration', 0) / 60:.1f} minutes")
                print(f"- Elevation gain: {activity.get('elevationGain', 0):.0f} meters")
                print(f"- Average pace: {activity.get('duration', 0) / (activity.get('distance', 1) / 1000):.2f} min/km")
            print()
            
            # Try to get split data from splitSummaries
            print("\nGetting split data...")
            splits = activity.get('splitSummaries', [])
            
            if splits:
                print(f"Found {len(splits)} splits:")
                print("-" * 180)
                print(f"{'Split':<8} {'Distance':<10} {'Time':<12} {'Pace':<12} {'Elevation':<15} {'HR':<10} {'Power':<12}")
                print("-" * 180)
                
                for i, split in enumerate(splits):
                    if isinstance(split, dict):
                        # Get distance and time from split data
                        split_distance = split.get('distance', 0) / 1000  # convert to km
                        split_time = split.get('duration', 0) / 60  # convert to minutes
                        split_pace = split_time / split_distance if split_distance > 0 else 0
                        
                        # Get elevation data
                        split_elevation_gain = split.get('elevationGain', 0)
                        split_elevation_loss = split.get('elevationLoss', 0)
                        
                        # Get heart rate data
                        split_hr = split.get('averageHeartRate', split.get('averageHR', 0))
                        split_max_hr = split.get('maxHeartRate', split.get('maxHR', 0))
                        
                        # Get power data
                        split_power = split.get('averagePower', 0)
                        
                        # Format display strings
                        time_str = f"{int(split_time // 60):02d}:{int(split_time % 60):02d}"
                        pace_str = f"{split_pace:.2f} min/km"
                        elevation_str = f"+{split_elevation_gain:.0f}/-{split_elevation_loss:.0f}"
                        hr_str = f"{split_hr}/{split_max_hr}"
                        power_str = f"{split_power}W"
                        
                        print(f"{i+1:<8} {split_distance:.2f} km    {time_str:<12} {pace_str:<12} {elevation_str:<15} {hr_str:<10} {power_str:<12}")
                
                print("-" * 180)
            else:
                print("No split data found in activity.")
            
            # Try to get detailed activity data with metrics
            print("\nGetting detailed activity metrics...")
            
            try:
                # Get detailed activity data
                detailed_activity = garmin_client.get_activity_details(activity_id)
                
                if detailed_activity:
                    print("Detailed activity data retrieved successfully.")
                    
                    # Print detailed activity structure
                    print(f"Detailed activity type: {type(detailed_activity)}")
                    if isinstance(detailed_activity, dict):
                        print(f"Detailed activity keys: {list(detailed_activity.keys())}")
            except Exception as e:
                print(f"Error getting detailed activity metrics: {e}")
            
            # Try using garth client directly to get splits
            print("\nTrying to get splits via garth client...")
            try:
                # Check if garmin_client has garth attribute
                if hasattr(garmin_client, 'garth'):
                    print("✓ Using garth client for direct API calls")
                    
                    # Try different split endpoints
                    split_endpoints = [
                        f"activity-service/activity/{activity_id}/splits",
                        f"activity-service/activity/{activity_id}/splits/summary",
                        f"activity-service/activity/{activity_id}/laps"
                    ]
                    
                    for endpoint in split_endpoints:
                        try:
                            print(f"\nTrying endpoint: {endpoint}")
                            response = garmin_client.garth.get("connectapi", endpoint)
                            
                            if response.status_code == 200:
                                split_data = response.json()
                                print(f"✓ Success! Status code: {response.status_code}")
                                print(f"  Response type: {type(split_data)}")
                                
                                if isinstance(split_data, dict):
                                    print(f"  Keys: {list(split_data.keys())}")
                                    
                                    # Check if we have lapDTOs in the response
                                    if 'lapDTOs' in split_data:
                                        laps = split_data['lapDTOs']
                                        print(f"  Found {len(laps)} laps")
                                        
                                        if laps:
                                            # Print first lap structure
                                            first_lap = laps[0]
                                            print(f"  First lap keys: {list(first_lap.keys())}")
                                            
                                            # Display laps if they look like per-kilometer splits
                                            if len(laps) > 5 and all('distance' in lap for lap in laps[:5]):
                                                print(f"\nFound {len(laps)} potential per-kilometer laps:")
                                                print("-" * 180)
                                                print(f"{'Lap':<8} {'Distance':<10} {'Time':<12} {'Moving Time':<12} {'Pace':<12} {'Moving Pace':<12} {'Elevation':<15} {'HR':<10} {'Power':<12}")
                                                print("-" * 180)
                                                
                                                for i, lap in enumerate(laps):
                                                    if isinstance(lap, dict):
                                                        lap_distance = lap.get('distance', 0) / 1000  # convert to km
                                                        
                                                        # Total time
                                                        lap_time = lap.get('duration', 0) / 60  # convert to minutes
                                                        lap_pace = lap_time / lap_distance if lap_distance > 0 else 0
                                                        
                                                        # Moving time (excluding rest)
                                                        lap_moving_time = lap.get('movingDuration', 0) / 60  # convert to minutes
                                                        lap_moving_pace = lap_moving_time / lap_distance if lap_distance > 0 else 0
                                                        
                                                        lap_elevation_gain = lap.get('elevationGain', 0)
                                                        lap_elevation_loss = lap.get('elevationLoss', 0)
                                                        lap_hr = lap.get('averageHR', lap.get('averageHeartRate', 0))
                                                        lap_max_hr = lap.get('maxHR', lap.get('maxHeartRate', 0))
                                                        lap_power = lap.get('averagePower', 0)
                                                        
                                                        time_str = f"{int(lap_time // 60):02d}:{int(lap_time % 60):02d}"
                                                        moving_time_str = f"{int(lap_moving_time // 60):02d}:{int(lap_moving_time % 60):02d}"
                                                        pace_str = f"{format_pace(lap_pace)} min/km"
                                                        moving_pace_str = f"{format_pace(lap_moving_pace)} min/km"
                                                        elevation_str = f"+{lap_elevation_gain:.0f}/-{lap_elevation_loss:.0f}"
                                                        hr_str = f"{lap_hr}/{lap_max_hr}"
                                                        power_str = f"{lap_power}W"
                                                        
                                                        print(f"{i+1:<8} {lap_distance:.2f} km    {time_str:<12} {moving_time_str:<12} {pace_str:<12} {moving_pace_str:<12} {elevation_str:<15} {hr_str:<10} {power_str:<12}")
                                                
                                                print("-" * 180)
                                                break
                                    
                                    # Check if we have splits in the response
                                    elif 'splits' in split_data:
                                        splits = split_data['splits']
                                        print(f"  Found {len(splits)} splits")
                                        
                                        if splits:
                                            # Print first split structure
                                            first_split = splits[0]
                                            print(f"  First split keys: {list(first_split.keys())}")
                                    
                                    # Check if we have lapDTOList in the response
                                    elif 'lapDTOList' in split_data:
                                        laps = split_data['lapDTOList']
                                        print(f"  Found {len(laps)} laps")
                                        
                                        if laps:
                                            # Print first lap structure
                                            first_lap = laps[0]
                                            print(f"  First lap keys: {list(first_lap.keys())}")
                            else:
                                print(f"✗ Failed: Status code {response.status_code}")
                        except Exception as e:
                            print(f"✗ Error with endpoint {endpoint}: {e}")
                else:
                    print("✗ garth client not available")
            except Exception as e:
                print(f"Error getting splits via garth: {e}")
                import traceback
                traceback.print_exc()
                
    except Exception as e:
        print(f"Error getting activity segments: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    try:
        get_activity_segments_actual()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
