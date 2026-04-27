#!/usr/bin/env python3
"""
Analyze training status and schedule adjusted training plan to Garmin calendar
"""

import json
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garmin_mcp import workouts
from garmin_mcp import init_api

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

def get_workout_id_by_name(workouts_list, name):
    """Get workout ID by name"""
    for workout in workouts_list:
        if workout.get('workoutName') == name:
            return workout.get('workoutId')
    return None

def schedule_adjusted_plan(garmin_client):
    """Schedule adjusted training plan based on analysis"""
    # Get existing workouts
    all_workouts = garmin_client.get_workouts()
    
    # Define workout mapping based on workout names we have
    workout_mapping = {
        'easy_run': 'Erun-40min',
        'tempo_run': 'Erun-50min',
        'long_run': 'LSD-90min',
        'interval_training': '元大都-1.2km间歇'
    }
    
    # Get workout IDs
    workout_ids = {}
    for key, name in workout_mapping.items():
        workout_id = get_workout_id_by_name(all_workouts, name)
        if workout_id:
            workout_ids[key] = workout_id
            print(f"Found {name} (ID: {workout_id}) for {key}")
        else:
            print(f"Warning: Could not find {name} for {key}")
    
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
        
        # Initialize Garmin API
        print("Initializing Garmin API (China region)...")
        garmin_client = init_api(None, None, is_cn=True)
        workouts.configure(garmin_client)
        
        # Analyze training status
        print("\nAnalyzing training and sleep data...")
        analysis = analyze_training_status()
        
        print("\nTRAINING ANALYSIS")
        print("=" * 60)
        print(f"Training Status: {json.dumps(analysis['training_status'], indent=2, ensure_ascii=False)}")
        print(f"Sleep Status: {json.dumps(analysis['sleep_status'], indent=2, ensure_ascii=False)}")
        print(f"Recommendations: {analysis['recommendations']}")
        
        # Schedule adjusted plan
        print("\nScheduling adjusted training plan...")
        scheduled = schedule_adjusted_plan(garmin_client)
        
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
