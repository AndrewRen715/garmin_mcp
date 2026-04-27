"""Script to get sleep data for the last week"""
import json
import os
import sys
from datetime import datetime, timedelta

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

# Get date range for the last week
today = datetime.now()
end_date = today - timedelta(days=1)  # Yesterday
start_date = end_date - timedelta(days=6)  # 7 days ago

print(f"Getting sleep data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

# Process sleep data to get a summary
def process_sleep_data(sleep_data, date):
    """Process sleep data to get a summary"""
    if not sleep_data:
        return None
    
    # Extract only essential summary metrics
    summary = {'date': date}
    
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
    
    return summary

# Get sleep data for each day in the range
sleep_data_list = []
current_date = start_date

while current_date <= end_date:
    date_str = current_date.strftime('%Y-%m-%d')
    print(f"Getting sleep data for {date_str}...")
    
    try:
        sleep_data = garmin_client.get_sleep_data(date_str)
        processed_data = process_sleep_data(sleep_data, date_str)
        if processed_data:
            sleep_data_list.append(processed_data)
            print(f"✓ Successfully retrieved data for {date_str}")
        else:
            print(f"✗ No sleep data found for {date_str}")
    except Exception as e:
        print(f"✗ Error retrieving data for {date_str}: {str(e)}")
    
    current_date += timedelta(days=1)

# Calculate weekly averages
def calculate_weekly_averages(data_list):
    """Calculate weekly averages from sleep data"""
    if not data_list:
        return None
    
    averages = {}
    keys = ['sleep_hours', 'sleep_score', 'deep_sleep_percent', 'light_sleep_percent', 'rem_sleep_percent', 
            'awake_count', 'avg_sleep_stress', 'avg_overnight_hrv', 'resting_heart_rate_bpm']
    
    for key in keys:
        values = [item.get(key) for item in data_list if item.get(key) is not None]
        if values:
            averages[key] = round(sum(values) / len(values), 2)
    
    return averages

# Calculate weekly averages
weekly_averages = calculate_weekly_averages(sleep_data_list)

# Generate weekly summary
print("\n" + "="*60)
print("WEEKLY SLEEP SUMMARY")
print("="*60)
print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
print(f"Days with Data: {len(sleep_data_list)}")
print()

if weekly_averages:
    print("Weekly Averages:")
    print(f"  Average Sleep Duration: {weekly_averages.get('sleep_hours', 'N/A')} hours")
    print(f"  Average Sleep Score: {weekly_averages.get('sleep_score', 'N/A')}")
    print(f"  Average Sleep Phases:")
    print(f"    Deep Sleep: {weekly_averages.get('deep_sleep_percent', 'N/A')}%")
    print(f"    Light Sleep: {weekly_averages.get('light_sleep_percent', 'N/A')}%")
    print(f"    REM Sleep: {weekly_averages.get('rem_sleep_percent', 'N/A')}%")
    print(f"  Average Awakenings: {weekly_averages.get('awake_count', 'N/A')}")
    print(f"  Average Sleep Stress: {weekly_averages.get('avg_sleep_stress', 'N/A')}")
    print(f"  Average Overnight HRV: {weekly_averages.get('avg_overnight_hrv', 'N/A')}")
    print(f"  Average Resting Heart Rate: {weekly_averages.get('resting_heart_rate_bpm', 'N/A')} BPM")
else:
    print("No sufficient data to calculate weekly averages.")

print()
print("Daily Sleep Data:")
print("-"*60)

for data in sleep_data_list:
    print(f"Date: {data.get('date')}")
    print(f"  Sleep Duration: {data.get('sleep_hours', 'N/A')} hours")
    print(f"  Sleep Score: {data.get('sleep_score', 'N/A')} ({data.get('sleep_score_qualifier', 'N/A')})")
    print(f"  Sleep Phases: Deep={data.get('deep_sleep_percent', 'N/A')}%, Light={data.get('light_sleep_percent', 'N/A')}%, REM={data.get('rem_sleep_percent', 'N/A')}%")
    print(f"  Awakenings: {data.get('awake_count', 'N/A')}")
    print()

# Save data to JSON file
with open('weekly_sleep_data.json', 'w', encoding='utf-8') as f:
    json.dump({'weekly_averages': weekly_averages, 'daily_data': sleep_data_list}, f, indent=2, ensure_ascii=False)

print("\nData saved to weekly_sleep_data.json")
