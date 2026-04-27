#!/usr/bin/env python3
"""
Schedule adjusted training plan based on training status and sleep data
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def load_json_file(file_path):
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def analyze_training_status():
    """Analyze training status and sleep data"""
    # Load training status data
    training_data = load_json_file('training_status_data.json')
    sleep_data = load_json_file('weekly_sleep_data.json')
    
    analysis = {
        'training_status': {},
        'sleep_status': {},
        'recommendations': []
    }
    
    # Analyze training status
    if training_data and 'training_readiness' in training_data:
        readiness = training_data['training_readiness']
        analysis['training_status'] = {
            'date': readiness.get('date'),
            'resting_heart_rate': readiness.get('resting_heart_rate_bpm'),
            'body_battery': readiness.get('body_battery_current'),
            'stress_level': readiness.get('average_stress_level'),
            'sleep_duration': readiness.get('sleeping_seconds', 0) / 3600
        }
    
    # Analyze sleep data
    if sleep_data and 'weekly_summary' in sleep_data:
        weekly = sleep_data['weekly_summary']
        analysis['sleep_status'] = {
            'average_duration': weekly.get('average_sleep_duration'),
            'average_score': weekly.get('average_sleep_score'),
            'latest_score': weekly.get('latest_sleep_score')
        }
    
    # Generate recommendations
    if analysis['training_status'].get('body_battery', 100) < 40:
        analysis['recommendations'].append('Reduce training intensity due to low body battery')
    
    if analysis['sleep_status'].get('average_score', 100) < 70:
        analysis['recommendations'].append('Prioritize sleep recovery')
    
    return analysis

def schedule_training_plan(garmin_client, analysis):
    """Schedule adjusted training plan based on analysis"""
    # Get existing workouts
    all_workouts = garmin_client.get_workouts()
    
    # Define workout mapping based on workout names
    workout_mapping = {
        'easy_run': '轻松跑3K热身',
        'tempo_run': '轻松跑3K热身',
        'long_run': '长距离跑',
        'interval_training': '冲刺训练'
    }
    
    # Get workout IDs
    workout_ids = {}
    for key, name in workout_mapping.items():
        for workout in all_workouts:
            if workout.get('workoutName') == name:
                workout_ids[key] = workout.get('workoutId')
                print(f"Found workout '{name}' (ID: {workout_ids[key]}) for {key}")
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
        else:
            print(f"✗ No workout found for {plan['type']}")
    
    return scheduled

def main():
    """Main function"""
    try:
        # Set environment variables for China region
        os.environ['GARMIN_CN'] = 'true'
        
        # Initialize Garmin client
        print("Initializing Garmin Connect China region client...")
        
        # Get credentials from user
        email = input("Enter your Garmin Connect email: ").strip()
        password = input("Enter your Garmin Connect password: ").strip()
        
        garmin_client = Garmin(email=email, password=password, is_cn=True)
        garmin_client.login()
        
        print("✓ Login successful!")
        
        # Analyze training status
        print("\nAnalyzing training status and sleep data...")
        analysis = analyze_training_status()
        
        print("\nTRAINING ANALYSIS")
        print("=" * 60)
        print(f"Training Status: {json.dumps(analysis['training_status'], indent=2, ensure_ascii=False)}")
        print(f"Sleep Status: {json.dumps(analysis['sleep_status'], indent=2, ensure_ascii=False)}")
        print(f"Recommendations: {analysis['recommendations']}")
        
        # Schedule adjusted plan
        print("\nScheduling adjusted training plan...")
        scheduled = schedule_training_plan(garmin_client, analysis)
        
        # Verify schedule
        print("\nVerifying schedule...")
        today = datetime.now().strftime('%Y-%m-%d')
        next_week = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        
        verification = garmin_client.query_garmin_graphql({
            "query": f'query{{workoutScheduleSummariesScalar(startDate:"{today}", endDate:"{next_week}")}}'
        })
        
        if verification and "data" in verification:
            verified_workouts = verification["data"].get("workoutScheduleSummariesScalar", [])
            print(f"Verified schedule ({len(verified_workouts)} workouts):")
            for workout in verified_workouts:
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
