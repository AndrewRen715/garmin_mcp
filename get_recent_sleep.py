import sys
import os
import json
from datetime import datetime, timedelta
sys.path.insert(0, 'src')

# Set up Python path and environment variables
os.environ['PYTHONPATH'] = 'src'

from garmin_mcp import init_api
import asyncio

async def main():
    """Get recent sleep data"""
    print("Getting recent sleep data...")
    
    # Initialize API with saved tokens
    garmin_client = init_api(None, None, True)  # is_cn=True for China region
    
    if not garmin_client:
        print("Failed to initialize Garmin client")
        return
    
    print("Garmin client initialized successfully")
    
    # Calculate date range (last 7 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"\nGetting sleep data from {start_date} to {end_date}")
    
    # Get sleep data for each day
    try:
        sleep_data_list = []
        
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            print(f"\nGetting sleep data for {date}...")
            
            try:
                sleep_data = garmin_client.get_sleep_data(date)
                
                if sleep_data:
                    sleep_data_list.append({
                        'date': date,
                        'data': sleep_data
                    })
                else:
                    print(f"No sleep data found for {date}")
                    
            except Exception as e:
                print(f"Error getting sleep data for {date}: {e}")
        
        if sleep_data_list:
            print("\nAnalyzing sleep data...")
            analyze_sleep_data(sleep_data_list)
        else:
            print("\nNo sleep data found for the last 7 days")
            
    except Exception as e:
        print(f"Error getting sleep data: {e}")
        import traceback
        traceback.print_exc()

def analyze_sleep_data(sleep_data_list):
    """Analyze and display sleep data"""
    print("\n" + "=" * 80)
    print("SLEEP ANALYSIS REPORT")
    print("=" * 80)
    
    total_sleep_days = len(sleep_data_list)
    total_deep_sleep = 0
    total_light_sleep = 0
    total_rem_sleep = 0
    total_awake = 0
    total_sleep_duration = 0
    sleep_quality_scores = []
    
    print("\nRecent Sleep Data:")
    print("-" * 80)
    
    # Sort by date (newest first)
    sleep_data_list.sort(key=lambda x: x['date'], reverse=True)
    
    for item in sleep_data_list:
        date = item['date']
        data = item['data']
        
        # Extract sleep summary
        sleep_summary = data.get('dailySleepDTO', {})
        sleep_time = sleep_summary.get('sleepTimeSeconds', 0)
        deep_sleep = sleep_summary.get('deepSleepSeconds', 0)
        light_sleep = sleep_summary.get('lightSleepSeconds', 0)
        rem_sleep = sleep_summary.get('remSleepSeconds', 0)
        awake = sleep_summary.get('awakeSleepSeconds', 0)
        quality = sleep_summary.get('sleepQuality', 0)
        
        # Convert to hours and minutes
        sleep_hours = sleep_time / 3600
        deep_hours = deep_sleep / 3600
        light_hours = light_sleep / 3600
        rem_hours = rem_sleep / 3600
        awake_hours = awake / 3600
        
        # Accumulate totals
        total_sleep_duration += sleep_hours
        total_deep_sleep += deep_hours
        total_light_sleep += light_hours
        total_rem_sleep += rem_hours
        total_awake += awake_hours
        if quality > 0:
            sleep_quality_scores.append(quality)
        
        # Display daily sleep data
        print(f"\nDate: {date}")
        print(f"Sleep Duration: {sleep_hours:.1f} hours")
        print(f"Deep Sleep: {deep_hours:.1f} hours ({(deep_sleep/sleep_time*100):.1f}%)")
        print(f"Light Sleep: {light_hours:.1f} hours ({(light_sleep/sleep_time*100):.1f}%)")
        print(f"REM Sleep: {rem_hours:.1f} hours ({(rem_sleep/sleep_time*100):.1f}%)")
        print(f"Awake: {awake_hours:.1f} hours ({(awake/sleep_time*100):.1f}%)")
        print(f"Sleep Quality: {quality}/100" if quality > 0 else "Sleep Quality: N/A")
        print("-" * 80)
    
    # Calculate averages
    if total_sleep_days > 0:
        avg_sleep = total_sleep_duration / total_sleep_days
        avg_deep = total_deep_sleep / total_sleep_days
        avg_light = total_light_sleep / total_sleep_days
        avg_rem = total_rem_sleep / total_sleep_days
        avg_awake = total_awake / total_sleep_days
        avg_quality = sum(sleep_quality_scores) / len(sleep_quality_scores) if sleep_quality_scores else 0
        
        print("\n" + "=" * 80)
        print("7-DAY AVERAGE SLEEP STATISTICS")
        print("=" * 80)
        print(f"Average Sleep Duration: {avg_sleep:.1f} hours")
        print(f"Average Deep Sleep: {avg_deep:.1f} hours ({(avg_deep/avg_sleep*100):.1f}%)")
        print(f"Average Light Sleep: {avg_light:.1f} hours ({(avg_light/avg_sleep*100):.1f}%)")
        print(f"Average REM Sleep: {avg_rem:.1f} hours ({(avg_rem/avg_sleep*100):.1f}%)")
        print(f"Average Awake: {avg_awake:.1f} hours ({(avg_awake/avg_sleep*100):.1f}%)")
        print(f"Average Sleep Quality: {avg_quality:.1f}/100" if avg_quality > 0 else "Average Sleep Quality: N/A")
        
        # Sleep quality assessment
        if avg_quality >= 80:
            quality_assessment = "Excellent sleep quality!"
        elif avg_quality >= 70:
            quality_assessment = "Good sleep quality."
        elif avg_quality >= 60:
            quality_assessment = "Fair sleep quality."
        else:
            quality_assessment = "Poor sleep quality."
        
        # Sleep duration assessment
        if avg_sleep >= 7:
            duration_assessment = "Your sleep duration is sufficient."
        elif avg_sleep >= 6:
            duration_assessment = "Your sleep duration is somewhat insufficient."
        else:
            duration_assessment = "Your sleep duration is inadequate."
        
        print("\n" + "=" * 80)
        print("SLEEP ASSESSMENT")
        print("=" * 80)
        print(f"{quality_assessment}")
        print(f"{duration_assessment}")
        
        if avg_sleep < 7:
            print("Recommendation: Try to get 7-9 hours of sleep per night for optimal health.")
        
        if avg_deep < 1.5:
            print("Recommendation: Consider improving sleep hygiene to increase deep sleep time.")
        
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())
