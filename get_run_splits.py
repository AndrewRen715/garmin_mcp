import sys
import os
import json
sys.path.insert(0, 'src')

# Set up Python path and environment variables
os.environ['PYTHONPATH'] = 'src'

from garmin_mcp import init_api
import asyncio

async def main():
    """Get splits for the most recent running activity"""
    print("Getting splits for the most recent running activity...")
    
    # Initialize API with saved tokens
    garmin_client = init_api(None, None, True)  # is_cn=True for China region
    
    if not garmin_client:
        print("Failed to initialize Garmin client")
        return
    
    print("Garmin client initialized successfully")
    
    # Most recent running activity ID (from previous test)
    activity_id = 564291593
    
    # Get activity splits
    try:
        print(f"\nGetting splits for activity ID: {activity_id}")
        splits_data = garmin_client.get_activity_splits(activity_id)
        
        if not splits_data:
            print("No splits data found for this activity")
            return
        
        # Extract lap data
        laps = splits_data.get('lapDTOs', [])
        
        print(f"\nFound {len(laps)} laps for this activity")
        
        if laps:
            print("\nSplit details:")
            print("=" * 80)
            
            total_distance = 0
            total_duration = 0
            
            for i, lap in enumerate(laps, 1):
                distance = lap.get('distance', 0) / 1000  # Convert to kilometers
                duration = lap.get('duration', 0) / 60      # Convert to minutes
                avg_speed = lap.get('averageSpeed', 0) * 3.6  # Convert to km/h
                avg_hr = lap.get('averageHR', 0)
                
                total_distance += distance
                total_duration += duration
                
                print(f"Lap {i}:")
                print(f"  Distance: {distance:.2f} km")
                print(f"  Duration: {duration:.2f} min")
                print(f"  Avg Pace: {60/avg_speed:.2f} min/km" if avg_speed > 0 else "  Avg Pace: N/A")
                print(f"  Avg Speed: {avg_speed:.2f} km/h" if avg_speed > 0 else "  Avg Speed: N/A")
                print(f"  Avg HR: {avg_hr} bpm" if avg_hr > 0 else "  Avg HR: N/A")
                print("-" * 80)
            
            # Print summary
            print("\nActivity Summary:")
            print("=" * 80)
            print(f"Total Distance: {total_distance:.2f} km")
            print(f"Total Duration: {total_duration:.2f} min")
            print(f"Overall Avg Pace: {total_duration/total_distance:.2f} min/km" if total_distance > 0 else "Overall Avg Pace: N/A")
            print(f"Overall Avg Speed: {total_distance/(total_duration/60):.2f} km/h" if total_duration > 0 else "Overall Avg Speed: N/A")
            print("=" * 80)
            
        else:
            print("No lap data found in splits")
            
    except Exception as e:
        print(f"Error getting activity splits: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
