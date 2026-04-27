"""Script to get training status data"""
import json
import os
import sys
from datetime import datetime, timedelta

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

# Set environment variables if not already set
if 'GARMIN_CN' not in os.environ:
    os.environ['GARMIN_CN'] = 'true'

# Initialize Garmin API with empty credentials (will use saved tokens)
print("Initializing Garmin API...")
is_cn = os.getenv('GARMIN_CN', 'true').lower() == 'true'
garmin_client = init_api(None, None, is_cn=is_cn)

if not garmin_client:
    print("Error: Failed to initialize Garmin API.")
    sys.exit(1)

# Get yesterday's date (since today might not have data yet)
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
print(f"Getting training status data for {yesterday}...")

# Try to get health stats data directly
try:
    print("Trying to get health stats data...")
    stats_data = garmin_client.get_stats(yesterday)
    print("Successfully retrieved health stats data")
    print(f"Data type: {type(stats_data)}")
    if stats_data:
        print(f"Data keys: {list(stats_data.keys())}")
    
    # Use stats data
    readiness_data = stats_data
except Exception as e:
    print(f"Error retrieving health stats data: {str(e)}")
    sys.exit(1)

# Process training readiness data
def process_training_readiness(data):
    """Process training readiness data"""
    if not data:
        return None
    
    # Extract essential metrics
    processed_data = {}
    
    # Check if data is morning training readiness (dict)
    if isinstance(data, dict):
        # Morning training readiness data
        if 'readinessScore' in data:
            processed_data['score'] = data.get('readinessScore')
            processed_data['level'] = data.get('readinessLevel')
            processed_data['recovery_time_hours'] = data.get('recoveryTime')
            processed_data['hrv_status'] = data.get('hrvStatus')
            processed_data['sleep_quality'] = data.get('sleepQuality')
            processed_data['sleep_score'] = data.get('sleepScore')
            processed_data['resting_heart_rate_bpm'] = data.get('restingHeartRate')
            processed_data['hrv_baseline'] = data.get('hrvBaseline')
            processed_data['hrv_last_night'] = data.get('hrvLastNight')
            processed_data['body_battery_percent'] = data.get('bodyBattery')
            processed_data['stress_level'] = data.get('stressLevel')
            processed_data['training_load_balance'] = data.get('trainingLoadBalance')
            processed_data['acute_load'] = data.get('acuteLoad')
            processed_data['chronic_load'] = data.get('chronicLoad')
            
        # Health stats data as fallback
        elif 'calendarDate' in data:
            processed_data['date'] = data.get('calendarDate')
            processed_data['resting_heart_rate_bpm'] = data.get('restingHeartRate')
            processed_data['min_heart_rate_bpm'] = data.get('minHeartRate')
            processed_data['max_heart_rate_bpm'] = data.get('maxHeartRate')
            processed_data['average_stress_level'] = data.get('averageStressLevel')
            processed_data['max_stress_level'] = data.get('maxStressLevel')
            processed_data['stress_qualifier'] = data.get('stressQualifier')
            processed_data['body_battery_current'] = data.get('bodyBatteryMostRecentValue')
            processed_data['body_battery_highest'] = data.get('bodyBatteryHighestValue')
            processed_data['body_battery_lowest'] = data.get('bodyBatteryLowestValue')
            processed_data['total_steps'] = data.get('totalSteps')
            processed_data['daily_step_goal'] = data.get('dailyStepGoal')
            processed_data['active_seconds'] = data.get('activeSeconds')
            processed_data['sedentary_seconds'] = data.get('sedentarySeconds')
            processed_data['sleeping_seconds'] = data.get('sleepingSeconds')
            
    # Check if data is training readiness list
    elif isinstance(data, list) and data:
        # Get the most recent entry
        entry = data[0]
        timestamp = entry.get('timestampLocal')
        if timestamp:
            processed_data['timestamp'] = timestamp
            processed_data['date'] = entry.get('calendarDate')
            processed_data['context'] = entry.get('inputContext')
            
            # Overall readiness
            processed_data['level'] = entry.get('level')
            processed_data['score'] = entry.get('score')
            processed_data['feedback'] = entry.get('feedbackShort')
            
            # Contributing factors
            processed_data['sleep_score'] = entry.get('sleepScore')
            processed_data['sleep_factor_percent'] = entry.get('sleepScoreFactorPercent')
            processed_data['sleep_factor_feedback'] = entry.get('sleepScoreFactorFeedback')
            
            processed_data['recovery_time_hours'] = round(entry.get('recoveryTime', 0) / 60, 1) if entry.get('recoveryTime') else None
            processed_data['recovery_factor_percent'] = entry.get('recoveryTimeFactorPercent')
            processed_data['recovery_factor_feedback'] = entry.get('recoveryTimeFactorFeedback')
            
            processed_data['training_load_factor_percent'] = entry.get('acwrFactorPercent')
            processed_data['training_load_feedback'] = entry.get('acwrFactorFeedback')
            processed_data['acute_load'] = entry.get('acuteLoad')
            
            processed_data['hrv_factor_percent'] = entry.get('hrvFactorPercent')
            processed_data['hrv_factor_feedback'] = entry.get('hrvFactorFeedback')
            processed_data['hrv_weekly_avg'] = entry.get('hrvWeeklyAverage')
            
            processed_data['stress_history_factor_percent'] = entry.get('stressHistoryFactorPercent')
            processed_data['stress_history_feedback'] = entry.get('stressHistoryFactorFeedback')
            
            processed_data['sleep_history_factor_percent'] = entry.get('sleepHistoryFactorPercent')
            processed_data['sleep_history_feedback'] = entry.get('sleepHistoryFactorFeedback')
    
    return processed_data

# Process the data
processed_data = process_training_readiness(readiness_data)

# Generate training status report
print("\n" + "="*60)
print("TRAINING STATUS REPORT")
print("="*60)

if processed_data:
    print(f"Date: {processed_data.get('date', yesterday)}")
    print(f"Timestamp: {processed_data.get('timestamp', 'N/A')}")
    print()
    
    # Check if this is morning training readiness data
    if 'readinessScore' in processed_data:
        print("Morning Training Readiness:")
        score = processed_data.get('readinessScore', 'N/A')
        level = processed_data.get('readinessLevel', 'N/A')
        print(f"  Score: {score}/100")
        print(f"  Level: {level}")
        print()
        
        print("Key Metrics:")
        print(f"  Recovery Time: {processed_data.get('recovery_time_hours', 'N/A')} hours")
        print(f"  Sleep Quality: {processed_data.get('sleep_quality', 'N/A')}")
        print(f"  Sleep Score: {processed_data.get('sleep_score', 'N/A')}")
        print(f"  Resting Heart Rate: {processed_data.get('resting_heart_rate_bpm', 'N/A')} BPM")
        print(f"  HRV Status: {processed_data.get('hrv_status', 'N/A')}")
        print(f"  HRV Baseline: {processed_data.get('hrv_baseline', 'N/A')}")
        print(f"  HRV Last Night: {processed_data.get('hrv_last_night', 'N/A')}")
        print(f"  Body Battery: {processed_data.get('body_battery_percent', 'N/A')}%")
        print(f"  Stress Level: {processed_data.get('stress_level', 'N/A')}")
        print(f"  Training Load Balance: {processed_data.get('training_load_balance', 'N/A')}")
        print(f"  Acute Load: {processed_data.get('acute_load', 'N/A')}")
        print(f"  Chronic Load: {processed_data.get('chronic_load', 'N/A')}")
        print()
        
    # Check if this is health stats data
    elif 'resting_heart_rate_bpm' in processed_data:
        print("Health Stats (Training Status Indicators):")
        print(f"  Resting Heart Rate: {processed_data.get('resting_heart_rate_bpm', 'N/A')} BPM")
        print(f"  Heart Rate Range: {processed_data.get('min_heart_rate_bpm', 'N/A')} - {processed_data.get('max_heart_rate_bpm', 'N/A')} BPM")
        print(f"  Stress Level: {processed_data.get('average_stress_level', 'N/A')} (Max: {processed_data.get('max_stress_level', 'N/A')})")
        print(f"  Stress Qualifier: {processed_data.get('stress_qualifier', 'N/A')}")
        print(f"  Body Battery: {processed_data.get('body_battery_current', 'N/A')} (Highest: {processed_data.get('body_battery_highest', 'N/A')}, Lowest: {processed_data.get('body_battery_lowest', 'N/A')})")
        print(f"  Activity: {processed_data.get('total_steps', 'N/A')} steps ({processed_data.get('active_seconds', 'N/A')} seconds active)")
        print(f"  Sleep: {processed_data.get('sleeping_seconds', 'N/A')} seconds")
        print()
        
    # Check if this is regular training readiness data
    else:
        print("Overall Training Readiness:")
        score = processed_data.get('score', 'N/A')
        level = processed_data.get('level', 'N/A')
        feedback = processed_data.get('feedback', 'N/A')
        print(f"  Score: {score}/100")
        print(f"  Level: {level}")
        print(f"  Feedback: {feedback}")
        print()
        
        print("Contributing Factors:")
        
        # Sleep factor
        sleep_score = processed_data.get('sleep_score', 'N/A')
        sleep_factor = processed_data.get('sleep_factor_percent', 'N/A')
        sleep_feedback = processed_data.get('sleep_factor_feedback', 'N/A')
        print(f"  Sleep:")
        print(f"    Score: {sleep_score}")
        print(f"    Factor: {sleep_factor}%")
        print(f"    Feedback: {sleep_feedback}")
        print()
        
        # Recovery time
        recovery_time = processed_data.get('recovery_time_hours', 'N/A')
        recovery_factor = processed_data.get('recovery_factor_percent', 'N/A')
        recovery_feedback = processed_data.get('recovery_factor_feedback', 'N/A')
        print(f"  Recovery:")
        print(f"    Recovery Time: {recovery_time} hours")
        print(f"    Factor: {recovery_factor}%")
        print(f"    Feedback: {recovery_feedback}")
        print()
        
        # Training load
        training_load_factor = processed_data.get('training_load_factor_percent', 'N/A')
        training_load_feedback = processed_data.get('training_load_feedback', 'N/A')
        acute_load = processed_data.get('acute_load', 'N/A')
        print(f"  Training Load:")
        print(f"    Factor: {training_load_factor}%")
        print(f"    Feedback: {training_load_feedback}")
        print(f"    Acute Load: {acute_load}")
        print()
    
    # Analysis and recommendations
    print("="*60)
    print("ANALYSIS & RECOMMENDATIONS")
    print("="*60)
    
    # Get score from whichever field it's in
    score = processed_data.get('readinessScore', processed_data.get('score', 50))
    
    # Based on readiness score
    if score >= 80:
        print("Your training readiness is excellent! You're fully recovered and ready for intense training.")
        print("Recommended: You can safely engage in high-intensity workouts or competitions.")
    elif score >= 60:
        print("Your training readiness is good. You're well-recovered and ready for moderate training.")
        print("Recommended: You can engage in moderate-intensity workouts and continue your training plan.")
    elif score >= 40:
        print("Your training readiness is fair. You're partially recovered but should take it easy.")
        print("Recommended: Focus on light to moderate-intensity workouts and prioritize recovery.")
    else:
        print("Your training readiness is low. You need more recovery time.")
        print("Recommended: Take a rest day or engage in very light activity like walking or yoga.")
    
    # Based on recovery time
    recovery_time = processed_data.get('recovery_time_hours', processed_data.get('recoveryTime', 0))
    if recovery_time and recovery_time > 24:
        print(f"\nNote: Your recovery time is {recovery_time} hours, which is longer than usual.")
        print("This suggests you need more time to fully recover from previous training.")
    
    # Based on sleep score
    sleep_score = processed_data.get('sleep_score', processed_data.get('sleepScore', 70))
    if sleep_score and sleep_score < 70:
        print(f"\nNote: Your sleep score ({sleep_score}) is below optimal.")
        print("Poor sleep can negatively impact your training performance and recovery.")
        print("Consider improving your sleep hygiene for better training results.")
    
    # Based on stress level
    stress_level = processed_data.get('stress_level', processed_data.get('average_stress_level', 30))
    if stress_level and stress_level > 50:
        print(f"\nNote: Your stress level ({stress_level}) is higher than optimal.")
        print("High stress can negatively impact your training performance and recovery.")
        print("Consider incorporating stress management techniques into your routine.")
    
    # Based on body battery
    body_battery = processed_data.get('body_battery_percent', processed_data.get('bodyBatteryMostRecentValue', 50))
    if body_battery and body_battery < 30:
        print(f"\nNote: Your body battery ({body_battery}%) is low.")
        print("A low body battery indicates you need more rest and recovery.")
        print("Recommended: Take a rest day or engage in very light activity.")
    
else:
    print("No training readiness data found.")

# Save data to JSON file
with open('training_status_data.json', 'w', encoding='utf-8') as f:
    json.dump({'training_readiness': processed_data}, f, indent=2, ensure_ascii=False)

print("\nData saved to training_status_data.json")
