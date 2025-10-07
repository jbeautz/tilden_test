#!/usr/bin/env python3
"""
Analyze and visualize sensor data from CSV log files.
Combines multiple log files and creates time series plots.
"""

import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime

# Find all CSV log files in the current directory
log_files = sorted(glob.glob('rake_log_*.csv'))

if not log_files:
    print("No log files found! Make sure you're in the directory with the CSV files.")
    print("Looking for files matching: rake_log_*.csv")
    exit(1)

print(f"Found {len(log_files)} log files:")
for f in log_files:
    print(f"  - {f}")

# Read and combine all CSV files
all_data = []
for file in log_files:
    try:
        # Read CSV, skip comment rows that start with #
        df = pd.read_csv(file, comment='#')
        
        # Add source file column
        df['source_file'] = os.path.basename(file)
        
        all_data.append(df)
        print(f"✓ Loaded {file}: {len(df)} rows")
    except Exception as e:
        print(f"✗ Error loading {file}: {e}")

# Combine all dataframes
combined_df = pd.concat(all_data, ignore_index=True)

# Convert timestamp to datetime
combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])

# Sort by timestamp
combined_df = combined_df.sort_values('timestamp')

# Remove any duplicate timestamps
combined_df = combined_df.drop_duplicates(subset='timestamp', keep='first')

print(f"\n{'='*60}")
print(f"Combined dataset: {len(combined_df)} total readings")
print(f"Time range: {combined_df['timestamp'].min()} to {combined_df['timestamp'].max()}")
print(f"Duration: {combined_df['timestamp'].max() - combined_df['timestamp'].min()}")
print(f"{'='*60}\n")

# Display basic statistics
print("Data Summary:")
print(combined_df[['temperature', 'humidity', 'pressure', 'gas']].describe())
print()

# Create visualizations
fig, axes = plt.subplots(5, 1, figsize=(14, 12))
fig.suptitle('Environmental Sensor Data Over Time', fontsize=16, fontweight='bold')

# Temperature
ax1 = axes[0]
ax1.plot(combined_df['timestamp'], combined_df['temperature'], 'r-', linewidth=1, alpha=0.7)
ax1.set_ylabel('Temperature (°C)', fontsize=11, fontweight='bold')
ax1.grid(True, alpha=0.3)
ax1.set_title('Temperature', fontsize=12)

# Humidity
ax2 = axes[1]
ax2.plot(combined_df['timestamp'], combined_df['humidity'], 'b-', linewidth=1, alpha=0.7)
ax2.set_ylabel('Humidity (%)', fontsize=11, fontweight='bold')
ax2.grid(True, alpha=0.3)
ax2.set_title('Humidity', fontsize=12)

# Pressure
ax3 = axes[2]
ax3.plot(combined_df['timestamp'], combined_df['pressure'], 'g-', linewidth=1, alpha=0.7)
ax3.set_ylabel('Pressure (hPa)', fontsize=11, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.set_title('Atmospheric Pressure', fontsize=12)

# Gas/VOC (convert to kΩ for readability)
ax4 = axes[3]
combined_df['gas_kohm'] = combined_df['gas'] / 1000
ax4.plot(combined_df['timestamp'], combined_df['gas_kohm'], 'purple', linewidth=1, alpha=0.7)
ax4.set_ylabel('Gas Resistance (kΩ)', fontsize=11, fontweight='bold')
ax4.grid(True, alpha=0.3)
ax4.set_title('Air Quality (VOC Sensor)', fontsize=12)

# GPS Status (show when GPS was available)
ax5 = axes[4]
gps_available = combined_df['latitude'].notna() & combined_df['longitude'].notna()
ax5.scatter(combined_df[gps_available]['timestamp'], 
           [1]*gps_available.sum(), 
           c='orange', s=5, alpha=0.5, label='GPS Lock')
ax5.set_ylabel('GPS Status', fontsize=11, fontweight='bold')
ax5.set_yticks([0, 1])
ax5.set_yticklabels(['No Lock', 'Locked'])
ax5.grid(True, alpha=0.3)
ax5.set_title('GPS Lock Status', fontsize=12)
ax5.set_xlabel('Time', fontsize=11, fontweight='bold')

# Rotate x-axis labels for better readability
for ax in axes:
    ax.tick_params(axis='x', rotation=45)
    ax.margins(x=0.01)

plt.tight_layout()

# Save the plot
output_file = f'sensor_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"✓ Saved plot to: {output_file}")

# Show the plot
plt.show()

# Export combined data to a single CSV
output_csv = f'combined_sensor_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
combined_df.to_csv(output_csv, index=False)
print(f"✓ Saved combined data to: {output_csv}")

# Additional analysis: GPS coordinates if available
gps_data = combined_df[gps_available]
if len(gps_data) > 0:
    print(f"\nGPS Data: {len(gps_data)} readings with valid coordinates")
    print(f"Latitude range: {gps_data['latitude'].min():.6f} to {gps_data['latitude'].max():.6f}")
    print(f"Longitude range: {gps_data['longitude'].min():.6f} to {gps_data['longitude'].max():.6f}")
    print(f"Altitude range: {gps_data['altitude'].min():.1f}m to {gps_data['altitude'].max():.1f}m")
    
    # Create GPS map if we have coordinates
    fig2, ax = plt.subplots(figsize=(10, 8))
    scatter = ax.scatter(gps_data['longitude'], gps_data['latitude'], 
                        c=gps_data['temperature'], cmap='RdYlBu_r', 
                        s=50, alpha=0.6)
    ax.set_xlabel('Longitude', fontsize=12, fontweight='bold')
    ax.set_ylabel('Latitude', fontsize=12, fontweight='bold')
    ax.set_title('GPS Track with Temperature Overlay', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Temperature (°C)', fontsize=11)
    
    plt.tight_layout()
    gps_output = f'gps_track_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    plt.savefig(gps_output, dpi=300, bbox_inches='tight')
    print(f"✓ Saved GPS track to: {gps_output}")
    plt.show()
else:
    print("\nNo GPS data available in the logs.")

print("\n" + "="*60)
print("Analysis complete!")
print("="*60)
