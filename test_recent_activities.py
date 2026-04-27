import sys
import os
sys.path.insert(0, 'src')

# Set up Python path and environment variables
os.environ['PYTHONPATH'] = 'src'

from garmin_mcp import init_api
import asyncio

async def main():
    """Test script to get recent activities"""
    print("Testing Garmin MCP activity retrieval...")
    
    # Initialize API with saved tokens
    garmin_client = init_api(None, None, True)  # is_cn=True for China region
    
    if not garmin_client:
        print("Failed to initialize Garmin client")
        return
    
    print("Garmin client initialized successfully")
    
    # Get recent activities
    try:
        print("\nGetting recent activities...")
        activities = garmin_client.get_activities(0, 20)  # Get first 20 activities (newest first)
        
        print(f"Found {len(activities)} activities")
        
        # Filter for running activities
        running_activities = [activity for activity in activities if activity.get('activityType', {}).get('typeKey') == 'running']
        
        print(f"\nFound {len(running_activities)} running activities")
        
        if running_activities:
            # Get the most recent running activity
            most_recent_running = running_activities[0]
            activity_name = most_recent_running.get('activityName', 'Unknown')
            start_time = most_recent_running.get('startTimeLocal', 'Unknown time')
            activity_id = most_recent_running.get('activityId', 'Unknown ID')
            
            print(f"\nMost recent running activity:")
            print(f"Name: {activity_name}")
            print(f"Start time: {start_time}")
            print(f"Activity ID: {activity_id}")
        else:
            print("\nNo running activities found")
            
    except Exception as e:
        print(f"Error getting activities: {e}")

if __name__ == "__main__":
    asyncio.run(main())
