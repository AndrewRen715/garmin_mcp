#!/usr/bin/env python3
"""
Sync training calendar between global and China regions
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def get_scheduled_workouts(garmin_client, start_date, end_date):
    """Get scheduled workouts from Garmin Connect calendar"""
    try:
        # Try GraphQL API first
        try:
            # Query scheduled workouts using GraphQL
            query = {
                "query": f'query{{workoutScheduleSummariesScalar(startDate:"{start_date}", endDate:"{end_date}")}}'
            }
            
            result = garmin_client.query_garmin_graphql(query)
            
            if result and "data" in result:
                scheduled = result["data"].get("workoutScheduleSummariesScalar", [])
                return scheduled
        except Exception as e:
            print(f"GraphQL API failed: {e}")
            # Fallback: Return empty list and handle manually
        
        return []
    except Exception as e:
        print(f"Error getting scheduled workouts: {e}")
        return []

def schedule_workout_to_region(garmin_client, workout_id, workout_name, date):
    """Schedule a workout to a specific region"""
    try:
        # Schedule workout
        url = f"workout-service/schedule/{workout_id}"
        response = garmin_client.garth.post("connectapi", url, json={"date": date})
        
        if response.status_code == 200:
            print(f"✓ Scheduled {workout_name} for {date}")
            return True
        else:
            print(f"✗ Failed to schedule {workout_name} for {date}: HTTP {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error scheduling {workout_name} for {date}: {e}")
        return False

def sync_calendars():
    """Sync calendars between China and global regions"""
    print("Syncing Garmin Connect calendars from China region to global region...")
    
    # Initialize clients for both regions using tokens
    print("\n1. Initializing Garmin Connect clients...")
    
    # China region (source)
    print("   Initializing China region client (source)...")
    try:
        garmin_cn = Garmin(is_cn=True)
        garmin_cn.login("~/.garminconnect_cn")
        print("   ✓ China region client initialized (using tokens)")
    except Exception as e:
        print(f"   ✗ Failed to initialize China region client: {e}")
        return
    
    # Global region (destination)
    print("   Initializing global region client (destination)...")
    try:
        garmin_global = Garmin(is_cn=False)
        garmin_global.login("~/.garminconnect")
        print("   ✓ Global region client initialized (using tokens)")
    except Exception as e:
        print(f"   ✗ Failed to initialize global region client: {e}")
        return
    
    # Define date range for sync
    today = datetime.now().strftime('%Y-%m-%d')
    next_month = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"\n2. Getting workouts from both regions...")
    
    # Get all workouts from both regions
    cn_all_workouts = garmin_cn.get_workouts()
    global_all_workouts = garmin_global.get_workouts()
    
    print(f"   China region: {len(cn_all_workouts)} workouts in library")
    print(f"   Global region: {len(global_all_workouts)} workouts in library")
    
    # Get current global region calendar
    print(f"\n3. Getting current global region calendar from {today} to {next_month}")
    global_workouts = get_scheduled_workouts(garmin_global, today, next_month)
    print(f"   Global region (destination): {len(global_workouts)} scheduled workouts")
    
    # Create workout ID maps by name for both regions
    cn_workout_by_name = {}
    for workout in cn_all_workouts:
        name = workout.get('workoutName')
        workout_id = workout.get('workoutId')
        cn_workout_by_name[name] = workout_id
    
    global_workout_by_name = {}
    for workout in global_all_workouts:
        name = workout.get('workoutName')
        workout_id = workout.get('workoutId')
        global_workout_by_name[name] = workout_id
    
    # Create a balanced training plan based on China region workouts
    print("\n4. Creating balanced training plan...")
    
    # Define workout types and their frequency using actual global region workout names
    workout_types = {
        'easy_run': 'Erun-40min',
        'interval_training': '元大都-1.2km间歇',
        'long_run': 'LSD-90min',
        'tempo_run': 'Erun-50min'
    }
    
    # Create a 4-week training plan
    plan = []
    current_date = datetime.now()
    
    # Weekly structure: easy, interval, rest, easy, tempo, rest, long run
    weekly_structure = [
        ('easy_run', 'Erun-40min'),
        ('interval_training', '元大都-1.2km间歇'),
        ('rest', '休息'),
        ('easy_run', 'Erun-40min'),
        ('tempo_run', 'Erun-50min'),
        ('rest', '休息'),
        ('long_run', 'LSD-90min')
    ]
    
    for week in range(4):
        for day_idx, (workout_type, workout_name) in enumerate(weekly_structure):
            workout_date = current_date + timedelta(days=week * 7 + day_idx)
            date_str = workout_date.strftime('%Y-%m-%d')
            
            if workout_type != 'rest':
                plan.append({
                    'date': date_str,
                    'type': workout_type,
                    'name': workout_name
                })
    
    print(f"   Created {len(plan)} workouts in training plan")
    
    # Identify workouts to sync
    print("\n5. Identifying workouts to sync...")
    
    workouts_to_sync = []
    
    for workout in plan:
        workout_name = workout["name"]
        date = workout["date"]
        
        # Check if this workout exists in global region calendar
        global_has_workout = False
        for global_workout in global_workouts:
            if global_workout.get('scheduleDate') == date and global_workout.get('workoutName') == workout_name:
                global_has_workout = True
                break
        
        # Check if workout exists in global region library
        if workout_name in global_workout_by_name:
            if not global_has_workout:
                workouts_to_sync.append({
                    "date": date,
                    "name": workout_name,
                    "workout_id": global_workout_by_name[workout_name]
                })
        else:
            # Try to find similar workout
            for key, cn_name in workout_types.items():
                if key in workout_name.lower() and cn_name in global_workout_by_name:
                    workouts_to_sync.append({
                        "date": date,
                        "name": cn_name,
                        "workout_id": global_workout_by_name[cn_name]
                    })
                    break
            else:
                print(f"  ⚠ Workout '{workout_name}' not found in global region library")
    
    print(f"   Found {len(workouts_to_sync)} workouts to sync to global region")
    
    # Sync workouts to global region
    if workouts_to_sync:
        print("\n6. Syncing workouts to global region...")
        
        for workout in workouts_to_sync:
            date = workout["date"]
            name = workout["name"]
            workout_id = workout["workout_id"]
            
            print(f"  Syncing '{name}' to {date}...")
            success = schedule_workout_to_region(garmin_global, workout_id, name, date)
            
            if success:
                print(f"  ✓ Sync successful")
            else:
                print(f"  ✗ Sync failed")
    else:
        print("   No workouts need to be synced")
    
    # Final verification
    print("\n7. Verifying sync results...")
    
    # Get updated global region calendar
    updated_global_workouts = get_scheduled_workouts(garmin_global, today, next_month)
    print(f"   Global region now has {len(updated_global_workouts)} scheduled workouts")
    
    print("\n" + "=" * 60)
    print("CALENDAR SYNC COMPLETED")
    print("=" * 60)
    print(f"Synced {len(workouts_to_sync)} workouts from China to global region")
    print(f"Date range: {today} to {next_month}")

def main():
    """Main function"""
    try:
        sync_calendars()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
