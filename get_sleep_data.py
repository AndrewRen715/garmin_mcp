"""Script to get sleep data for a specific date"""
import json
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from garmin_mcp import init_api

# Set environment variables
os.environ['GARMIN_CN'] = 'true'

# Initialize Garmin API with empty credentials (will use saved tokens)
print("Initializing Garmin API...")
garmin_client = init_api(None, None, is_cn=True)

if not garmin_client:
    print("Error: Failed to initialize Garmin API.")
    sys.exit(1)

# Get sleep data for last night (2026-02-08)
date = "2026-02-08"
print(f"Getting sleep data for {date}...")

# Get sleep data directly from garmin_client
sleep_data = garmin_client.get_sleep_data(date)

# Process sleep data to get a summary
def get_sleep_summary(sleep_data):
    """Process sleep data to get a summary"""
    if not sleep_data:
        return "No sleep data found"
    
    # Extract only essential summary metrics
    summary = {}
    
    # Extract data from dailySleepDTO if available
    daily_sleep = sleep_data.get('dailySleepDTO', {})
    if daily_sleep:
        # Sleep duration and timing
        summary['sleep_seconds'] = daily_sleep.get('sleepTimeSeconds')
        summary['nap_seconds'] = daily_sleep.get('napTimeSeconds')
        summary['sleep_start'] = daily_sleep.get('sleepStartTimestampGMT')
        summary['sleep_end'] = daily_sleep.get('sleepEndTimestampGMT')
        
        # Sleep score and quality
        summary['sleep_score'] = daily_sleep.get('sleepScores', {}).get('overall', {}).get('value')
        summary['sleep_score_qualifier'] = daily_sleep.get('sleepScores', {}).get('overall', {}).get('qualifierKey')
        
        # Sleep phases (in seconds)
        summary['deep_sleep_seconds'] = daily_sleep.get('deepSleepSeconds')
        summary['light_sleep_seconds'] = daily_sleep.get('lightSleepSeconds')
        summary['rem_sleep_seconds'] = daily_sleep.get('remSleepSeconds')
        summary['awake_seconds'] = daily_sleep.get('awakeSleepSeconds')
        
        # Sleep disruptions
        summary['awake_count'] = daily_sleep.get('awakeCount')
        summary['restless_moments_count'] = daily_sleep.get('restlessMomentsCount')
        
        # Average physiological metrics
        summary['avg_sleep_stress'] = daily_sleep.get('avgSleepStress')
        summary['resting_heart_rate_bpm'] = daily_sleep.get('restingHeartRate')
    
    # Extract SpO2 summary if available
    spo2_summary = sleep_data.get('wellnessSpO2SleepSummaryDTO', {})
    if spo2_summary:
        summary['avg_spo2_percent'] = spo2_summary.get('averageSpo2')
        summary['lowest_spo2_percent'] = spo2_summary.get('lowestSpo2')
    
    # Add HRV data if available at top level
    if 'avgOvernightHrv' in sleep_data:
        summary['avg_overnight_hrv'] = sleep_data.get('avgOvernightHrv')
    
    # Calculate sleep phase percentages if total sleep time is available
    total_sleep = summary.get('sleep_seconds', 0)
    if total_sleep and total_sleep > 0:
        summary['deep_sleep_percent'] = round((summary.get('deep_sleep_seconds', 0) / total_sleep) * 100, 1)
        summary['light_sleep_percent'] = round((summary.get('light_sleep_seconds', 0) / total_sleep) * 100, 1)
        summary['rem_sleep_percent'] = round((summary.get('rem_sleep_seconds', 0) / total_sleep) * 100, 1)
    
    # Convert sleep duration to hours for convenience
    if total_sleep:
        summary['sleep_hours'] = round(total_sleep / 3600, 2)
    
    # Remove None values
    summary = {k: v for k, v in summary.items() if v is not None}
    
    return json.dumps(summary, indent=2)

# Process the sleep data
sleep_summary = get_sleep_summary(sleep_data)

print("\nSleep Summary:")
print(sleep_summary)
