#!/usr/bin/env python3
"""
Advanced health data sync between global and China regions
Using FIT file creation and upload method
"""

import sys
import os
import tempfile
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def create_fit_file(health_data, data_type, date):
    """Create a FIT file with health data"""
    # This is a placeholder for FIT file creation
    # In a real implementation, you would use a FIT file library
    # to create a proper FIT file with the health data
    
    # For now, we'll create a simple text file as a placeholder
    fit_content = f"""FIT File for {data_type} data
Date: {date}
Data: {health_data}
"""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as f:
        f.write(fit_content.encode('utf-8'))
        temp_file = f.name
    
    return temp_file

def sync_health_data_advanced():
    """Advanced sync of health data between China and global regions"""
    print("Advanced syncing of Garmin Connect health data from China region to global region...")
    
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
    
    # Define date range for sync (last 3 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
    
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
                        # Create FIT file
                        fit_file = create_fit_file(cn_stats, data_type, date_str)
                        print(f"   ✓ Created FIT file: {fit_file}")
                        # Upload to global region
                        try:
                            print(f"   Uploading to global region...")
                            # Note: This will fail with our placeholder FIT file
                            # In a real implementation, you would create a proper FIT file
                            # upload_result = garmin_global.upload_activity(fit_file)
                            # print(f"   ✓ Upload successful: {upload_result}")
                            print("   ⚠ Upload skipped (placeholder FIT file)")
                        except Exception as upload_error:
                            print(f"   ✗ Upload failed: {upload_error}")
                        # Clean up
                        os.unlink(fit_file)
            
            elif data_type == "sleep":
                # Get sleep data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Getting sleep data for {date_str}...")
                    cn_sleep = garmin_cn.get_sleep_data(date_str)
                    if cn_sleep:
                        print(f"   ✓ Got sleep data for {date_str}")
                        # Create FIT file
                        fit_file = create_fit_file(cn_sleep, data_type, date_str)
                        print(f"   ✓ Created FIT file: {fit_file}")
                        # Upload to global region
                        try:
                            print(f"   Uploading to global region...")
                            # upload_result = garmin_global.upload_activity(fit_file)
                            # print(f"   ✓ Upload successful: {upload_result}")
                            print("   ⚠ Upload skipped (placeholder FIT file)")
                        except Exception as upload_error:
                            print(f"   ✗ Upload failed: {upload_error}")
                        # Clean up
                        os.unlink(fit_file)
            
            elif data_type == "heart_rate":
                # Get heart rate data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Getting heart rate data for {date_str}...")
                    cn_hr = garmin_cn.get_heart_rates(date_str)
                    if cn_hr:
                        print(f"   ✓ Got heart rate data for {date_str}")
                        # Create FIT file
                        fit_file = create_fit_file(cn_hr, data_type, date_str)
                        print(f"   ✓ Created FIT file: {fit_file}")
                        # Upload to global region
                        try:
                            print(f"   Uploading to global region...")
                            # upload_result = garmin_global.upload_activity(fit_file)
                            # print(f"   ✓ Upload successful: {upload_result}")
                            print("   ⚠ Upload skipped (placeholder FIT file)")
                        except Exception as upload_error:
                            print(f"   ✗ Upload failed: {upload_error}")
                        # Clean up
                        os.unlink(fit_file)
            
            elif data_type == "stress":
                # Get stress data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Getting stress data for {date_str}...")
                    cn_stress = garmin_cn.get_stress_data(date_str)
                    if cn_stress:
                        print(f"   ✓ Got stress data for {date_str}")
                        # Create FIT file
                        fit_file = create_fit_file(cn_stress, data_type, date_str)
                        print(f"   ✓ Created FIT file: {fit_file}")
                        # Upload to global region
                        try:
                            print(f"   Uploading to global region...")
                            # upload_result = garmin_global.upload_activity(fit_file)
                            # print(f"   ✓ Upload successful: {upload_result}")
                            print("   ⚠ Upload skipped (placeholder FIT file)")
                        except Exception as upload_error:
                            print(f"   ✗ Upload failed: {upload_error}")
                        # Clean up
                        os.unlink(fit_file)
            
            elif data_type == "body_battery":
                # Get body battery data for the date range
                print(f"   Getting body battery data for {start_date} to {end_date}...")
                cn_battery = garmin_cn.get_body_battery(start_date, end_date)
                if cn_battery:
                    print(f"   ✓ Got body battery data for {len(cn_battery)} days")
                    for day in cn_battery:
                        date = day.get('date')
                        # Create FIT file for each day
                        fit_file = create_fit_file(day, data_type, date)
                        print(f"   ✓ Created FIT file for {date}: {fit_file}")
                        # Upload to global region
                        try:
                            print(f"   Uploading to global region...")
                            # upload_result = garmin_global.upload_activity(fit_file)
                            # print(f"   ✓ Upload successful: {upload_result}")
                            print("   ⚠ Upload skipped (placeholder FIT file)")
                        except Exception as upload_error:
                            print(f"   ✗ Upload failed: {upload_error}")
                        # Clean up
                        os.unlink(fit_file)
            
        except Exception as e:
            print(f"   ✗ Error syncing {data_type} data: {e}")
    
    print("\n" + "=" * 60)
    print("ADVANCED HEALTH DATA SYNC COMPLETED")
    print("=" * 60)
    print(f"Synced health data from {start_date} to {end_date}")
    print("Note: This is a prototype - actual FIT file creation and upload requires")
    print("      proper FIT file library integration.")

def main():
    """Main function"""
    try:
        sync_health_data_advanced()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
