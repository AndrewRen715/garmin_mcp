import sys
import os
import json
from datetime import datetime, timedelta
sys.path.insert(0, 'src')

# Set up Python path and environment variables
os.environ['PYTHONPATH'] = 'src'

import asyncio

async def main():
    """Test sleep data tools"""
    print("Testing sleep data tools...")
    
    # Initialize API with saved tokens
    from garmin_mcp import init_api
    garmin_client = init_api(None, None, True)
    
    if not garmin_client:
        print("Failed to initialize Garmin client")
        return
    
    print("Garmin client initialized successfully")
    
    # Get today's date and yesterday's date
    today = datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    print(f"\nGetting sleep data for: {yesterday}")
    print("-" * 80)
    
    # Get sleep data directly from the client
    try:
        print("\nGetting sleep data...")
        sleep_data = garmin_client.get_sleep_data(yesterday)
        
        if not sleep_data:
            print(f"No sleep data found for {yesterday}")
            return
        
        print("Sleep data retrieved successfully")
        
        # Extract sleep summary
        daily_sleep = sleep_data.get('dailySleepDTO', {})
        
        if daily_sleep:
            print("\nSleep Summary:")
            print("=" * 60)
            
            # Sleep duration
            sleep_time = daily_sleep.get('sleepTimeSeconds', 0)
            sleep_hours = sleep_time / 3600
            print(f"Sleep Duration: {sleep_hours:.1f} hours")
            
            # Sleep phases
            deep_sleep = daily_sleep.get('deepSleepSeconds', 0) / 3600
            light_sleep = daily_sleep.get('lightSleepSeconds', 0) / 3600
            rem_sleep = daily_sleep.get('remSleepSeconds', 0) / 3600
            awake = daily_sleep.get('awakeSleepSeconds', 0) / 3600
            
            print(f"Deep Sleep: {deep_sleep:.1f} hours ({(deep_sleep/sleep_hours*100):.1f}%)")
            print(f"Light Sleep: {light_sleep:.1f} hours ({(light_sleep/sleep_hours*100):.1f}%)")
            print(f"REM Sleep: {rem_sleep:.1f} hours ({(rem_sleep/sleep_hours*100):.1f}%)")
            print(f"Awake: {awake:.1f} hours ({(awake/sleep_hours*100):.1f}%)")
            
            # Sleep start and end
            sleep_start = daily_sleep.get('sleepStartTimestampGMT')
            sleep_end = daily_sleep.get('sleepEndTimestampGMT')
            
            if sleep_start:
                print(f"Sleep Start: {sleep_start}")
            if sleep_end:
                print(f"Sleep End: {sleep_end}")
            
            # Sleep quality
            sleep_quality = daily_sleep.get('sleepQuality', 0)
            print(f"Sleep Quality: {sleep_quality}/100")
            
            # Sleep disruptions
            awake_count = daily_sleep.get('awakeCount', 0)
            restless_count = daily_sleep.get('restlessMomentsCount', 0)
            print(f"Awake Count: {awake_count}")
            print(f"Restless Moments: {restless_count}")
            
            print("=" * 60)
        else:
            print("No daily sleep data found")
            
    except Exception as e:
        print(f"Error getting sleep data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
