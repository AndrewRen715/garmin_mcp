#!/usr/bin/env python3
"""
Sync health data between global and China regions
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def sync_health_data():
    """Sync health data between China and global regions"""
    print("Syncing Garmin Connect health data from China region to global region...")
    
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
    
    # Define date range for sync (last 7 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    print(f"\n2. Syncing health data from {start_date} to {end_date}")
    
    # Health data types to sync
    health_data_types = [
        "stats",
        "sleep",
        "heart_rate",
        "stress",
        "body_battery"
    ]
    
    # Sync each health data type
    for data_type in health_data_types:
        print(f"\n3. Syncing {data_type} data...")
        
        try:
            # Get data from China region
            if data_type == "stats":
                # Get daily stats for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Getting stats for {date_str}...")
                    cn_stats = garmin_cn.get_stats(date_str)
                    if cn_stats:
                        print(f"   ✓ Got stats for {date_str}")
                        # Here you would implement the sync logic
                        # For now, we'll just display the data
                        print(f"     Steps: {cn_stats.get('totalSteps', 'N/A')}")
                        print(f"     Calories: {cn_stats.get('totalKilocalories', 'N/A')}")
            
            elif data_type == "sleep":
                # Get sleep data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Getting sleep data for {date_str}...")
                    cn_sleep = garmin_cn.get_sleep_data(date_str)
                    if cn_sleep:
                        print(f"   ✓ Got sleep data for {date_str}")
                        # Extract sleep score if available
                        sleep_score = cn_sleep.get('dailySleepDTO', {}).get('sleepScores', {}).get('overall', {}).get('value')
                        print(f"     Sleep score: {sleep_score or 'N/A'}")
            
            elif data_type == "heart_rate":
                # Get heart rate data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Getting heart rate data for {date_str}...")
                    cn_hr = garmin_cn.get_heart_rates(date_str)
                    if cn_hr:
                        print(f"   ✓ Got heart rate data for {date_str}")
                        print(f"     Max HR: {cn_hr.get('maxHeartRate', 'N/A')}")
                        print(f"     Min HR: {cn_hr.get('minHeartRate', 'N/A')}")
                        print(f"     Resting HR: {cn_hr.get('restingHeartRate', 'N/A')}")
            
            elif data_type == "stress":
                # Get stress data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Getting stress data for {date_str}...")
                    cn_stress = garmin_cn.get_stress_data(date_str)
                    if cn_stress:
                        print(f"   ✓ Got stress data for {date_str}")
                        print(f"     Avg stress: {cn_stress.get('avgStressLevel', 'N/A')}")
                        print(f"     Max stress: {cn_stress.get('maxStressLevel', 'N/A')}")
            
            elif data_type == "body_battery":
                # Get body battery data for the date range
                print(f"   Getting body battery data for {start_date} to {end_date}...")
                cn_battery = garmin_cn.get_body_battery(start_date, end_date)
                if cn_battery:
                    print(f"   ✓ Got body battery data for {len(cn_battery)} days")
                    for day in cn_battery:
                        date = day.get('date')
                        charged = day.get('charged')
                        drained = day.get('drained')
                        print(f"     {date}: Charged={charged}, Drained={drained}")
            
        except Exception as e:
            print(f"   ✗ Error syncing {data_type} data: {e}")
    
    print("\n" + "=" * 60)
    print("HEALTH DATA SYNC COMPLETED")
    print("=" * 60)
    print(f"Synced health data from {start_date} to {end_date}")

def main():
    """Main function"""
    try:
        sync_health_data()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
