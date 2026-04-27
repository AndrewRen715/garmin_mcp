#!/usr/bin/env python3
"""
Test Garmin Connect China region connection directly
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def main():
    """Main function"""
    try:
        # Set China region
        is_cn = True
        
        print(f"Testing Garmin Connect {'China' if is_cn else 'Global'} region connection...")
        
        # Get credentials from user
        email = input("Enter your Garmin Connect email: ").strip()
        password = input("Enter your Garmin Connect password: ").strip()
        
        # Initialize Garmin client
        print("\nInitializing Garmin client...")
        garmin = Garmin(email=email, password=password, is_cn=is_cn)
        
        # Login
        print("Logging in...")
        garmin.login()
        print("✓ Login successful!")
        
        # Test API endpoints
        print("\nTesting API endpoints...")
        
        # Get user profile
        print("1. Getting user profile...")
        user_profile = garmin.get_user_profile()
        if user_profile:
            print("✓ User profile retrieved successfully")
            print(f"   User ID: {user_profile.get('userId')}")
            print(f"   Display name: {user_profile.get('displayName')}")
        else:
            print("✗ Failed to get user profile")
        
        # Get workouts
        print("\n2. Getting workouts...")
        workouts = garmin.get_workouts()
        if workouts:
            print(f"✓ Found {len(workouts)} workouts")
            for i, workout in enumerate(workouts[:3]):
                print(f"   {i+1}. {workout.get('workoutName')} (ID: {workout.get('workoutId')})")
        else:
            print("✗ No workouts found")
        
        # Test calendar scheduling
        print("\n3. Testing calendar scheduling...")
        if workouts:
            # Use the first workout
            test_workout = workouts[0]
            workout_id = test_workout.get('workoutId')
            workout_name = test_workout.get('workoutName')
            
            # Schedule for day after tomorrow
            test_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
            print(f"   Scheduling {workout_name} for {test_date}...")
            
            try:
                # Schedule workout using the correct method
                url = f"workout-service/schedule/{workout_id}"
                print(f"   API URL: {url}")
                
                # Make the request using garth client
                response = garmin.garth.post("connectapi", url, json={"date": test_date})
                
                print(f"   HTTP Status: {response.status_code}")
                print(f"   Response: {response.text}")
                
                if response.status_code == 200:
                    print(f"✓ Successfully scheduled {workout_name} for {test_date}")
                else:
                    print(f"✗ Failed to schedule workout")
                    
            except Exception as e:
                print(f"✗ Error scheduling workout: {e}")
                import traceback
                traceback.print_exc()
        
        # Test getting scheduled workouts
        print("\n4. Getting scheduled workouts...")
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        try:
            # Query scheduled workouts
            query = {
                "query": f'query{{workoutScheduleSummariesScalar(startDate:"{today}", endDate:"{next_week}")}}'
            }
            
            print(f"   Querying from {today} to {next_week}")
            
            result = garmin.query_garmin_graphql(query)
            
            if result and "data" in result:
                scheduled = result["data"].get("workoutScheduleSummariesScalar", [])
                print(f"✓ Found {len(scheduled)} scheduled workouts")
                for workout in scheduled:
                    date = workout.get('scheduleDate')
                    name = workout.get('workoutName')
                    completed = workout.get('associatedActivityId') is not None
                    print(f"   {date}: {name} {'✓' if completed else '○'}")
            else:
                print("✗ Failed to get scheduled workouts")
                print(f"   Result: {result}")
                
        except Exception as e:
            print(f"✗ Error getting scheduled workouts: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED")
        print("=" * 60)
        print(f"Region: {'China' if is_cn else 'Global'}")
        print(f"Login: {'Successful' if garmin else 'Failed'}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
