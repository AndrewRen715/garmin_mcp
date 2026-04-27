#!/usr/bin/env python3
"""
Check existing workouts and schedule training plan to Garmin calendar
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garmin_mcp import workouts
from garmin_mcp import init_api

def main():
    """Main function"""
    try:
        # Set environment variables for China region
        os.environ['GARMIN_CN'] = 'true'
        
        # Initialize Garmin API
        print("Initializing Garmin API...")
        garmin_client = init_api(None, None, is_cn=True)
        workouts.configure(garmin_client)
        
        # Get existing workouts
        print("\nGetting existing workouts...")
        all_workouts = garmin_client.get_workouts()
        
        if not all_workouts:
            print("No workouts found in your library.")
            return
        
        print(f"Found {len(all_workouts)} workouts:")
        for i, workout in enumerate(all_workouts[:10]):  # Show first 10
            workout_id = workout.get('workoutId')
            name = workout.get('workoutName')
            sport = workout.get('sportType', {}).get('sportTypeKey')
            print(f"  {i+1}. {name} (ID: {workout_id}, Sport: {sport})")
        
        if len(all_workouts) > 10:
            print(f"  ... and {len(all_workouts) - 10} more workouts")
        
        # Get scheduled workouts for this week
        print("\nGetting scheduled workouts for this week...")
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        scheduled = garmin_client.query_garmin_graphql({
            "query": f'query{{workoutScheduleSummariesScalar(startDate:"{today}", endDate:"{next_week}")}}'
        })
        
        if scheduled and "data" in scheduled:
            scheduled_workouts = scheduled["data"].get("workoutScheduleSummariesScalar", [])
            print(f"Scheduled workouts ({len(scheduled_workouts)}):")
            for workout in scheduled_workouts:
                date = workout.get('scheduleDate')
                name = workout.get('workoutName')
                completed = workout.get('associatedActivityId') is not None
                print(f"  {date}: {name} {'✓' if completed else '○'}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
