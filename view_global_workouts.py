#!/usr/bin/env python3
"""
View global region workouts to understand available workout names
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def main():
    """Main function"""
    print("Viewing global region workouts...")
    
    # Initialize Garmin client for global region
    print("Initializing global region client...")
    try:
        garmin_global = Garmin(is_cn=False)
        garmin_global.login("~/.garminconnect")
        print("✓ Global region client initialized (using tokens)")
    except Exception as e:
        print(f"✗ Failed to initialize global region client: {e}")
        return
    
    # Get all workouts
    print("\nGetting all global region workouts...")
    global_all_workouts = garmin_global.get_workouts()
    
    print(f"Found {len(global_all_workouts)} workouts in global region library:")
    
    # Display workout names and IDs
    for i, workout in enumerate(global_all_workouts[:20]):  # Show first 20
        workout_id = workout.get('workoutId')
        name = workout.get('workoutName')
        sport = workout.get('sportType', {}).get('sportTypeKey')
        print(f"  {i+1}. {name} (ID: {workout_id}, Sport: {sport})")
    
    if len(global_all_workouts) > 20:
        print(f"  ... and {len(global_all_workouts) - 20} more workouts")
    
    # Get current calendar
    print("\nGetting current global region calendar...")
    today = datetime.now().strftime('%Y-%m-%d')
    next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    try:
        query = {
            "query": f'query{{workoutScheduleSummariesScalar(startDate:"{today}", endDate:"{next_month}")}}'
        }
        
        result = garmin_global.query_garmin_graphql(query)
        
        if result and "data" in result:
            scheduled = result["data"].get("workoutScheduleSummariesScalar", [])
            print(f"\nCurrent scheduled workouts ({len(scheduled)}):")
            for workout in scheduled:
                date = workout.get('scheduleDate')
                name = workout.get('workoutName')
                completed = workout.get('associatedActivityId') is not None
                print(f"  {date}: {name} {'✓' if completed else '○'}")
        else:
            print("No scheduled workouts found")
    except Exception as e:
        print(f"Error getting scheduled workouts: {e}")

if __name__ == "__main__":
    main()
