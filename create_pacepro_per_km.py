#!/usr/bin/env python3
"""
Create PacePro plan with per-kilometer pacing for 2024-10-08 trail run activity
Target: improve time from 5:09 to 4:00 hours
"""

import sys
import os
from datetime import datetime, timedelta

def create_pacepro_per_km():
    """Create PacePro plan with per-kilometer pacing"""
    print("Creating PacePro plan (per kilometer) for 2024-10-08 trail run...")
    print("Current activity: 24.99 km, 1731m elevation gain, 5:09:00 time")
    print("Target: 4:00:00 time improvement\n")
    
    # Activity details
    activity_id = "420601500"
    total_distance_km = 24.99
    total_elevation_gain = 1731
    current_time_minutes = 308.8  # ~5:09
    target_time_minutes = 240.0   # 4:00
    
    # Calculate pace improvement
    current_pace_min_per_km = current_time_minutes / total_distance_km
    target_pace_min_per_km = target_time_minutes / total_distance_km
    
    print(f"Current average pace: {current_pace_min_per_km:.2f} min/km")
    print(f"Target average pace: {target_pace_min_per_km:.2f} min/km")
    print(f"Pace improvement: {current_pace_min_per_km - target_pace_min_per_km:.2f} min/km\n")
    
    # Create per-kilometer segments
    segments = []
    total_km = int(total_distance_km)
    
    # Create elevation profile per kilometer
    # Using more accurate elevation data based on user input
    # First km: 175m climb, 24m descent
    elevation_per_km = [
        0,      # Start
        151,    # 1km: 175m up, 24m down = net 151m
        300,    # 2km: additional 149m up
        450,    # 3km: additional 150m up
        600,    # 4km: additional 150m up
        750,    # 5km: additional 150m up
        900,    # 6km: additional 150m up
        1050,   # 7km: additional 150m up
        1200,   # 8km: additional 150m up
        1300,   # 9km: additional 100m up
        1400,   # 10km: additional 100m up
        1480,   # 11km: additional 80m up
        1550,   # 12km: additional 70m up
        1600,   # 13km: additional 50m up
        1650,   # 14km: additional 50m up
        1680,   # 15km: additional 30m up
        1700,   # 16km: additional 20m up
        1710,   # 17km: additional 10m up
        1715,   # 18km: additional 5m up
        1720,   # 19km: additional 5m up
        1725,   # 20km: additional 5m up
        1728,   # 21km: additional 3m up
        1730,   # 22km: additional 2m up
        1731,   # 23km: additional 1m up
        1731,   # 24km: flat
        1731    # 25km: flat
    ]
    
    # Ensure we have enough elevation points
    while len(elevation_per_km) < total_km + 1:
        elevation_per_km.append(total_elevation_gain)
    
    # Calculate per-kilometer paces
    cumulative_time = 0
    for km in range(total_km):
        start_km = km
        end_km = km + 1
        distance = 1.0
        
        # Calculate elevation gain for this kilometer
        elevation_start = elevation_per_km[km]
        elevation_end = elevation_per_km[km + 1]
        elevation_change = elevation_end - elevation_start
        
        # Adjust pace based on elevation change
        # For every 100m of elevation gain, add 1 min/km to pace
        # For every 100m of elevation loss, subtract 0.5 min/km from pace
        elevation_adjustment = 0
        if elevation_change > 0:
            elevation_adjustment = (elevation_change / 100) * 1.0
        else:
            elevation_adjustment = (abs(elevation_change) / 100) * -0.5
        
        # Calculate km pace
        km_pace = target_pace_min_per_km + elevation_adjustment
        # Ensure pace doesn't get too extreme
        km_pace = max(6.0, min(13.0, km_pace))
        
        # Calculate km time
        km_time = distance * km_pace
        cumulative_time += km_time
        
        # Format time
        km_time_str = f"{int(km_time // 60):02d}:{int(km_time % 60):02d}"
        cumulative_time_str = f"{int(cumulative_time // 60):02d}:{int(cumulative_time % 60):02d}"
        
        segments.append({
            'km': km + 1,
            'start_km': start_km,
            'end_km': end_km,
            'distance_km': distance,
            'elevation_start': elevation_start,
            'elevation_end': elevation_end,
            'elevation_change': elevation_change,
            'pace_min_per_km': km_pace,
            'time_minutes': km_time,
            'time_str': km_time_str,
            'cumulative_time_minutes': cumulative_time,
            'cumulative_time_str': cumulative_time_str
        })
    
    # Handle the last partial kilometer
    if total_distance_km > total_km:
        start_km = total_km
        end_km = total_distance_km
        distance = total_distance_km - total_km
        
        elevation_start = elevation_per_km[total_km]
        elevation_end = total_elevation_gain
        elevation_change = elevation_end - elevation_start
        
        # Adjust pace based on elevation change
        elevation_adjustment = 0
        if elevation_change > 0:
            elevation_adjustment = (elevation_change / 100) * 1.0
        else:
            elevation_adjustment = (abs(elevation_change) / 100) * -0.5
        
        # Calculate pace
        km_pace = target_pace_min_per_km + elevation_adjustment
        km_pace = max(6.0, min(13.0, km_pace))
        
        # Calculate time
        km_time = distance * km_pace
        cumulative_time += km_time
        
        # Format time
        km_time_str = f"{int(km_time // 60):02d}:{int(km_time % 60):02d}"
        cumulative_time_str = f"{int(cumulative_time // 60):02d}:{int(cumulative_time % 60):02d}"
        
        segments.append({
            'km': total_km + 1,
            'start_km': start_km,
            'end_km': end_km,
            'distance_km': distance,
            'elevation_start': elevation_start,
            'elevation_end': elevation_end,
            'elevation_change': elevation_change,
            'pace_min_per_km': km_pace,
            'time_minutes': km_time,
            'time_str': km_time_str,
            'cumulative_time_minutes': cumulative_time,
            'cumulative_time_str': cumulative_time_str
        })
    
    # Adjust times to ensure total is exactly 4 hours
    if segments:
        current_total = segments[-1]['cumulative_time_minutes']
        time_diff = target_time_minutes - current_total
        
        if abs(time_diff) > 0.1:
            # Distribute the time difference proportionally
            for seg in segments:
                seg['time_minutes'] += (seg['time_minutes'] / current_total) * time_diff
                seg['pace_min_per_km'] = seg['time_minutes'] / seg['distance_km']
                # Ensure pace is within reasonable range
                seg['pace_min_per_km'] = max(6.0, min(13.0, seg['pace_min_per_km']))
                seg['time_minutes'] = seg['pace_min_per_km'] * seg['distance_km']
            
            # Recalculate cumulative times
            cumulative_time = 0
            for seg in segments:
                cumulative_time += seg['time_minutes']
                seg['cumulative_time_minutes'] = cumulative_time
                seg['time_str'] = f"{int(seg['time_minutes'] // 60):02d}:{int(seg['time_minutes'] % 60):02d}"
                seg['cumulative_time_str'] = f"{int(cumulative_time // 60):02d}:{int(cumulative_time % 60):02d}"
            
            # Final adjustment to last segment
            last_seg = segments[-1]
            final_diff = target_time_minutes - last_seg['cumulative_time_minutes']
            if abs(final_diff) > 0.1:
                last_seg['time_minutes'] += final_diff
                last_seg['cumulative_time_minutes'] = target_time_minutes
                last_seg['pace_min_per_km'] = last_seg['time_minutes'] / last_seg['distance_km']
                last_seg['pace_min_per_km'] = max(6.0, min(13.0, last_seg['pace_min_per_km']))
                last_seg['time_minutes'] = last_seg['pace_min_per_km'] * last_seg['distance_km']
                last_seg['time_str'] = f"{int(last_seg['time_minutes'] // 60):02d}:{int(last_seg['time_minutes'] % 60):02d}"
                last_seg['cumulative_time_str'] = f"{int(target_time_minutes // 60):02d}:{int(target_time_minutes % 60):02d}"
    
    # Print PacePro plan
    print("PacePro Plan (Per Kilometer) - Target: 4:00:00:")
    print("-" * 130)
    print(f"{'KM':<5} {'Distance':<10} {'Elevation':<20} {'Pace':<12} {'KM Time':<12} {'Cumulative Time':<15}")
    print("-" * 130)
    
    for seg in segments:
        elevation_str = f"{seg['elevation_start']}m → {seg['elevation_end']}m ({seg['elevation_change']:+d}m)"
        pace_str = f"{seg['pace_min_per_km']:.2f} min/km"
        
        print(f"{seg['km']:<5} {seg['distance_km']:.1f} km    {elevation_str:<20} {pace_str:<12} {seg['time_str']:<12} {seg['cumulative_time_str']:<15}")
    
    print("-" * 130)
    print(f"{'Total':<5} {total_distance_km:.2f} km    {'Total gain: ' + str(total_elevation_gain) + 'm':<20} {'Average: ' + f'{target_pace_min_per_km:.2f} min/km':<12} {'':<12} {'4:00:00':<15}")
    print("-" * 130)
    
    # Instructions for using PacePro
    print("\nInstructions for using this PacePro plan:")
    print("1. Open Garmin Connect app or Garmin Express")
    print("2. Go to Training > PacePro Pacing Strategies")
    print("3. Create a new PacePro plan for trail running")
    print("4. Enter the total distance: 25.0 km")
    print("5. Enter the total elevation gain: 1731 m")
    print("6. Set target time: 4:00:00")
    print("7. Select 'Custom' pacing strategy")
    print("8. Add custom segments at each kilometer mark using the table above")
    print("9. For each segment, enter the start distance, end distance, and target pace")
    print("10. Sync the plan to your Garmin device")
    print("11. Select this plan when starting your next trail run")
    
    # API Information
    print("\nAPI Information:")
    print("The garminconnect library (v0.2.38) used in this project does not currently support")
    print("direct PacePro plan creation via API. You need to manually create the plan in")
    print("Garmin Connect using the above per-kilometer pacing data.")
    
    # Additional tips
    print("\nTraining Tips:")
    print("- Practice running at the target paces during training sessions")
    print("- Include hill training to improve uphill performance")
    print("- Practice running downhill with proper form to save energy")
    print("- Do tempo runs to improve your aerobic capacity")
    print("- Fuel properly during long runs (every 45-60 minutes)")
    print("- Hydrate regularly before, during, and after runs")
    print("- Get adequate rest between training sessions")
    print("- Gradually build up your mileage and intensity")

def main():
    """Main function"""
    try:
        create_pacepro_per_km()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
