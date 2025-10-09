#!/usr/bin/env python3
"""
Generate 10 historical log files from different Tilden Regional Park trails
These simulate real sensor data from various hikes with different microclimates
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)

# Define 10 different trail routes in Tilden Regional Park
trails = {
    "1_Nimitz_Way_South": {
        "description": "Nimitz Way - South Section (Exposed ridge, dry)",
        "start_lat": 37.8920, "start_lon": -122.2410, "start_alt": 380,
        "end_lat": 37.8880, "end_lon": -122.2380, "end_alt": 420,
        "humidity_base": 45, "temp_base": 17, "duration_min": 25
    },
    "2_Wildcat_Creek_Trail": {
        "description": "Wildcat Creek Trail (Creek bed, very humid)",
        "start_lat": 37.9020, "start_lon": -122.2350, "start_alt": 200,
        "end_lat": 37.9070, "end_lon": -122.2320, "end_alt": 250,
        "humidity_base": 78, "temp_base": 16, "duration_min": 30
    },
    "3_Seaview_Trail": {
        "description": "Seaview Trail (Mid-elevation loop)",
        "start_lat": 37.8990, "start_lon": -122.2480, "start_alt": 300,
        "end_lat": 37.9030, "end_lon": -122.2500, "end_alt": 400,
        "humidity_base": 55, "temp_base": 18, "duration_min": 35
    },
    "4_Big_Springs_Trail": {
        "description": "Big Springs Trail (Spring-fed, moist)",
        "start_lat": 37.8950, "start_lon": -122.2400, "start_alt": 280,
        "end_lat": 37.8985, "end_lon": -122.2380, "end_alt": 320,
        "humidity_base": 72, "temp_base": 15, "duration_min": 20
    },
    "5_Curran_Trail": {
        "description": "Curran Trail (Shaded forest)",
        "start_lat": 37.8930, "start_lon": -122.2520, "start_alt": 260,
        "end_lat": 37.8970, "end_lon": -122.2550, "end_alt": 340,
        "humidity_base": 65, "temp_base": 16, "duration_min": 28
    },
    "6_Pack_Rat_Trail": {
        "description": "Pack Rat Trail (Sunny exposed hillside)",
        "start_lat": 37.8960, "start_lon": -122.2360, "start_alt": 320,
        "end_lat": 37.9000, "end_lon": -122.2340, "end_alt": 380,
        "humidity_base": 42, "temp_base": 19, "duration_min": 22
    },
    "7_Laurel_Canyon_Trail": {
        "description": "Laurel Canyon Trail (Deep canyon, humid)",
        "start_lat": 37.8940, "start_lon": -122.2460, "start_alt": 240,
        "end_lat": 37.8900, "end_lon": -122.2490, "end_alt": 220,
        "humidity_base": 76, "temp_base": 15, "duration_min": 32
    },
    "8_Mezue_Trail": {
        "description": "Mezue Trail (Ridge connector, moderate)",
        "start_lat": 37.9010, "start_lon": -122.2420, "start_alt": 350,
        "end_lat": 37.9050, "end_lon": -122.2450, "end_alt": 420,
        "humidity_base": 52, "temp_base": 17, "duration_min": 26
    },
    "9_Quarry_Trail": {
        "description": "Quarry Trail (Old quarry site, dry rocky)",
        "start_lat": 37.8980, "start_lon": -122.2300, "start_alt": 340,
        "end_lat": 37.9020, "end_lon": -122.2280, "end_alt": 380,
        "humidity_base": 40, "temp_base": 20, "duration_min": 18
    },
    "10_Jewel_Lake_Loop": {
        "description": "Jewel Lake Loop (Lake shore, humid)",
        "start_lat": 37.8910, "start_lon": -122.2580, "start_alt": 220,
        "end_lat": 37.8935, "end_lon": -122.2560, "end_alt": 230,
        "humidity_base": 82, "temp_base": 14, "duration_min": 24
    }
}

def generate_trail_log(trail_name, trail_config, date_offset_days):
    """Generate a realistic log file for one trail"""
    
    # Calculate number of data points (1Hz sampling)
    n_points = trail_config['duration_min'] * 60
    
    # Create timestamp
    start_date = datetime(2025, 10, 1) + timedelta(days=date_offset_days)
    times = pd.date_range(start=start_date, periods=n_points, freq='1s')
    
    # Progress along trail (0 to 1)
    progress = np.linspace(0, 1, n_points)
    
    # Latitude (with realistic winding)
    lat_change = trail_config['end_lat'] - trail_config['start_lat']
    lats = trail_config['start_lat'] + lat_change * progress
    lats += 0.0001 * np.sin(progress * 15) + np.random.normal(0, 0.00003, n_points)
    
    # Longitude (with realistic winding)
    lon_change = trail_config['end_lon'] - trail_config['start_lon']
    lons = trail_config['start_lon'] + lon_change * progress
    lons += 0.0001 * np.cos(progress * 12) + np.random.normal(0, 0.00003, n_points)
    
    # Altitude (smooth transitions with micro-variations)
    alt_change = trail_config['end_alt'] - trail_config['start_alt']
    alts = trail_config['start_alt'] + alt_change * (progress ** 0.9)
    alts += 4 * np.sin(progress * 8) + np.random.normal(0, 1.5, n_points)
    
    # Temperature (affected by altitude and time of day)
    temps = trail_config['temp_base'] - (alt_change / 100) * progress
    temps += 1.5 * np.sin(progress * 3) + np.random.normal(0, 0.4, n_points)
    
    # Humidity (characteristic of trail type, inversely correlated with temp)
    humids = trail_config['humidity_base'] * np.ones(n_points)
    humids += -5 * (temps - trail_config['temp_base']) / 5  # Temperature effect
    humids += 3 * np.sin(progress * 5) + np.random.normal(0, 1.8, n_points)
    humids = np.clip(humids, 20, 95)  # Realistic bounds
    
    # Pressure (decreases with altitude)
    press = 1013 - (alts - trail_config['start_alt']) / 10
    press += 0.8 * np.sin(progress * 4) + np.random.normal(0, 0.3, n_points)
    
    # VOC/Gas (higher in humid areas, lower in dry exposed areas)
    # Correlates with organic matter and moisture
    gas_base = 45000 + (humids - 50) * 250  # More humid = more organic = higher gas
    gas = gas_base + 3000 * np.sin(progress * 7) + np.random.normal(0, 600, n_points)
    gas = np.clip(gas, 35000, 70000)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': times,
        'latitude': lats,
        'longitude': lons,
        'altitude': alts,
        'temperature': temps,
        'humidity': humids,
        'pressure': press,
        'gas': gas
    })
    
    # Save to CSV
    filename = f"rake_log_{trail_name}_{start_date.strftime('%Y%m%d_%H%M%S')}.csv"
    df.to_csv(filename, index=False)
    print(f"✓ Generated: {filename} ({n_points} points, {trail_config['description']})")
    return filename

# Generate all 10 trail logs
print("Generating 10 historical trail logs for Tilden Regional Park...\n")
print("=" * 80)

generated_files = []
for idx, (trail_name, config) in enumerate(trails.items()):
    filename = generate_trail_log(trail_name, config, date_offset_days=idx)
    generated_files.append(filename)

print("=" * 80)
print(f"\n✅ Successfully generated {len(generated_files)} historical log files!")
print("\nThese logs cover diverse microclimates:")
print("  🌊 Humid creek beds and lake shores (75-85% humidity)")
print("  🌲 Shaded forest trails (60-70% humidity)")
print("  ⛰️  Exposed ridges and hillsides (40-55% humidity)")
print("  🏔️  Various elevations (200-420m)")
print("\nFiles can now be loaded in the data viewer for aggregate analysis!")
