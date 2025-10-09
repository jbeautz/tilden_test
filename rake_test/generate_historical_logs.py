#!/usr/bin/env python3
"""
Generate diverse historical trail logs for Tilden Regional Park
Creates 10 different trails covering various microclimates
Each trail represents a different date and terrain type
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_trail_log(trail_config):
    """Generate a single trail log based on configuration"""
    np.random.seed(trail_config['seed'])
    
    n_points = trail_config['duration']  # seconds at 1Hz
    times = pd.date_range(
        start=trail_config['date'],
        periods=n_points,
        freq='1s'
    )
    
    progress = np.linspace(0, 1, n_points)
    
    # Generate GPS path
    start_lat, start_lon = trail_config['start']
    end_lat, end_lon = trail_config['end']
    
    # Create winding path with natural variation
    lats = start_lat + (end_lat - start_lat) * progress
    lats += trail_config['path_variance'] * np.sin(progress * trail_config['path_frequency'])
    lats += np.random.normal(0, 0.00003, n_points)
    
    lons = start_lon + (end_lon - start_lon) * progress
    lons += trail_config['path_variance'] * np.cos(progress * trail_config['path_frequency'] * 1.3)
    lons += np.random.normal(0, 0.00004, n_points)
    
    # Altitude profile
    start_alt, end_alt = trail_config['altitude_range']
    if trail_config['terrain_type'] == 'steep_climb':
        alts = start_alt + (end_alt - start_alt) * (progress ** 1.5)
    elif trail_config['terrain_type'] == 'steep_descent':
        alts = start_alt + (end_alt - start_alt) * (progress ** 0.5)
    elif trail_config['terrain_type'] == 'rolling':
        alts = start_alt + (end_alt - start_alt) * progress + 30 * np.sin(progress * 8)
    else:  # gradual
        alts = start_alt + (end_alt - start_alt) * progress
    
    alts += np.random.normal(0, 2, n_points)
    
    # Temperature - varies with altitude and exposure
    base_temp = trail_config['base_temp']
    temp_alt_factor = -0.0065  # °C per meter
    altitude_effect = (alts - start_alt) * temp_alt_factor
    temps = base_temp + altitude_effect + np.random.normal(0, 0.4, n_points)
    
    # Add time of day variation if specified
    if trail_config.get('time_variation'):
        hour_progress = progress * 2  # Assume 2 hour max hike
        temps += 1.5 * np.sin(hour_progress * np.pi)  # Warming during day
    
    # Humidity - based on microclimate
    base_humidity = trail_config['base_humidity']
    humidity_trend = trail_config['humidity_trend']  # Change over trail
    
    humids = base_humidity + humidity_trend * progress
    
    # Add microclimate features
    if trail_config['microclimate'] == 'creek_bed':
        # High humidity with local variation near water features
        humids += 5 * np.sin(progress * 15) + np.random.normal(0, 2, n_points)
    elif trail_config['microclimate'] == 'exposed_ridge':
        # Lower humidity, more variable
        humids += np.random.normal(0, 3, n_points)
    elif trail_config['microclimate'] == 'forest':
        # Stable, moderate humidity
        humids += np.random.normal(0, 1.5, n_points)
    elif trail_config['microclimate'] == 'canyon':
        # Protected, stable high humidity
        humids += 2 * np.sin(progress * 5) + np.random.normal(0, 1, n_points)
    else:
        humids += np.random.normal(0, 2, n_points)
    
    humids = np.clip(humids, 20, 95)  # Realistic bounds
    
    # Pressure - decreases with altitude
    base_pressure = 1013.25
    pressure_alt_factor = -0.12  # hPa per meter
    press = base_pressure + (alts - 200) * pressure_alt_factor / 10
    press += np.random.normal(0, 0.5, n_points)
    
    # VOC/Gas - related to organic matter and humidity
    base_gas = trail_config['base_gas']
    gas_humidity_factor = trail_config['gas_humidity_factor']
    
    gas = base_gas + gas_humidity_factor * (humids - 60)
    gas += trail_config['gas_variance'] * np.sin(progress * 12)
    gas += np.random.normal(0, 800, n_points)
    gas = np.clip(gas, 30000, 80000)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': times,
        'temperature': temps,
        'humidity': humids,
        'pressure': press,
        'gas': gas,
        'latitude': lats,
        'longitude': lons,
        'altitude': alts
    })
    
    return df

# Trail configurations for Tilden Regional Park
TRAILS = [
    {
        'name': 'Nimitz Way - South Section',
        'date': '2025-10-01 09:00:00',
        'duration': 1500,  # 25 minutes
        'start': (37.8920, -122.2380),
        'end': (37.9050, -122.2490),
        'altitude_range': (350, 420),
        'terrain_type': 'rolling',
        'microclimate': 'exposed_ridge',
        'base_temp': 19.0,
        'base_humidity': 48,
        'humidity_trend': -5,  # Gets drier
        'base_gas': 48000,
        'gas_humidity_factor': 200,
        'gas_variance': 1500,
        'path_variance': 0.0002,
        'path_frequency': 10,
        'seed': 101,
        'description': 'Exposed ridge, dry'
    },
    {
        'name': 'Wildcat Creek Trail',
        'date': '2025-10-02 10:30:00',
        'duration': 1800,  # 30 minutes
        'start': (37.8980, -122.2290),
        'end': (37.9120, -122.2350),
        'altitude_range': (200, 260),
        'terrain_type': 'gradual',
        'microclimate': 'creek_bed',
        'base_temp': 17.5,
        'base_humidity': 85,
        'humidity_trend': 2,  # Stays humid
        'base_gas': 66000,
        'gas_humidity_factor': 250,
        'gas_variance': 2000,
        'path_variance': 0.00015,
        'path_frequency': 18,
        'seed': 102,
        'description': 'Creek bed, very humid'
    },
    {
        'name': 'Seaview Trail',
        'date': '2025-10-03 14:00:00',
        'duration': 2100,  # 35 minutes
        'start': (37.9000, -122.2420),
        'end': (37.9080, -122.2550),
        'altitude_range': (280, 380),
        'terrain_type': 'rolling',
        'microclimate': 'mixed',
        'base_temp': 20.0,
        'base_humidity': 58,
        'humidity_trend': -8,
        'base_gas': 54000,
        'gas_humidity_factor': 220,
        'gas_variance': 1800,
        'path_variance': 0.00025,
        'path_frequency': 12,
        'time_variation': True,
        'seed': 103,
        'description': 'Mid-elevation loop'
    },
    {
        'name': 'Big Springs Trail',
        'date': '2025-10-04 08:15:00',
        'duration': 1200,  # 20 minutes
        'start': (37.8950, -122.2410),
        'end': (37.9010, -122.2380),
        'altitude_range': (240, 280),
        'terrain_type': 'gradual',
        'microclimate': 'creek_bed',
        'base_temp': 16.5,
        'base_humidity': 78,
        'humidity_trend': 3,
        'base_gas': 63000,
        'gas_humidity_factor': 240,
        'gas_variance': 1700,
        'path_variance': 0.00012,
        'path_frequency': 15,
        'seed': 104,
        'description': 'Spring-fed, moist'
    },
    {
        'name': 'Curran Trail',
        'date': '2025-10-05 11:45:00',
        'duration': 1680,  # 28 minutes
        'start': (37.8930, -122.2450),
        'end': (37.9040, -122.2400),
        'altitude_range': (260, 340),
        'terrain_type': 'steep_climb',
        'microclimate': 'forest',
        'base_temp': 18.0,
        'base_humidity': 68,
        'humidity_trend': -6,
        'base_gas': 58000,
        'gas_humidity_factor': 210,
        'gas_variance': 1600,
        'path_variance': 0.00018,
        'path_frequency': 14,
        'seed': 105,
        'description': 'Shaded forest'
    },
    {
        'name': 'Pack Rat Trail',
        'date': '2025-10-06 13:20:00',
        'duration': 1320,  # 22 minutes
        'start': (37.8970, -122.2480),
        'end': (37.9060, -122.2440),
        'altitude_range': (310, 400),
        'terrain_type': 'steep_climb',
        'microclimate': 'exposed_ridge',
        'base_temp': 21.0,
        'base_humidity': 45,
        'humidity_trend': -7,
        'base_gas': 46000,
        'gas_humidity_factor': 190,
        'gas_variance': 1400,
        'path_variance': 0.00022,
        'path_frequency': 11,
        'time_variation': True,
        'seed': 106,
        'description': 'Sunny exposed hillside'
    },
    {
        'name': 'Laurel Canyon Trail',
        'date': '2025-10-07 09:45:00',
        'duration': 1920,  # 32 minutes
        'start': (37.8910, -122.2350),
        'end': (37.9030, -122.2460),
        'altitude_range': (220, 310),
        'terrain_type': 'gradual',
        'microclimate': 'canyon',
        'base_temp': 17.0,
        'base_humidity': 72,
        'humidity_trend': 4,
        'base_gas': 61000,
        'gas_humidity_factor': 230,
        'gas_variance': 1900,
        'path_variance': 0.00014,
        'path_frequency': 16,
        'seed': 107,
        'description': 'Deep canyon, humid'
    },
    {
        'name': 'Mezue Trail',
        'date': '2025-10-08 15:10:00',
        'duration': 1560,  # 26 minutes
        'start': (37.8990, -122.2500),
        'end': (37.9090, -122.2420),
        'altitude_range': (300, 370),
        'terrain_type': 'rolling',
        'microclimate': 'mixed',
        'base_temp': 19.5,
        'base_humidity': 56,
        'humidity_trend': -4,
        'base_gas': 52000,
        'gas_humidity_factor': 205,
        'gas_variance': 1650,
        'path_variance': 0.0002,
        'path_frequency': 13,
        'time_variation': True,
        'seed': 108,
        'description': 'Ridge connector, moderate'
    },
    {
        'name': 'Quarry Trail',
        'date': '2025-10-09 12:00:00',
        'duration': 1080,  # 18 minutes
        'start': (37.8960, -122.2320),
        'end': (37.9020, -122.2380),
        'altitude_range': (340, 410),
        'terrain_type': 'steep_climb',
        'microclimate': 'exposed_ridge',
        'base_temp': 20.5,
        'base_humidity': 42,
        'humidity_trend': -3,
        'base_gas': 44000,
        'gas_humidity_factor': 180,
        'gas_variance': 1300,
        'path_variance': 0.00028,
        'path_frequency': 9,
        'seed': 109,
        'description': 'Old quarry site, dry rocky'
    },
    {
        'name': 'Jewel Lake Loop',
        'date': '2025-10-10 10:00:00',
        'duration': 1440,  # 24 minutes
        'start': (37.8940, -122.2530),
        'end': (37.8990, -122.2510),
        'altitude_range': (210, 240),
        'terrain_type': 'gradual',
        'microclimate': 'creek_bed',
        'base_temp': 17.0,
        'base_humidity': 82,
        'humidity_trend': 1,
        'base_gas': 65000,
        'gas_humidity_factor': 245,
        'gas_variance': 2100,
        'path_variance': 0.0001,
        'path_frequency': 20,
        'seed': 110,
        'description': 'Lake shore, humid'
    }
]

def main():
    print("Generating 10 historical trail logs for Tilden Regional Park...")
    print()
    print("=" * 80)
    
    total_points = 0
    
    for i, trail_config in enumerate(TRAILS, 1):
        df = generate_trail_log(trail_config)
        
        # Create filename
        date_str = trail_config['date'].replace(' ', '_').replace(':', '')[:15]
        trail_name_safe = trail_config['name'].replace(' ', '_').replace('-', '_')
        filename = f"rake_log_{i}_{trail_name_safe}_{date_str}.csv"
        
        # Save to CSV
        df.to_csv(filename, index=False)
        
        total_points += len(df)
        
        print(f"✓ Generated: {filename} ({len(df)} points, {trail_config['description']})")
    
    print("=" * 80)
    print()
    print(f"✅ Successfully generated 10 historical log files!")
    print()
    print("These logs cover diverse microclimates:")
    print("  🌊 Humid creek beds and lake shores (75-85% humidity)")
    print("  🌲 Shaded forest trails (60-70% humidity)")
    print("  ⛰️  Exposed ridges and hillsides (40-55% humidity)")
    print("  🏔️  Various elevations (200-420m)")
    print()
    print(f"Total data points: {total_points:,}")
    print()
    print("Files can now be loaded in the data viewer for aggregate analysis!")

if __name__ == '__main__':
    main()
