#!/usr/bin/env python3
"""
Diagnose data quality issues in sensor logs.
Identifies missing data, outliers, and stability problems.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob

# Load log files
log_files = sorted(glob.glob('rake_log_*.csv'))
if not log_files:
    print("No log files found!")
    exit(1)

all_data = []
for file in log_files:
    df = pd.read_csv(file, comment='#')
    df['source_file'] = file
    all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)
combined_df['timestamp'] = pd.to_datetime(combined_df['timestamp'])
combined_df = combined_df.sort_values('timestamp')

print("="*70)
print("DATA QUALITY DIAGNOSTIC REPORT")
print("="*70)

# Check for missing/null values
print("\n1. MISSING DATA ANALYSIS")
print("-" * 70)
for col in ['temperature', 'humidity', 'pressure', 'gas']:
    null_count = combined_df[col].isna().sum()
    null_pct = (null_count / len(combined_df)) * 100
    print(f"{col:15s}: {null_count:4d} missing ({null_pct:5.2f}%)")

# Check for suspiciously constant values (might be simulated)
print("\n2. DATA VARIATION ANALYSIS")
print("-" * 70)
for col in ['temperature', 'humidity', 'pressure', 'gas']:
    data = combined_df[col].dropna()
    if len(data) > 0:
        std = data.std()
        mean = data.mean()
        cv = (std / mean) * 100 if mean != 0 else 0
        print(f"{col:15s}: Mean={mean:8.2f}, StdDev={std:8.2f}, CV={cv:5.2f}%")

# Identify outliers using IQR method
print("\n3. OUTLIER DETECTION (IQR Method)")
print("-" * 70)
outlier_indices = {}
for col in ['temperature', 'humidity', 'pressure', 'gas']:
    data = combined_df[col].dropna()
    if len(data) > 0:
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = combined_df[(combined_df[col] < lower_bound) | (combined_df[col] > upper_bound)]
        outlier_count = len(outliers)
        outlier_pct = (outlier_count / len(data)) * 100
        
        print(f"{col:15s}: {outlier_count:4d} outliers ({outlier_pct:5.2f}%)")
        print(f"                 Valid range: {lower_bound:.2f} to {upper_bound:.2f}")
        outlier_indices[col] = outliers.index.tolist()

# Check for sudden jumps (rate of change)
print("\n4. SUDDEN CHANGE DETECTION")
print("-" * 70)
for col in ['temperature', 'humidity', 'pressure', 'gas']:
    data = combined_df[col].dropna()
    if len(data) > 1:
        diff = data.diff().abs()
        large_changes = diff[diff > diff.quantile(0.95)]
        print(f"{col:15s}: {len(large_changes):4d} sudden jumps (>95th percentile)")
        if len(large_changes) > 0:
            print(f"                 Max change: {diff.max():.2f}")

# Check for simulated data patterns (sinusoidal = simulated)
print("\n5. SIMULATED DATA DETECTION")
print("-" * 70)
print("Checking for mathematical patterns that indicate simulated data...")

for col in ['temperature', 'humidity', 'pressure', 'gas']:
    data = combined_df[col].dropna().values
    if len(data) > 10:
        # Calculate autocorrelation at lag 1
        if len(data) > 1:
            autocorr = np.corrcoef(data[:-1], data[1:])[0, 1]
            
            # Very high autocorrelation might indicate smooth simulated data
            if autocorr > 0.99:
                print(f"{col:15s}: ⚠️  SUSPICIOUS - Very smooth (autocorr={autocorr:.4f})")
            else:
                print(f"{col:15s}: ✓  Looks real (autocorr={autocorr:.4f})")

# Time series stability - check first vs last quartile
print("\n6. TEMPORAL STABILITY")
print("-" * 70)
for col in ['temperature', 'humidity', 'pressure', 'gas']:
    data = combined_df[col].dropna()
    if len(data) > 20:
        quarter_size = len(data) // 4
        first_quarter = data.iloc[:quarter_size]
        last_quarter = data.iloc[-quarter_size:]
        
        mean_shift = last_quarter.mean() - first_quarter.mean()
        std_ratio = last_quarter.std() / first_quarter.std() if first_quarter.std() != 0 else 1
        
        print(f"{col:15s}: Mean shift={mean_shift:+7.2f}, StdDev ratio={std_ratio:.2f}")

# GPS data quality
print("\n7. GPS DATA QUALITY")
print("-" * 70)
gps_valid = combined_df['latitude'].notna() & combined_df['longitude'].notna()
gps_count = gps_valid.sum()
gps_pct = (gps_count / len(combined_df)) * 100
print(f"Valid GPS readings: {gps_count}/{len(combined_df)} ({gps_pct:.1f}%)")

if gps_count > 0:
    gps_data = combined_df[gps_valid]
    lat_range = gps_data['latitude'].max() - gps_data['latitude'].min()
    lon_range = gps_data['longitude'].max() - gps_data['longitude'].min()
    print(f"Latitude range:  {lat_range:.6f}° ({lat_range * 111:.1f} km)")
    print(f"Longitude range: {lon_range:.6f}° ({lon_range * 111:.1f} km)")
    
    if lat_range < 0.001 and lon_range < 0.001:
        print("⚠️  GPS stationary (very small movement)")

# Create visualization of data quality
fig, axes = plt.subplots(4, 1, figsize=(14, 10))
fig.suptitle('Data Quality Analysis', fontsize=16, fontweight='bold')

for idx, col in enumerate(['temperature', 'humidity', 'pressure', 'gas']):
    ax = axes[idx]
    
    # Plot data
    ax.plot(combined_df['timestamp'], combined_df[col], 'b-', linewidth=0.5, alpha=0.5, label='Data')
    
    # Mark outliers
    if col in outlier_indices and outlier_indices[col]:
        outlier_data = combined_df.loc[outlier_indices[col]]
        ax.scatter(outlier_data['timestamp'], outlier_data[col], 
                  c='red', s=20, zorder=5, label='Outliers')
    
    # Mark missing data
    missing = combined_df[combined_df[col].isna()]
    if len(missing) > 0:
        ax.scatter(missing['timestamp'], [combined_df[col].mean()] * len(missing),
                  c='orange', marker='x', s=30, zorder=5, label='Missing')
    
    ax.set_ylabel(col, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=8)
    ax.tick_params(axis='x', rotation=45)

plt.tight_layout()
output_file = 'data_quality_analysis.png'
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Saved diagnostic plot to: {output_file}")
plt.show()

print("\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)

# Provide recommendations based on findings
recommendations = []

for col in ['temperature', 'humidity', 'pressure', 'gas']:
    null_pct = (combined_df[col].isna().sum() / len(combined_df)) * 100
    if null_pct > 10:
        recommendations.append(f"• High missing data for {col} ({null_pct:.1f}%) - Check I2C connection")

for col in ['temperature', 'humidity', 'pressure', 'gas']:
    data = combined_df[col].dropna().values
    if len(data) > 1:
        autocorr = np.corrcoef(data[:-1], data[1:])[0, 1]
        if autocorr > 0.99:
            recommendations.append(f"• {col} data looks simulated - Real sensor may not be working")

if gps_pct < 10:
    recommendations.append(f"• Very low GPS lock rate ({gps_pct:.1f}%) - Check GPS antenna/connection")

if not recommendations:
    recommendations.append("• Data quality looks good overall!")

for rec in recommendations:
    print(rec)

print("="*70)
