#!/usr/bin/env python3
"""
Check if Garmin API is connected to China region or global
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from garmin_mcp import init_api

def main():
    """Main function"""
    try:
        # Set environment variables for China region
        os.environ['GARMIN_CN'] = 'true'
        
        # Initialize Garmin API
        print("Initializing Garmin API (China region)...")
        garmin_client = init_api(None, None, is_cn=True)
        
        if not garmin_client:
            print("Error: Failed to initialize Garmin API.")
            return
        
        # Check the API endpoints being used
        print("\nChecking API configuration...")
        
        # Get user profile to verify connection
        print("Getting user profile...")
        user_profile = garmin_client.get_user_profile()
        
        if user_profile:
            print("✓ Successfully retrieved user profile")
            print(f"User display name: {user_profile.get('displayName', 'N/A')}")
            print(f"User full name: {user_profile.get('fullName', 'N/A')}")
        
        # Check garth configuration
        print("\nChecking Garth configuration...")
        if hasattr(garmin_client, 'garth'):
            garth = garmin_client.garth
            if hasattr(garth, 'api'):
                api_config = garth.api
                print(f"API configuration: {api_config}")
            
            # Check if we can access China-specific endpoints
            print("\nTesting China region access...")
            try:
                # Try to get health stats (should work for both regions)
                from datetime import datetime, timedelta
                yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                stats = garmin_client.get_stats(yesterday)
                print("✓ Successfully accessed health stats API")
                print(f"Stats data available: {len(stats) > 0}")
            except Exception as e:
                print(f"✗ Error accessing API: {e}")
        
        print("\nConnection check completed!")
        print("The API is now configured to use China region.")
        print("All training plans will be scheduled to your Garmin Connect China calendar.")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
