"""Script to parse and analyze the detailed running activity data"""
import json
import os
import sys
from datetime import datetime

# Read the saved activity data
with open('last_run_details.json', 'r', encoding='utf-8') as f:
    activity_data = json.load(f)

# Extract metric descriptors
metric_descriptors = activity_data.get('metricDescriptors', [])
metric_map = {}

# Create a map of metric keys to their indices
for descriptor in metric_descriptors:
    key = descriptor.get('key')
    index = descriptor.get('metricsIndex')
    if key and index is not None:
        metric_map[key] = index

# Extract activity detail metrics
activity_metrics = activity_data.get('activityDetailMetrics', [])

if not activity_metrics:
    print("No activity metrics found")
    sys.exit(1)

# Function to get metric value at a specific index
def get_metric_value(metrics, metric_key):
    if metric_key not in metric_map:
        return None
    index = metric_map[metric_key]
    if index < len(metrics):
        return metrics[index]
    return None

# Extract summary data
print("=" * 80)
print("RUNNING ACTIVITY ANALYSIS")
print("=" * 80)

# Get start time
first_metrics = activity_metrics[0].get('metrics', [])
last_metrics = activity_metrics[-1].get('metrics', [])

# Calculate total distance
total_distance = get_metric_value(last_metrics, 'sumDistance')
if total_distance:
    # Convert from meters to kilometers
    total_distance_km = total_distance / 1000
    print(f"Total Distance: {total_distance_km:.2f} km")
else:
    print("Total Distance: Unknown")

# Calculate total duration
total_duration = get_metric_value(last_metrics, 'sumDuration')
if total_duration:
    # Convert from seconds to minutes and seconds
    minutes = int(total_duration // 60)
    seconds = int(total_duration % 60)
    print(f"Total Duration: {minutes}:{seconds:02d}")
    
    # Calculate average pace
    if total_distance and total_distance > 0:
        pace_seconds_per_km = total_duration / (total_distance / 1000)
        pace_minutes = int(pace_seconds_per_km // 60)
        pace_seconds = int(pace_seconds_per_km % 60)
        print(f"Average Pace: {pace_minutes}:{pace_seconds:02d} min/km")
        
        # Calculate average speed
        avg_speed = (total_distance / 1000) / (total_duration / 3600)
        print(f"Average Speed: {avg_speed:.2f} km/h")
else:
    print("Total Duration: Unknown")

# Calculate average heart rate
heart_rates = []
for metric_entry in activity_metrics:
    metrics = metric_entry.get('metrics', [])
    hr = get_metric_value(metrics, 'directHeartRate')
    if hr and hr is not None:
        heart_rates.append(hr)

if heart_rates:
    avg_hr = sum(heart_rates) / len(heart_rates)
    max_hr = max(heart_rates)
    min_hr = min(heart_rates)
    print(f"Average Heart Rate: {avg_hr:.1f} BPM")
    print(f"Max Heart Rate: {max_hr} BPM")
    print(f"Min Heart Rate: {min_hr} BPM")
else:
    print("Heart Rate Data: Not available")

# Calculate average cadence
cadences = []
for metric_entry in activity_metrics:
    metrics = metric_entry.get('metrics', [])
    cadence = get_metric_value(metrics, 'directRunCadence')
    if cadence and cadence is not None:
        cadences.append(cadence)

if cadences:
    avg_cadence = sum(cadences) / len(cadences)
    print(f"Average Cadence: {avg_cadence:.1f} steps/min")
else:
    print("Cadence Data: Not available")

# Calculate average ground contact time
ground_contact_times = []
for metric_entry in activity_metrics:
    metrics = metric_entry.get('metrics', [])
    gct = get_metric_value(metrics, 'directGroundContactTime')
    if gct and gct is not None:
        ground_contact_times.append(gct)

if ground_contact_times:
    avg_gct = sum(ground_contact_times) / len(ground_contact_times)
    print(f"Average Ground Contact Time: {avg_gct:.1f} ms")
else:
    print("Ground Contact Time: Not available")

# Calculate average speed
speeds = []
for metric_entry in activity_metrics:
    metrics = metric_entry.get('metrics', [])
    speed = get_metric_value(metrics, 'directSpeed')
    if speed and speed is not None:
        speeds.append(speed)

if speeds:
    avg_speed = sum(speeds) / len(speeds)
    # Convert from m/s to km/h
    avg_speed_kmh = avg_speed * 3.6
    print(f"Average Speed (from sensor): {avg_speed_kmh:.2f} km/h")
else:
    print("Speed Data: Not available")

# Calculate elevation gain
first_elevation = get_metric_value(first_metrics, 'directElevation')
last_elevation = get_metric_value(last_metrics, 'directElevation')
if first_elevation is not None and last_elevation is not None:
    elevation_gain = last_elevation - first_elevation
    print(f"Elevation Change: {elevation_gain:.1f} m")
else:
    print("Elevation Data: Not available")

# Calculate performance condition
performance_conditions = []
for metric_entry in activity_metrics:
    metrics = metric_entry.get('metrics', [])
    pc = get_metric_value(metrics, 'directPerformanceCondition')
    if pc and pc is not None:
        performance_conditions.append(pc)

if performance_conditions:
    avg_pc = sum(performance_conditions) / len(performance_conditions)
    print(f"Average Performance Condition: {avg_pc:.1f}")
else:
    print("Performance Condition: Not available")

# Heart rate zone analysis
print("\nHEART RATE ZONE ANALYSIS")
print("-" * 80)

# Define heart rate zones (example values, adjust based on user's actual zones)
max_hr = max(heart_rates) if heart_rates else 180
zones = [
    {"name": "Zone 1 (Recovery)", "min": 0, "max": int(max_hr * 0.6)},  # 60%
    {"name": "Zone 2 (Endurance)", "min": int(max_hr * 0.6), "max": int(max_hr * 0.7)},  # 60-70%
    {"name": "Zone 3 (Tempo)", "min": int(max_hr * 0.7), "max": int(max_hr * 0.8)},  # 70-80%
    {"name": "Zone 4 (Threshold)", "min": int(max_hr * 0.8), "max": int(max_hr * 0.9)},  # 80-90%
    {"name": "Zone 5 (Maximum)", "min": int(max_hr * 0.9), "max": max_hr}  # 90-100%
]

# Calculate time in each zone
zone_times = {"Zone 1": 0, "Zone 2": 0, "Zone 3": 0, "Zone 4": 0, "Zone 5": 0}

if heart_rates and len(heart_rates) == len(activity_metrics):
    # Assume each metric entry is 1 second apart
    interval = 1  # seconds
    
    for hr in heart_rates:
        for i, zone in enumerate(zones):
            if zone["min"] <= hr < zone["max"]:
                zone_name = f"Zone {i+1}"
                if zone_name in zone_times:
                    zone_times[zone_name] += interval
                break
    
    # Convert to minutes and print
    total_time = sum(zone_times.values())
    for zone_name, time in zone_times.items():
        minutes = time / 60
        percentage = (time / total_time) * 100 if total_time > 0 else 0
        print(f"{zone_name}: {minutes:.1f} minutes ({percentage:.1f}%)")
else:
    print("Insufficient heart rate data for zone analysis")

# Speed analysis
print("\nSPEED ANALYSIS")
print("-" * 80)

if speeds:
    max_speed = max(speeds)
    min_speed = min([s for s in speeds if s > 0]) if speeds else 0
    avg_speed = sum(speeds) / len(speeds)
    
    print(f"Max Speed: {max_speed * 3.6:.2f} km/h")
    print(f"Min Speed: {min_speed * 3.6:.2f} km/h")
    print(f"Average Speed: {avg_speed * 3.6:.2f} km/h")
else:
    print("Insufficient speed data for analysis")

# Cadence analysis
print("\nCADENCE ANALYSIS")
print("-" * 80)

if cadences:
    max_cadence = max(cadences)
    min_cadence = min(cadences)
    avg_cadence = sum(cadences) / len(cadences)
    
    print(f"Max Cadence: {max_cadence:.1f} steps/min")
    print(f"Min Cadence: {min_cadence:.1f} steps/min")
    print(f"Average Cadence: {avg_cadence:.1f} steps/min")
else:
    print("Insufficient cadence data for analysis")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
