"""Script to analyze yesterday's training data and heart rate zones"""
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

# Get yesterday's date
today = datetime.now()
yesterday = today - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

print(f"Analyzing training data for {yesterday_str}...")

# Get activities for yesterday
try:
    print("\nGetting activities data...")
    # Get recent activities
    activities = []
    start = 0
    limit = 20
    
    # Get activities with pagination
    while True:
        page = garmin_client.get_activities(start, limit)
        if not page:
            break
        activities.extend(page)
        start += limit
        if len(page) < limit:
            break
    
    # Filter activities for yesterday
    yesterday_activities = []
    for activity in activities:
        start_time = activity.get('startTimeLocal', '')
        if start_time:
            activity_date = start_time.split(' ')[0]
            if activity_date == yesterday_str:
                yesterday_activities.append(activity)
    
    if not yesterday_activities:
        print(f"No activities found for {yesterday_str}")
        sys.exit(1)
    
    print(f"Found {len(yesterday_activities)} activities for {yesterday_str}")
    
    # Get detailed activity data for each activity
    detailed_activities = []
    for activity in yesterday_activities:
        activity_id = activity.get('activityId')
        if activity_id:
            try:
                detailed_activity = garmin_client.get_activity(activity_id)
                detailed_activities.append(detailed_activity)
                print(f"Got details for activity: {activity.get('activityName', 'Unnamed')}")
            except Exception as e:
                print(f"Error getting details for activity {activity_id}: {str(e)}")
    
    if not detailed_activities:
        print("No detailed activity data available")
        sys.exit(1)
    
    # Get health stats for yesterday
    print("\nGetting health stats data...")
    try:
        health_stats = garmin_client.get_stats(yesterday_str)
        print("Got health stats data")
    except Exception as e:
        print(f"Error getting health stats: {str(e)}")
        health_stats = None
    
    # Analyze heart rate zones for each activity
    print("\nAnalyzing heart rate zones...")
    for i, activity in enumerate(detailed_activities):
        # Get summary data from summaryDTO
        summary = activity.get('summaryDTO', {})
        activity_type = activity.get('activityTypeDTO', {})
        
        print(f"\nActivity {i+1}: {activity.get('activityName', 'Unnamed')}")
        print(f"Type: {activity_type.get('typeKey', 'Unknown')}")
        print(f"Duration: {summary.get('duration', 0) // 60} minutes")
        print(f"Distance: {summary.get('distance', 0) / 1000:.2f} km")
        print(f"Average HR: {summary.get('averageHR', 'N/A')} BPM")
        print(f"Max HR: {summary.get('maxHR', 'N/A')} BPM")
        
        # Get heart rate zones data
        hr_zones = summary.get('heartRateZones', [])
        if hr_zones:
            print("\nHeart Rate Zones:")
            for zone in hr_zones:
                zone_num = zone.get('zone', 'N/A')
                min_hr = zone.get('min', 'N/A')
                max_hr = zone.get('max', 'N/A')
                time = zone.get('time', 0) // 60  # Convert to minutes
                print(f"  Zone {zone_num}: {min_hr}-{max_hr} BPM - {time} minutes")
        else:
            print("\nNo heart rate zone data available")
        
        # Calculate training load if available
        training_load = summary.get('activityTrainingLoad', 'N/A')
        if training_load != 'N/A':
            print(f"\nTraining Load: {training_load}")
        
        # Calculate intensity factor if possible
        avg_hr = summary.get('averageHR')
        max_hr = summary.get('maxHR')
        if avg_hr and max_hr:
            intensity_factor = (avg_hr / max_hr) * 100 if max_hr > 0 else 0
            print(f"Intensity Factor: {intensity_factor:.1f}%")
    
    # Generate summary
    print("\n" + "=" * 80)
    print("TRAINING ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Date: {yesterday_str}")
    print(f"Total Activities: {len(yesterday_activities)}")
    
    # Calculate total duration
    total_duration = 0
    total_distance = 0
    total_training_load = 0
    training_load_count = 0
    
    for activity in detailed_activities:
        summary = activity.get('summaryDTO', {})
        total_duration += summary.get('duration', 0)
        total_distance += summary.get('distance', 0)
        tl = summary.get('activityTrainingLoad')
        if tl and tl != 'N/A':
            total_training_load += tl
            training_load_count += 1
    
    print(f"Total Duration: {total_duration // 60} minutes")
    print(f"Total Distance: {total_distance / 1000:.2f} km")
    if training_load_count > 0:
        avg_training_load = total_training_load / training_load_count
        print(f"Average Training Load: {avg_training_load:.1f}")
    
    # Analyze heart rate zones across all activities
    print("\nHEART RATE ZONE ANALYSIS")
    print("-" * 80)
    
    # Combine heart rate zone data from all activities
    combined_zones = {}
    for activity in detailed_activities:
        summary = activity.get('summaryDTO', {})
        hr_zones = summary.get('heartRateZones', [])
        for zone in hr_zones:
            zone_num = zone.get('zone')
            if zone_num:
                if zone_num not in combined_zones:
                    combined_zones[zone_num] = 0
                combined_zones[zone_num] += zone.get('time', 0)
    
    # Sort zones by zone number
    sorted_zones = sorted(combined_zones.items(), key=lambda x: x[0])
    
    total_zone_time = sum(combined_zones.values())
    if total_zone_time > 0:
        for zone_num, time in sorted_zones:
            minutes = time // 60
            percentage = (time / total_zone_time) * 100
            print(f"Zone {zone_num}: {minutes} minutes ({percentage:.1f}%)")
    else:
        print("No heart rate zone data available")
    
    # Generate training status analysis
    print("\nTRAINING STATUS ANALYSIS")
    print("-" * 80)
    
    # Based on heart rate zone distribution
    if combined_zones:
        # Calculate percentage of time in each zone
        zone_1_time = combined_zones.get(1, 0)
        zone_2_time = combined_zones.get(2, 0)
        zone_3_time = combined_zones.get(3, 0)
        zone_4_time = combined_zones.get(4, 0)
        zone_5_time = combined_zones.get(5, 0)
        
        total_time = total_zone_time
        
        zone_1_perc = (zone_1_time / total_time) * 100 if total_time > 0 else 0
        zone_2_perc = (zone_2_time / total_time) * 100 if total_time > 0 else 0
        zone_3_perc = (zone_3_time / total_time) * 100 if total_time > 0 else 0
        zone_4_perc = (zone_4_time / total_time) * 100 if total_time > 0 else 0
        zone_5_perc = (zone_5_time / total_time) * 100 if total_time > 0 else 0
        
        # Analyze training intensity
        if zone_4_perc + zone_5_perc > 30:
            print("Training Intensity: High")
            print("Your training was high intensity, with significant time spent in anaerobic zones.")
            print("This is good for improving speed and VO2 max, but requires adequate recovery.")
        elif zone_3_perc > 40:
            print("Training Intensity: Moderate-High")
            print("Your training was at a moderate-high intensity, mostly in the aerobic threshold zone.")
            print("This is effective for improving aerobic capacity and endurance.")
        elif zone_2_perc > 50:
            print("Training Intensity: Moderate")
            print("Your training was at a moderate intensity, primarily in the aerobic zone.")
            print("This is good for building base endurance and fat-burning capacity.")
        else:
            print("Training Intensity: Low")
            print("Your training was at a low intensity, mostly in the recovery zone.")
            print("This is good for active recovery and improving cardiovascular health.")
    
    # Analyze training load
    if training_load_count > 0:
        avg_tl = total_training_load / training_load_count
        if avg_tl > 300:
            print("\nTraining Load: Very High")
            print("Your training load is very high. Consider taking a rest day to allow for recovery.")
        elif avg_tl > 200:
            print("\nTraining Load: High")
            print("Your training load is high. Ensure you get adequate rest and nutrition.")
        elif avg_tl > 100:
            print("\nTraining Load: Moderate")
            print("Your training load is moderate. This is a good balance for consistent training.")
        else:
            print("\nTraining Load: Low")
            print("Your training load is low. This is suitable for recovery or active rest days.")
    
    # Check health stats for recovery indicators
    if health_stats:
        print("\nRECOVERY INDICATORS")
        print("-" * 80)
        
        # Check resting heart rate
        rhr = health_stats.get('restingHeartRate')
        if rhr:
            print(f"Resting Heart Rate: {rhr} BPM")
            if rhr < 50:
                print("Your resting heart rate is very low, indicating good cardiovascular health.")
            elif rhr < 60:
                print("Your resting heart rate is low, indicating good cardiovascular fitness.")
            elif rhr < 70:
                print("Your resting heart rate is normal.")
            else:
                print("Your resting heart rate is slightly elevated. Ensure you're getting adequate rest.")
        
        # Check body battery
        body_battery = health_stats.get('bodyBatteryMostRecentValue')
        if body_battery:
            print(f"Body Battery: {body_battery}")
            if body_battery < 25:
                print("Your body battery is very low. Consider taking a rest day.")
            elif body_battery < 50:
                print("Your body battery is moderate. Focus on recovery and nutrition.")
            else:
                print("Your body battery is good. You're ready for your next training session.")
    
    # Generate recommendations
    print("\nRECOMMENDATIONS")
    print("-" * 80)
    
    if combined_zones:
        # Based on heart rate zone distribution
        if zone_4_perc + zone_5_perc > 30:
            print("1. Take a rest day or do light active recovery tomorrow")
            print("2. Focus on hydration and nutrition to support recovery")
            print("3. Ensure you get 7-8 hours of sleep tonight")
        elif zone_3_perc > 40:
            print("1. Tomorrow could be a moderate-intensity training day or active recovery")
            print("2. Continue with your regular training plan")
            print("3. Monitor your body's response to training")
        elif zone_2_perc > 50:
            print("1. You're in a good position for your next training session")
            print("2. Consider increasing intensity slightly in your next workout")
            print("3. Maintain consistent training schedule")
        else:
            print("1. Your training was light, suitable for recovery")
            print("2. You can increase intensity in your next workout")
            print("3. Focus on building consistency in your training")
    
    # Based on training load
    if training_load_count > 0:
        avg_tl = total_training_load / training_load_count
        if avg_tl > 200:
            print("4. Reduce training intensity for the next 1-2 days")
            print("5. Consider incorporating yoga or stretching for recovery")
        elif avg_tl < 100:
            print("4. You have room to increase training volume or intensity")
            print("5. Consider adding a higher intensity session to your weekly plan")
    
    # Based on health stats
    if health_stats:
        body_battery = health_stats.get('bodyBatteryMostRecentValue')
        if body_battery and body_battery < 30:
            print("4. Prioritize rest and recovery for the next 24-48 hours")
            print("5. Avoid high-intensity training until body battery improves")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Analysis of your training on {yesterday_str} has been completed.")
    print("Based on your heart rate zones and training load, you have a good understanding")
    print("of your current training status and recovery needs.")
    print("\nRemember to listen to your body and adjust your training plan accordingly.")
    
except Exception as e:
    print(f"Error analyzing training data: {str(e)}")
    import traceback
    traceback.print_exc()
