"""Script to analyze training data for the past month"""
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

# Get date range for the past month
today = datetime.now()
end_date = today - timedelta(days=1)  # Yesterday
start_date = end_date - timedelta(days=29)  # 30 days ago

print(f"Getting training data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")

# Get activities data
try:
    print("Getting activities data...")
    # Get activities with pagination support
    activities = []
    start = 0
    limit = 20
    max_retries = 3
    retry_count = 0
    
    # Convert start_date and end_date to strings for comparison
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    while True:
        try:
            page = garmin_client.get_activities(start, limit)
            if not page:
                break
            
            # Filter activities to only include those within the date range
            filtered_page = []
            for activity in page:
                start_time = activity.get('startTimeLocal', '')
                if start_time:
                    activity_date = start_time.split(' ')[0]
                    if start_date_str <= activity_date <= end_date_str:
                        filtered_page.append(activity)
            
            activities.extend(filtered_page)
            
            # If we've reached the end of activities or no more in date range
            if len(page) < limit:
                break
            
            # Check if we've gone beyond the start date
            if filtered_page:
                oldest_activity = min(filtered_page, key=lambda x: x.get('startTimeLocal', ''))
                oldest_date = oldest_activity.get('startTimeLocal', '').split(' ')[0]
                if oldest_date < start_date_str:
                    break
            
            start += limit
            retry_count = 0  # Reset retry count after successful request
        except Exception as e:
            retry_count += 1
            if retry_count > max_retries:
                print(f"✗ Error retrieving activities data after {max_retries} retries: {str(e)}")
                # Continue with available data instead of exiting
                break
            print(f"⚠️  Network error, retrying ({retry_count}/{max_retries})...")
            import time
            time.sleep(2)  # Wait 2 seconds before retrying
    
    print(f"✓ Successfully retrieved {len(activities)} activities within the date range")
except Exception as e:
    print(f"✗ Error retrieving activities data: {str(e)}")
    # Continue with empty activities instead of exiting
    activities = []

# Get health stats data for each day
def get_health_stats_for_date(date_str):
    """Get health stats for a specific date"""
    try:
        stats = garmin_client.get_stats(date_str)
        return stats
    except Exception as e:
        print(f"✗ Error retrieving health stats for {date_str}: {str(e)}")
        return None

# Get health stats for each day in the range
print("\nGetting health stats data for each day...")
health_stats = {}
current_date = start_date
processed_days = 0

while current_date <= end_date:
    date_str = current_date.strftime('%Y-%m-%d')
    print(f"Getting health stats for {date_str}...")
    
    stats = get_health_stats_for_date(date_str)
    if stats:
        health_stats[date_str] = stats
        processed_days += 1
        print(f"✓ Successfully retrieved health stats for {date_str}")
    else:
        print(f"✗ No health stats data for {date_str}")
    
    current_date += timedelta(days=1)

print(f"\n✓ Successfully retrieved health stats for {processed_days} out of {30} days")

# Analyze training data
def analyze_training_data(activities, health_stats):
    """Analyze training data"""
    analysis = {
        'summary': {
            'total_activities': len(activities),
            'days_with_data': len(health_stats),
            'date_range': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        },
        'activity_analysis': {},
        'health_analysis': {},
        'training_load': {},
        'recovery': {},
        'recommendations': []
    }
    
    # Activity analysis
    if activities:
        # Activity types
        activity_types = {}
        for activity in activities:
            activity_type_obj = activity.get('activityType', 'Unknown')
            # Handle case where activityType is a dict
            if isinstance(activity_type_obj, dict):
                activity_type = activity_type_obj.get('typeKey', 'Unknown')
            else:
                activity_type = activity_type_obj
            activity_types[activity_type] = activity_types.get(activity_type, 0) + 1
        analysis['activity_analysis']['types'] = activity_types
        
        # Activity duration
        total_duration = sum(activity.get('duration', 0) for activity in activities)
        avg_duration = total_duration / len(activities) if activities else 0
        analysis['activity_analysis']['total_duration_seconds'] = total_duration
        analysis['activity_analysis']['average_duration_seconds'] = avg_duration
        analysis['activity_analysis']['average_duration_minutes'] = round(avg_duration / 60, 2)
        
        # Activity frequency
        activity_dates = set()
        for activity in activities:
            start_time = activity.get('startTimeLocal', '')
            if start_time:
                date = start_time.split(' ')[0]
                activity_dates.add(date)
        analysis['activity_analysis']['activity_days'] = len(activity_dates)
        analysis['activity_analysis']['activity_frequency'] = round(len(activity_dates) / 30 * 100, 2)
    
    # Health analysis
    if health_stats:
        # Resting heart rate
        resting_heart_rates = [stats.get('restingHeartRate') for stats in health_stats.values() if stats.get('restingHeartRate')]
        if resting_heart_rates:
            avg_rhr = sum(resting_heart_rates) / len(resting_heart_rates)
            min_rhr = min(resting_heart_rates)
            max_rhr = max(resting_heart_rates)
            analysis['health_analysis']['resting_heart_rate'] = {
                'average': round(avg_rhr, 1),
                'min': min_rhr,
                'max': max_rhr
            }
        
        # Stress levels
        stress_levels = [stats.get('averageStressLevel') for stats in health_stats.values() if stats.get('averageStressLevel')]
        if stress_levels:
            avg_stress = sum(stress_levels) / len(stress_levels)
            analysis['health_analysis']['stress_level'] = {
                'average': round(avg_stress, 1)
            }
        
        # Body battery
        body_battery = [stats.get('bodyBatteryMostRecentValue') for stats in health_stats.values() if stats.get('bodyBatteryMostRecentValue')]
        if body_battery:
            avg_battery = sum(body_battery) / len(body_battery)
            analysis['health_analysis']['body_battery'] = {
                'average': round(avg_battery, 1)
            }
        
        # Steps
        steps = [stats.get('totalSteps') for stats in health_stats.values() if stats.get('totalSteps')]
        if steps:
            avg_steps = sum(steps) / len(steps)
            analysis['health_analysis']['steps'] = {
                'average': round(avg_steps, 0)
            }
    
    # Training load analysis
    # Calculate training frequency and intensity
    if activities:
        # Group activities by week
        weekly_activities = {}
        for activity in activities:
            start_time = activity.get('startTimeLocal', '')
            if start_time:
                date = start_time.split(' ')[0]
                week_start = datetime.strptime(date, '%Y-%m-%d') - timedelta(days=datetime.strptime(date, '%Y-%m-%d').weekday())
                week_key = week_start.strftime('%Y-%m-%d')
                if week_key not in weekly_activities:
                    weekly_activities[week_key] = []
                weekly_activities[week_key].append(activity)
        
        analysis['training_load']['weekly_activities'] = {}
        for week, acts in weekly_activities.items():
            analysis['training_load']['weekly_activities'][week] = len(acts)
        
        # Calculate average weekly training frequency
        avg_weekly_activities = sum(len(acts) for acts in weekly_activities.values()) / len(weekly_activities) if weekly_activities else 0
        analysis['training_load']['average_weekly_activities'] = round(avg_weekly_activities, 1)
    
    # Recovery analysis
    # Based on resting heart rate trends and body battery
    if health_stats:
        # Check for recovery patterns
        analysis['recovery']['days_with_data'] = len(health_stats)
    
    # Generate recommendations
    analysis['recommendations'] = generate_recommendations(analysis)
    
    return analysis

# Generate recommendations
def generate_recommendations(analysis):
    """Generate training recommendations based on analysis"""
    recommendations = []
    
    # Activity frequency recommendations
    activity_frequency = analysis['activity_analysis'].get('activity_frequency', 0)
    if activity_frequency < 30:
        recommendations.append({
            'category': 'frequency',
            'priority': 'high' if activity_frequency < 15 else 'medium',
            'title': 'Increase training frequency',
            'description': f'Your current training frequency is {activity_frequency}% (training on {analysis["activity_analysis"].get("activity_days", 0)} out of 30 days). Consider increasing to at least 4-5 days per week for optimal results.'
        })
    elif activity_frequency > 80:
        recommendations.append({
            'category': 'recovery',
            'priority': 'medium',
            'title': 'Include rest days',
            'description': f'Your current training frequency is very high ({activity_frequency}%). Make sure to include regular rest days to allow for proper recovery.'
        })
    
    # Activity balance recommendations
    activity_types = analysis['activity_analysis'].get('types', {})
    if len(activity_types) < 2:
        recommendations.append({
            'category': 'variety',
            'priority': 'medium',
            'title': 'Add variety to your training',
            'description': f'You currently only engage in {list(activity_types.keys())} activities. Adding variety can help prevent overuse injuries and improve overall fitness.'
        })
    
    # Recovery recommendations
    body_battery = analysis['health_analysis'].get('body_battery', {}).get('average', 50)
    if body_battery < 40:
        recommendations.append({
            'category': 'recovery',
            'priority': 'high',
            'title': 'Prioritize recovery',
            'description': f'Your average body battery is {body_battery}, which indicates you may be overtraining. Consider reducing training intensity and increasing rest time.'
        })
    
    # Resting heart rate recommendations
    rhr = analysis['health_analysis'].get('resting_heart_rate', {}).get('average', 70)
    if rhr > 65:
        recommendations.append({
            'category': 'cardiovascular',
            'priority': 'medium',
            'title': 'Improve cardiovascular fitness',
            'description': f'Your average resting heart rate is {rhr}. Regular cardio training can help lower your resting heart rate, which is associated with better cardiovascular health.'
        })
    
    return recommendations

# Analyze the data
analysis = analyze_training_data(activities, health_stats)

# Generate report
print("\n" + "="*80)
print("MONTHLY TRAINING ANALYSIS REPORT")
print("="*80)
print(f"Date Range: {analysis['summary']['date_range']}")
print(f"Total Activities: {analysis['summary']['total_activities']}")
print(f"Days with Health Data: {analysis['summary']['days_with_data']}")
print()

# Activity analysis
print("ACTIVITY ANALYSIS")
print("-"*80)
if analysis['activity_analysis']:
    print(f"Activity Types: {analysis['activity_analysis'].get('types', {})}")
    print(f"Activity Days: {analysis['activity_analysis'].get('activity_days', 0)} out of 30 days")
    print(f"Activity Frequency: {analysis['activity_analysis'].get('activity_frequency', 0)}%")
    print(f"Average Activity Duration: {analysis['activity_analysis'].get('average_duration_minutes', 0)} minutes")
else:
    print("No activity data available")
print()

# Health analysis
print("HEALTH ANALYSIS")
print("-"*80)
if analysis['health_analysis']:
    rhr = analysis['health_analysis'].get('resting_heart_rate', {})
    if rhr:
        print(f"Resting Heart Rate: {rhr.get('average', 'N/A')} BPM (Min: {rhr.get('min', 'N/A')}, Max: {rhr.get('max', 'N/A')})")
    
    stress = analysis['health_analysis'].get('stress_level', {})
    if stress:
        print(f"Average Stress Level: {stress.get('average', 'N/A')}")
    
    battery = analysis['health_analysis'].get('body_battery', {})
    if battery:
        print(f"Average Body Battery: {battery.get('average', 'N/A')}")
    
    steps = analysis['health_analysis'].get('steps', {})
    if steps:
        print(f"Average Daily Steps: {steps.get('average', 'N/A')}")
else:
    print("No health data available")
print()

# Training load
print("TRAINING LOAD")
print("-"*80)
if analysis['training_load']:
    print(f"Average Weekly Activities: {analysis['training_load'].get('average_weekly_activities', 0)}")
    print("Weekly Activity Count:")
    for week, count in analysis['training_load'].get('weekly_activities', {}).items():
        print(f"  {week}: {count} activities")
else:
    print("No training load data available")
print()

# Recommendations
print("RECOMMENDATIONS")
print("-"*80)
if analysis['recommendations']:
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"{i}. [{rec['priority'].upper()}] {rec['title']}")
        print(f"   {rec['description']}")
        print()
else:
    print("No specific recommendations at this time. Your training plan appears to be well-balanced.")
print()

# Training plan evaluation
print("TRAINING PLAN EVALUATION")
print("-"*80)
# Evaluate based on activity frequency and variety
activity_frequency = analysis['activity_analysis'].get('activity_frequency', 0)
activity_types = analysis['activity_analysis'].get('types', {})

if activity_frequency >= 50 and len(activity_types) >= 2:
    print("Your current training plan appears to be well-balanced with good frequency and variety.")
    print("The plan includes regular training sessions and engages in multiple activity types, which is ideal for overall fitness development.")
elif activity_frequency >= 50:
    print("Your training frequency is good, but you could benefit from adding more variety to your activities.")
    print("Consider incorporating different types of exercises to target different muscle groups and prevent overuse injuries.")
elif len(activity_types) >= 2:
    print("You have good variety in your training, but your frequency could be improved.")
    print("Consider increasing your training to at least 4-5 days per week for better results.")
else:
    print("Your training plan would benefit from both increased frequency and variety.")
    print("Aim for 4-5 training sessions per week, including a mix of different activity types.")
print()

# Save analysis to JSON file
with open('monthly_training_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(analysis, f, indent=2, ensure_ascii=False)

print("Analysis saved to monthly_training_analysis.json")
print("="*80)
