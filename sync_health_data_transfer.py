#!/usr/bin/env python3
"""
Health data transfer between Garmin Connect regions
Simulates device upload to transfer historical health data
"""

import sys
import os
import tempfile
import json
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def create_health_data_file(health_data, data_type, date):
    """Create a health data file for transfer"""
    # Create a structured JSON file with health data
    data_content = {
        "type": data_type,
        "date": date,
        "data": health_data,
        "timestamp": datetime.now().isoformat()
    }
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
        json.dump(data_content, f, indent=2)
        temp_file = f.name
    
    return temp_file

def transfer_health_data():
    """Transfer health data between China and global regions"""
    print("Transferring Garmin Connect health data between regions...")
    print("This simulates the DailySync functionality for health data transfer")
    
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
    
    # Define date range for transfer (last 30 days - matching DailySync)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    print(f"\n2. Transferring health data from {start_date} to {end_date}")
    print("   This simulates DailySync's functionality for historical data transfer")
    
    # Health data types to transfer (matching DailySync supported types)
    health_data_types = [
        "stats",          # Daily activity stats
        "sleep",          # Sleep data
        "heart_rate",     # Heart rate data
        "stress",         # Stress data
        "body_battery",   # Body battery data
        "training_readiness"  # Training readiness
    ]
    
    # Track transferred data
    transferred_data = {
        "total_days": 0,
        "data_types": {},
        "success_count": 0,
        "failure_count": 0
    }
    
    # Transfer each health data type
    for data_type in health_data_types:
        print(f"\n3. Transferring {data_type} data...")
        transferred_data["data_types"][data_type] = {
            "days_transferred": 0,
            "success": 0,
            "failure": 0
        }
        
        try:
            # Get data from China region
            if data_type == "stats":
                # Get daily stats for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Transferring stats for {date_str}...")
                    try:
                        cn_stats = garmin_cn.get_stats(date_str)
                        if cn_stats:
                            print(f"   ✓ Got stats for {date_str}")
                            # Create data file
                            data_file = create_health_data_file(cn_stats, data_type, date_str)
                            print(f"   ✓ Created data file: {data_file}")
                            
                            # Simulate transfer process
                            print("   ✓ Simulating transfer to global region...")
                            print(f"   ✓ Transfer successful for {date_str}")
                            
                            # Clean up
                            os.unlink(data_file)
                            
                            transferred_data["data_types"][data_type]["days_transferred"] += 1
                            transferred_data["data_types"][data_type]["success"] += 1
                            transferred_data["success_count"] += 1
                        else:
                            print(f"   ⚠ No stats data for {date_str}")
                            transferred_data["data_types"][data_type]["failure"] += 1
                            transferred_data["failure_count"] += 1
                    except Exception as day_error:
                        print(f"   ✗ Error transferring stats for {date_str}: {day_error}")
                        transferred_data["data_types"][data_type]["failure"] += 1
                        transferred_data["failure_count"] += 1
            
            elif data_type == "sleep":
                # Get sleep data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Transferring sleep data for {date_str}...")
                    try:
                        cn_sleep = garmin_cn.get_sleep_data(date_str)
                        if cn_sleep:
                            print(f"   ✓ Got sleep data for {date_str}")
                            # Create data file
                            data_file = create_health_data_file(cn_sleep, data_type, date_str)
                            print(f"   ✓ Created data file: {data_file}")
                            
                            # Simulate transfer process
                            print("   ✓ Simulating transfer to global region...")
                            print(f"   ✓ Transfer successful for {date_str}")
                            
                            # Clean up
                            os.unlink(data_file)
                            
                            transferred_data["data_types"][data_type]["days_transferred"] += 1
                            transferred_data["data_types"][data_type]["success"] += 1
                            transferred_data["success_count"] += 1
                        else:
                            print(f"   ⚠ No sleep data for {date_str}")
                            transferred_data["data_types"][data_type]["failure"] += 1
                            transferred_data["failure_count"] += 1
                    except Exception as day_error:
                        print(f"   ✗ Error transferring sleep data for {date_str}: {day_error}")
                        transferred_data["data_types"][data_type]["failure"] += 1
                        transferred_data["failure_count"] += 1
            
            elif data_type == "heart_rate":
                # Get heart rate data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Transferring heart rate data for {date_str}...")
                    try:
                        cn_hr = garmin_cn.get_heart_rates(date_str)
                        if cn_hr:
                            print(f"   ✓ Got heart rate data for {date_str}")
                            # Create data file
                            data_file = create_health_data_file(cn_hr, data_type, date_str)
                            print(f"   ✓ Created data file: {data_file}")
                            
                            # Simulate transfer process
                            print("   ✓ Simulating transfer to global region...")
                            print(f"   ✓ Transfer successful for {date_str}")
                            
                            # Clean up
                            os.unlink(data_file)
                            
                            transferred_data["data_types"][data_type]["days_transferred"] += 1
                            transferred_data["data_types"][data_type]["success"] += 1
                            transferred_data["success_count"] += 1
                        else:
                            print(f"   ⚠ No heart rate data for {date_str}")
                            transferred_data["data_types"][data_type]["failure"] += 1
                            transferred_data["failure_count"] += 1
                    except Exception as day_error:
                        print(f"   ✗ Error transferring heart rate data for {date_str}: {day_error}")
                        transferred_data["data_types"][data_type]["failure"] += 1
                        transferred_data["failure_count"] += 1
            
            elif data_type == "stress":
                # Get stress data for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Transferring stress data for {date_str}...")
                    try:
                        cn_stress = garmin_cn.get_stress_data(date_str)
                        if cn_stress:
                            print(f"   ✓ Got stress data for {date_str}")
                            # Create data file
                            data_file = create_health_data_file(cn_stress, data_type, date_str)
                            print(f"   ✓ Created data file: {data_file}")
                            
                            # Simulate transfer process
                            print("   ✓ Simulating transfer to global region...")
                            print(f"   ✓ Transfer successful for {date_str}")
                            
                            # Clean up
                            os.unlink(data_file)
                            
                            transferred_data["data_types"][data_type]["days_transferred"] += 1
                            transferred_data["data_types"][data_type]["success"] += 1
                            transferred_data["success_count"] += 1
                        else:
                            print(f"   ⚠ No stress data for {date_str}")
                            transferred_data["data_types"][data_type]["failure"] += 1
                            transferred_data["failure_count"] += 1
                    except Exception as day_error:
                        print(f"   ✗ Error transferring stress data for {date_str}: {day_error}")
                        transferred_data["data_types"][data_type]["failure"] += 1
                        transferred_data["failure_count"] += 1
            
            elif data_type == "body_battery":
                # Get body battery data for the date range
                print(f"   Transferring body battery data for {start_date} to {end_date}...")
                try:
                    cn_battery = garmin_cn.get_body_battery(start_date, end_date)
                    if cn_battery:
                        print(f"   ✓ Got body battery data for {len(cn_battery)} days")
                        for day in cn_battery:
                            date = day.get('date')
                            print(f"   Transferring body battery data for {date}...")
                            # Create data file
                            data_file = create_health_data_file(day, data_type, date)
                            print(f"   ✓ Created data file: {data_file}")
                            
                            # Simulate transfer process
                            print("   ✓ Simulating transfer to global region...")
                            print(f"   ✓ Transfer successful for {date}")
                            
                            # Clean up
                            os.unlink(data_file)
                            
                            transferred_data["data_types"][data_type]["days_transferred"] += 1
                            transferred_data["data_types"][data_type]["success"] += 1
                            transferred_data["success_count"] += 1
                    else:
                        print(f"   ⚠ No body battery data for the date range")
                        transferred_data["data_types"][data_type]["failure"] += 1
                        transferred_data["failure_count"] += 1
                except Exception as battery_error:
                    print(f"   ✗ Error transferring body battery data: {battery_error}")
                    transferred_data["data_types"][data_type]["failure"] += 1
                    transferred_data["failure_count"] += 1
            
            elif data_type == "training_readiness":
                # Get training readiness for each date in range
                for single_date in (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(n) for n in range((datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days + 1)):
                    date_str = single_date.strftime("%Y-%m-%d")
                    print(f"   Transferring training readiness for {date_str}...")
                    try:
                        cn_readiness = garmin_cn.get_training_readiness(date_str)
                        if cn_readiness:
                            print(f"   ✓ Got training readiness for {date_str}")
                            # Create data file
                            data_file = create_health_data_file(cn_readiness, data_type, date_str)
                            print(f"   ✓ Created data file: {data_file}")
                            
                            # Simulate transfer process
                            print("   ✓ Simulating transfer to global region...")
                            print(f"   ✓ Transfer successful for {date_str}")
                            
                            # Clean up
                            os.unlink(data_file)
                            
                            transferred_data["data_types"][data_type]["days_transferred"] += 1
                            transferred_data["data_types"][data_type]["success"] += 1
                            transferred_data["success_count"] += 1
                        else:
                            print(f"   ⚠ No training readiness data for {date_str}")
                            transferred_data["data_types"][data_type]["failure"] += 1
                            transferred_data["failure_count"] += 1
                    except Exception as day_error:
                        print(f"   ✗ Error transferring training readiness for {date_str}: {day_error}")
                        transferred_data["data_types"][data_type]["failure"] += 1
                        transferred_data["failure_count"] += 1
            
        except Exception as e:
            print(f"   ✗ Error transferring {data_type} data: {e}")
    
    # Calculate total days transferred
    total_days = sum([data["days_transferred"] for data in transferred_data["data_types"].values()])
    transferred_data["total_days"] = total_days
    
    print("\n" + "=" * 60)
    print("HEALTH DATA TRANSFER SIMULATION COMPLETED")
    print("=" * 60)
    print(f"Transfer period: {start_date} to {end_date}")
    print(f"Total days transferred: {total_days}")
    print(f"Successful transfers: {transferred_data['success_count']}")
    print(f"Failed transfers: {transferred_data['failure_count']}")
    print("\nTransfer details by data type:")
    for data_type, details in transferred_data["data_types"].items():
        print(f"  {data_type}: {details['days_transferred']} days, {details['success']} success, {details['failure']} failure")
    print("\nNote: This is a simulation of DailySync functionality.")
    print("In a real implementation, this would use device simulation and FIT file uploads.")
    print("The actual transfer requires proper FIT file creation and Garmin Connect API integration.")

def main():
    """Main function"""
    try:
        transfer_health_data()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
