"""Script to analyze yesterday's running activity"""
import json
import os
from datetime import datetime

# Load the last run data
with open('last_run_details.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract metric descriptors
metric_descriptors = data.get('metricDescriptors', [])
metric_map = {}
for desc in metric_descriptors:
    metric_map[desc['metricsIndex']] = desc['key']

# Extract activity detail metrics
activity_metrics = data.get('activityDetailMetrics', [])

# Find key metric indices
duration_index = None
distance_index = None
heart_rate_index = None
speed_index = None
cadence_index = None

for idx, key in metric_map.items():
    if key == 'sumElapsedDuration':
        duration_index = idx
    elif key == 'sumDistance':
        distance_index = idx
    elif key == 'directHeartRate':
        heart_rate_index = idx
    elif key == 'directSpeed':
        speed_index = idx
    elif key == 'directRunCadence':
        cadence_index = idx

# Extract data points
heart_rates = []
speeds = []
cadences = []

for metric in activity_metrics:
    metrics = metric.get('metrics', [])
    
    if heart_rate_index is not None and len(metrics) > heart_rate_index and metrics[heart_rate_index] is not None:
        heart_rates.append(metrics[heart_rate_index])
    
    if speed_index is not None and len(metrics) > speed_index and metrics[speed_index] is not None:
        speeds.append(metrics[speed_index] * 3.6)  # Convert m/s to km/h
    
    if cadence_index is not None and len(metrics) > cadence_index and metrics[cadence_index] is not None:
        cadences.append(metrics[cadence_index])

# Calculate statistics
def calculate_stats(values):
    if not values:
        return None, None, None
    return min(values), max(values), sum(values) / len(values)

# Get statistics
min_hr, max_hr, avg_hr = calculate_stats(heart_rates)
min_speed, max_speed, avg_speed = calculate_stats(speeds)
min_cadence, max_cadence, avg_cadence = calculate_stats(cadences)

# Calculate total distance and duration from the last data point
last_metrics = activity_metrics[-1].get('metrics', []) if activity_metrics else []

if distance_index is not None and len(last_metrics) > distance_index:
    total_distance = last_metrics[distance_index] / 1000  # Convert to km (value / 1000)
else:
    total_distance = 0

if duration_index is not None and len(last_metrics) > duration_index:
    total_duration = last_metrics[duration_index] * 1000 / 1000  # Convert to seconds (value * factor / 1000)
else:
    total_duration = 0

# Calculate pace
if total_distance > 0 and total_duration > 0:
    pace_seconds_per_km = total_duration / total_distance
    pace_minutes = int(pace_seconds_per_km // 60)
    pace_seconds = int(pace_seconds_per_km % 60)
else:
    pace_minutes, pace_seconds = 0, 0

# Print analysis report
print("=" * 80)
print("YESTERDAY'S RUNNING ANALYSIS")
print("=" * 80)
print()

# Basic info
print("BASIC INFO")
print("-" * 80)
print(f"Activity ID: {data.get('activityId', 'Unknown')}")
print(f"Date: 2026-04-14")
print()

# Metrics
print("METRICS")
print("-" * 80)
print(f"Total Distance: {total_distance:.2f} km")
print(f"Total Duration: {int(total_duration // 3600)}:{int((total_duration % 3600) // 60)}:{int(total_duration % 60)}")
print(f"Average Pace: {pace_minutes}:{pace_seconds:02d} min/km")
print(f"Average Speed: {avg_speed:.2f} km/h")
print()

# Heart rate
print("HEART RATE")
print("-" * 80)
if heart_rates:
    print(f"Average Heart Rate: {avg_hr:.1f} BPM")
    print(f"Max Heart Rate: {max_hr:.1f} BPM")
    print(f"Min Heart Rate: {min_hr:.1f} BPM")
else:
    print("No heart rate data available")
print()

# Running dynamics
print("RUNNING DYNAMICS")
print("-" * 80)
if cadences:
    print(f"Average Cadence: {avg_cadence:.1f} steps/min")
else:
    print("No cadence data available")
print()

# Intensity analysis
print("INTENSITY ANALYSIS")
print("-" * 80)
if heart_rates:
    # Define heart rate zones (simplified)
    zones = {
        "Z1 (Recovery)": (0, 120),
        "Z2 (Endurance)": (120, 140),
        "Z3 (Tempo)": (140, 160),
        "Z4 (Threshold)": (160, 180),
        "Z5 (Maximum)": (180, 220)
    }
    
    zone_times = {zone: 0 for zone in zones}
    total_hr_points = len(heart_rates)
    
    for hr in heart_rates:
        for zone, (min_hr, max_hr) in zones.items():
            if min_hr <= hr < max_hr:
                zone_times[zone] += 1
                break
    
    print("Heart Rate Zone Distribution:")
    for zone, count in zone_times.items():
        if total_hr_points > 0:
            percentage = (count / total_hr_points) * 100
            print(f"  {zone}: {percentage:.1f}%")
else:
    print("No heart rate data for intensity analysis")
print()

# Conclusion
print("CONCLUSION")
print("-" * 80)
print("Based on the analysis of yesterday's run:")
print()

# Generate conclusion based on data
if total_distance > 0:
    if total_distance < 5:
        print("- This was a short run, likely a recovery or warm-up session.")
    elif total_distance < 10:
        print("- This was a moderate distance run, good for maintaining fitness.")
    else:
        print("- This was a long run, excellent for building endurance.")
else:
    print("- No distance data available.")

if avg_hr is not None:
    if avg_hr < 120:
        print("- The intensity was low, suitable for recovery.")
    elif avg_hr < 140:
        print("- The intensity was moderate, ideal for endurance training (Z2).")
    elif avg_hr < 160:
        print("- The intensity was high, good for tempo training (Z3).")
    else:
        print("- The intensity was very high, suitable for threshold or interval training.")
else:
    print("- No heart rate data available for intensity assessment.")

if avg_cadence is not None:
    if avg_cadence < 160:
        print("- Cadence is on the lower side, consider increasing for better running efficiency.")
    elif avg_cadence < 180:
        print("- Cadence is within the optimal range for efficient running.")
    else:
        print("- Cadence is very high, which may be efficient but could lead to fatigue.")
else:
    print("- No cadence data available for running form assessment.")

print()
print("=" * 80)
print("Analysis complete!")
print("=" * 80)