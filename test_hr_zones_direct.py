#!/usr/bin/env python3
"""Test script to check if garminconnect library supports getting user's heart rate zones"""

import os
import sys
import json
from garminconnect import Garmin

# Get credentials from environment variables
email = os.environ.get("GARMIN_EMAIL")
password = os.environ.get("GARMIN_PASSWORD")
is_cn = os.environ.get("GARMIN_CN", "false").lower() == "true"
tokenstore = "~/.garminconnect"

if not email or not password:
    print("Error: Please set GARMIN_EMAIL and GARMIN_PASSWORD environment variables")
    sys.exit(1)

# Initialize Garmin client
print("Initializing Garmin client...")
try:
    garmin_client = Garmin(email=email, password=password, is_cn=is_cn)
    garmin_client.login()
    print("Garmin client initialized successfully")
except Exception as e:
    print(f"Error: Failed to initialize Garmin client: {str(e)}")
    sys.exit(1)

print("\nTesting heart rate zone related methods...")
print("=" * 80)

# Check if the client has methods related to heart rate zones
client_methods = [method for method in dir(garmin_client) if not method.startswith('_')]

print("\nAvailable methods in Garmin client:")
for method in sorted(client_methods):
    if 'zone' in method.lower() or 'hr' in method.lower() or 'heart' in method.lower():
        print(f"  - {method}")

print("\n" + "=" * 80)

# Try to get user profile to see if it contains HR zone settings
print("\nTrying to get user profile...")
try:
    user_profile = garmin_client.get_user_profile()
    if user_profile:
        print("User profile obtained successfully")
        # Save user profile to file for inspection
        with open('user_profile.json', 'w', encoding='utf-8') as f:
            json.dump(user_profile, f, indent=2, ensure_ascii=False)
        print("User profile saved to user_profile.json")
        
        # Check if user profile contains HR zone settings
        if 'userSettings' in user_profile:
            user_settings = user_profile['userSettings']
            print("\nChecking user settings for HR zones...")
            for key, value in user_settings.items():
                if 'zone' in key.lower() or 'hr' in key.lower() or 'heart' in key.lower():
                    print(f"  {key}: {value}")
    else:
        print("No user profile data returned")
except Exception as e:
    print(f"Error getting user profile: {str(e)}")

print("\n" + "=" * 80)

# Try to get user profile settings
try:
    user_settings = garmin_client.get_userprofile_settings()
    if user_settings:
        print("User profile settings obtained successfully")
        # Save to file for inspection
        with open('user_profile_settings.json', 'w', encoding='utf-8') as f:
            json.dump(user_settings, f, indent=2, ensure_ascii=False)
        print("User profile settings saved to user_profile_settings.json")
    else:
        print("No user profile settings returned")
except Exception as e:
    print(f"Error getting user profile settings: {str(e)}")

print("\n" + "=" * 80)

# Try to get a recent activity to see if it contains HR zone information
try:
    print("\nTrying to get recent activities...")
    activities = garmin_client.get_activities(0, 5)
    if activities:
        print(f"Got {len(activities)} recent activities")
        
        # Get the first activity
        activity = activities[0]
        activity_id = activity.get('activityId')
        activity_name = activity.get('activityName')
        
        print(f"\nTrying to get HR zones for activity: {activity_name} (ID: {activity_id})")
        
        # Try to get HR zones for this activity
        try:
            hr_zones = garmin_client.get_activity_hr_in_timezones(activity_id)
            if hr_zones:
                print("HR zones data obtained successfully")
                # Save to file for inspection
                with open('activity_hr_zones.json', 'w', encoding='utf-8') as f:
                    json.dump(hr_zones, f, indent=2, ensure_ascii=False)
                print("HR zones data saved to activity_hr_zones.json")
            else:
                print("No HR zones data returned")
        except Exception as e:
            print(f"Error getting HR zones for activity: {str(e)}")
    else:
        print("No activities found")
except Exception as e:
    print(f"Error getting activities: {str(e)}")

print("\n" + "=" * 80)
print("Test completed. Check the generated JSON files for more details.")
