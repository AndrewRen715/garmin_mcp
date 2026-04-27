#!/usr/bin/env python3
"""
Create PacePro plan for 2024-10-08 trail run activity
Target: improve time from 5:09 to 4:00 hours
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def create_pacepro_plan():
    """Create PacePro plan for the trail run activity"""
    print("Creating PacePro plan for 2024-10-08 trail run...")
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
    
    # Create segments based on distance and elevation
    # We'll create 10 segments for better control
    segments = []
    segment_count = 10
    base_segment_distance = total_distance_km / segment_count
    
    # Simulate elevation profile (we'll create a realistic profile based on total gain)
    # Assuming elevation follows a typical trail pattern with ups and downs
    elevation_profile = [0, 200, 450, 700, 950, 1200, 1400, 1550, 1650, 1731, 1731]
    
    # Calculate segment paces considering elevation
    # Uphill segments will be slightly slower, downhill slightly faster
    for i in range(segment_count):
        segment_start_km = i * base_segment_distance
        segment_end_km = (i + 1) * base_segment_distance
        segment_distance = base_segment_distance
        
        if i == segment_count - 1:
            segment_distance = total_distance_km - segment_start_km
            segment_end_km = total_distance_km
        
        # Calculate elevation gain/loss for this segment
        segment_elevation_start = elevation_profile[i]
        segment_elevation_end = elevation_profile[i + 1]
        segment_elevation_change = segment_elevation_end - segment_elevation_start
        
        # Adjust pace based on elevation change
        # For every 100m of elevation gain, add 1 min/km to pace
        # For every 100m of elevation loss, subtract 0.5 min/km from pace
        elevation_adjustment = 0
        if segment_elevation_change > 0:
            elevation_adjustment = (segment_elevation_change / 100) * 1.0
        else:
            elevation_adjustment = (abs(segment_elevation_change) / 100) * -0.5
        
        # Calculate segment pace
        segment_pace = target_pace_min_per_km + elevation_adjustment
        # Ensure pace doesn't get too extreme
        segment_pace = max(6.0, min(13.0, segment_pace))
        
        # Calculate segment time
        segment_time_minutes = segment_distance * segment_pace
        
        # Calculate cumulative time
        cumulative_time_minutes = sum(seg['time_minutes'] for seg in segments) + segment_time_minutes
        
        # Format time
        segment_time_str = f"{int(segment_time_minutes // 60):02d}:{int(segment_time_minutes % 60):02d}"
        cumulative_time_str = f"{int(cumulative_time_minutes // 60):02d}:{int(cumulative_time_minutes % 60):02d}"
        
        segments.append({
            'segment': i + 1,
            'start_km': segment_start_km,
            'end_km': segment_end_km,
            'distance_km': segment_distance,
            'elevation_start': segment_elevation_start,
            'elevation_end': segment_elevation_end,
            'elevation_change': segment_elevation_change,
            'pace_min_per_km': segment_pace,
            'time_minutes': segment_time_minutes,
            'time_str': segment_time_str,
            'cumulative_time_minutes': cumulative_time_minutes,
            'cumulative_time_str': cumulative_time_str
        })
    
    # Adjust all segments proportionally to ensure total time is exactly 4 hours
    if segments:
        current_total_time = sum(seg['time_minutes'] for seg in segments)
        time_difference = target_time_minutes - current_total_time
        
        if abs(time_difference) > 0.1:
            # Calculate adjustment factor
            adjustment_factor = target_time_minutes / current_total_time
            
            # Adjust all segments proportionally
            cumulative_adjusted_time = 0
            for i, seg in enumerate(segments):
                seg['time_minutes'] *= adjustment_factor
                seg['pace_min_per_km'] = seg['time_minutes'] / seg['distance_km']
                # Ensure pace is within reasonable range
                seg['pace_min_per_km'] = max(6.0, min(13.0, seg['pace_min_per_km']))
                # Recalculate time based on adjusted pace
                seg['time_minutes'] = seg['pace_min_per_km'] * seg['distance_km']
                cumulative_adjusted_time += seg['time_minutes']
                seg['cumulative_time_minutes'] = cumulative_adjusted_time
                seg['time_str'] = f"{int(seg['time_minutes'] // 60):02d}:{int(seg['time_minutes'] % 60):02d}"
                seg['cumulative_time_str'] = f"{int(cumulative_adjusted_time // 60):02d}:{int(cumulative_adjusted_time % 60):02d}"
            
            # Final adjustment to ensure exactly 4 hours
            last_segment = segments[-1]
            final_time_difference = target_time_minutes - cumulative_adjusted_time
            if abs(final_time_difference) > 0.1:
                last_segment['time_minutes'] += final_time_difference
                last_segment['cumulative_time_minutes'] = target_time_minutes
                last_segment['pace_min_per_km'] = last_segment['time_minutes'] / last_segment['distance_km']
                # Ensure pace is within reasonable range
                last_segment['pace_min_per_km'] = max(6.0, min(13.0, last_segment['pace_min_per_km']))
                last_segment['time_str'] = f"{int(last_segment['time_minutes'] // 60):02d}:{int(last_segment['time_minutes'] % 60):02d}"
                last_segment['cumulative_time_str'] = f"{int(target_time_minutes // 60):02d}:{int(target_time_minutes % 60):02d}"
    
    # Print PacePro plan
    print("PacePro Plan (Target: 4:00:00):")
    print("-" * 120)
    print(f"{'Segment':<8} {'Distance':<12} {'Elevation':<20} {'Pace':<12} {'Segment Time':<15} {'Cumulative Time':<15}")
    print("-" * 120)
    
    for seg in segments:
        elevation_str = f"{seg['elevation_start']}m → {seg['elevation_end']}m ({seg['elevation_change']:+d}m)"
        pace_str = f"{seg['pace_min_per_km']:.2f} min/km"
        
        print(f"{seg['segment']:<8} {seg['distance_km']:.2f} km    {elevation_str:<20} {pace_str:<12} {seg['time_str']:<15} {seg['cumulative_time_str']:<15}")
    
    print("-" * 120)
    print(f"{'Total':<8} {total_distance_km:.2f} km    {'Total gain: ' + str(total_elevation_gain) + 'm':<20} {'Average: ' + f'{target_pace_min_per_km:.2f} min/km':<12} {'':<15} {'4:00:00':<15}")
    print("-" * 120)
    
    # Instructions for using PacePro
    print("\nInstructions for using this PacePro plan:")
    print("1. Open Garmin Connect app or Garmin Express")
    print("2. Go to Training > PacePro Pacing Strategies")
    print("3. Create a new PacePro plan for trail running")
    print("4. Enter the total distance: 25.0 km")
    print("5. Enter the total elevation gain: 1731 m")
    print("6. Set target time: 4:00:00")
    print("7. Add custom segments based on the above table")
    print("8. Sync the plan to your Garmin device")
    print("9. Select this plan when starting your next trail run")
    
    # Additional tips
    print("\nTraining Tips:")
    print("- Increase your weekly mileage gradually")
    print("- Include hill training to improve uphill performance")
    print("- Practice running downhill with proper form")
    print("- Do tempo runs to improve your aerobic capacity")
    print("- Fuel properly during long runs (every 45-60 minutes)")
    print("- Hydrate regularly before, during, and after runs")
    print("- Get adequate rest between training sessions")

def main():
    """Main function"""
    try:
        create_pacepro_plan()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
