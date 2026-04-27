#!/usr/bin/env python3
"""
Reset Garmin tokens and re-authenticate for China region
"""

import sys
import os
import shutil
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garmin_mcp import init_api
from garmin_mcp.workouts import schedule_workout

def reset_tokens():
    """Reset existing Garmin tokens"""
    # Use China-specific token path
    tokenstore = "~/.garminconnect_cn"
    tokenstore_base64 = "~/.garminconnect_cn_base64"
    
    # Expand paths
    tokenstore_expanded = os.path.expanduser(tokenstore)
    tokenstore_base64_expanded = os.path.expanduser(tokenstore_base64)
    
    print(f"Resetting Garmin tokens (China region)...")
    print(f"Token directory: {tokenstore_expanded}")
    print(f"Base64 token file: {tokenstore_base64_expanded}")
    
    # Remove token directory if it exists
    if os.path.exists(tokenstore_expanded):
        try:
            shutil.rmtree(tokenstore_expanded)
            print(f"✓ Removed token directory: {tokenstore_expanded}")
        except Exception as e:
            print(f"✗ Error removing token directory: {e}")
    
    # Remove base64 token file if it exists
    if os.path.exists(tokenstore_base64_expanded):
        try:
            os.remove(tokenstore_base64_expanded)
            print(f"✓ Removed base64 token file: {tokenstore_base64_expanded}")
        except Exception as e:
            print(f"✗ Error removing base64 token file: {e}")
    
    print("✓ Token reset completed")

def main():
    """Main function"""
    try:
        # Reset existing tokens
        reset_tokens()
        
        # Set environment variables for China region
        os.environ['GARMIN_CN'] = 'true'
        
        # Initialize Garmin API (will prompt for credentials)
        print("\nInitializing Garmin API (China region)...")
        print("Note: You will need to enter your Garmin Connect China credentials.")
        print("Make sure to use your China region account.")
        
        # Get credentials from user
        email = input("Enter your Garmin Connect China email: ").strip()
        password = input("Enter your Garmin Connect China password: ").strip()
        
        garmin_client = init_api(email, password, is_cn=True)
        
        if not garmin_client:
            print("Error: Failed to initialize Garmin API.")
            return
        
        print("\n✓ Successfully authenticated with Garmin Connect China")
        print("Tokens have been saved for future use.")
        
        # Test connection by getting user profile
        print("\nTesting China region connection...")
        user_profile = garmin_client.get_user_profile()
        if user_profile:
            print("✓ Successfully retrieved user profile from China region")
        
        # Get existing workouts
        print("\nGetting existing workouts...")
        all_workouts = garmin_client.get_workouts()
        
        if not all_workouts:
            print("No workouts found in your library.")
            return
        
        print(f"Found {len(all_workouts)} workouts:")
        for i, workout in enumerate(all_workouts[:5]):  # Show first 5
            workout_id = workout.get('workoutId')
            name = workout.get('workoutName')
            sport = workout.get('sportType', {}).get('sportTypeKey')
            print(f"  {i+1}. {name} (ID: {workout_id}, Sport: {sport})")
        
        if len(all_workouts) > 5:
            print(f"  ... and {len(all_workouts) - 5} more workouts")
        
        # Define workout mapping based on workout names
        workout_mapping = {
            'easy_run': 'Erun-40min',
            'tempo_run': 'Erun-50min',
            'long_run': 'LSD-90min',
            'interval_training': '元大都-1.2km间歇'
        }
        
        # Get workout IDs
        workout_ids = {}
        for key, name in workout_mapping.items():
            for workout in all_workouts:
                if workout.get('workoutName') == name:
                    workout_ids[key] = workout.get('workoutId')
                    print(f"Found {name} (ID: {workout_ids[key]}) for {key}")
                    break
        
        # Current date
        today = datetime.now()
        
        # Adjusted training plan for the next 7 days
        adjusted_plan = [
            {
                'date': (today + timedelta(days=0)).strftime('%Y-%m-%d'),
                'type': 'easy_run',
                'name': '轻松跑6公里'
            },
            {
                'date': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                'type': 'interval_training',
                'name': '间歇训练'
            },
            {
                'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                'type': 'rest',
                'name': '休息'
            },
            {
                'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'type': 'easy_run',
                'name': '轻松跑6公里'
            },
            {
                'date': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
                'type': 'tempo_run',
                'name': 'Tempo跑'
            },
            {
                'date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
                'type': 'rest',
                'name': '休息'
            },
            {
                'date': (today + timedelta(days=6)).strftime('%Y-%m-%d'),
                'type': 'long_run',
                'name': '长距离跑10公里'
            }
        ]
        
        # Schedule workouts
        print("\nScheduling training plan to China region calendar...")
        scheduled = []
        
        for plan in adjusted_plan:
            if plan['type'] == 'rest':
                print(f"Skipping rest day: {plan['date']}")
                continue
            
            workout_type = plan['type']
            if workout_type in workout_ids:
                workout_id = workout_ids[workout_type]
                date = plan['date']
                
                try:
                    # Schedule workout
                    url = f"workout-service/schedule/{workout_id}"
                    response = garmin_client.garth.post("connectapi", url, json={"date": date})
                    
                    if response.status_code == 200:
                        print(f"✓ Scheduled {plan['name']} for {date}")
                        scheduled.append(plan)
                    else:
                        print(f"✗ Failed to schedule {plan['name']} for {date}: HTTP {response.status_code}")
                        print(f"  Response: {response.text}")
                except Exception as e:
                    print(f"✗ Error scheduling {plan['name']} for {date}: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"✗ No workout found for {plan['type']}")
        
        print("\n" + "=" * 60)
        print("SCHEDULING RESULTS")
        print("=" * 60)
        print(f"Successfully scheduled {len(scheduled)} workouts:")
        for workout in scheduled:
            print(f"  - {workout['date']}: {workout['name']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
