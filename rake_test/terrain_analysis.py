#!/usr/bin/env python3
"""
Terrain-Based Microclimate Analysis
Uses altitude, humidity, VOC to identify similar terrain and predict microclimates
across the broader Tilden landscape
"""

import pandas as pd
import numpy as np
from scipy.spatial import distance
from sklearn.cluster import KMeans


class TerrainAnalyzer:
    """Analyzes terrain patterns and predicts microclimates across landscape"""
    
    def __init__(self):
        self.terrain_clusters = None
        self.microclimate_model = None
        
    def analyze_terrain_patterns(self, data):
        """
        Cluster terrain based on altitude, humidity, temperature, VOC
        Returns terrain types and their characteristics
        """
        # Extract features for clustering
        features = data[['altitude', 'humidity', 'temperature', 'gas']].values
        
        # Normalize features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Cluster into terrain types (5 types: valley, low hill, mid hill, high hill, ridge)
        n_clusters = min(5, len(data) // 10)  # At least 10 points per cluster
        if n_clusters < 2:
            n_clusters = 2
            
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        data['terrain_type'] = kmeans.fit_predict(features_scaled)
        
        # Calculate terrain type characteristics
        terrain_profiles = []
        for cluster_id in range(n_clusters):
            cluster_data = data[data['terrain_type'] == cluster_id]
            
            profile = {
                'type_id': cluster_id,
                'name': self._name_terrain_type(cluster_data),
                'altitude_range': (cluster_data['altitude'].min(), cluster_data['altitude'].max()),
                'avg_altitude': cluster_data['altitude'].mean(),
                'avg_humidity': cluster_data['humidity'].mean(),
                'avg_temp': cluster_data['temperature'].mean(),
                'avg_voc': cluster_data['gas'].mean(),
                'point_count': len(cluster_data),
                'lat_range': (cluster_data['latitude'].min(), cluster_data['latitude'].max()),
                'lon_range': (cluster_data['longitude'].min(), cluster_data['longitude'].max())
            }
            terrain_profiles.append(profile)
        
        return data, terrain_profiles
    
    def _name_terrain_type(self, cluster_data):
        """Give meaningful names to terrain types based on characteristics"""
        alt = cluster_data['altitude'].mean()
        humid = cluster_data['humidity'].mean()
        
        if alt < 250:
            if humid > 70:
                return "🌊 Riparian Zone (Lake/Stream)"
            else:
                return "🌿 Valley Floor"
        elif alt < 300:
            if humid > 65:
                return "🌳 Moist Forest Slope"
            else:
                return "🏞️ Grassland Slope"
        elif alt < 350:
            if humid > 60:
                return "🌲 Mixed Forest Mid-Slope"
            else:
                return "☀️ Oak Savanna"
        else:
            if humid > 55:
                return "🌲 Upper Forest"
            else:
                return "⛰️ Exposed Ridgeline"
    
    def predict_microclimate_grid(self, data, terrain_profiles, grid_resolution=50):
        """
        Create a prediction grid across the landscape
        Predicts microclimate conditions for unsampled areas based on terrain similarity
        """
        # Define grid bounds (expand beyond sampled area)
        lat_min, lat_max = data['latitude'].min(), data['latitude'].max()
        lon_min, lon_max = data['longitude'].min(), data['longitude'].max()
        
        # Expand bounds by 20% to cover adjacent areas
        lat_range = lat_max - lat_min
        lon_range = lon_max - lon_min
        lat_min -= lat_range * 0.2
        lat_max += lat_range * 0.2
        lon_min -= lon_range * 0.2
        lon_max += lon_range * 0.2
        
        # Create grid
        lats = np.linspace(lat_min, lat_max, grid_resolution)
        lons = np.linspace(lon_min, lon_max, grid_resolution)
        
        predictions = []
        
        for lat in lats:
            for lon in lons:
                # Estimate altitude based on distance from known points
                # (In reality, you'd use DEM data, but we'll interpolate)
                predicted = self._predict_point_microclimate(lat, lon, data, terrain_profiles)
                if predicted:
                    predictions.append(predicted)
        
        return pd.DataFrame(predictions)
    
    def _predict_point_microclimate(self, lat, lon, data, terrain_profiles):
        """Predict microclimate for a single point based on nearby sampled points"""
        # Find 5 nearest sampled points
        distances = []
        for idx, row in data.iterrows():
            dist = np.sqrt((lat - row['latitude'])**2 + (lon - row['longitude'])**2)
            distances.append((dist, row))
        
        distances.sort(key=lambda x: x[0])
        nearest = distances[:5]
        
        if not nearest or nearest[0][0] > 0.01:  # Too far from any sample
            return None
        
        # Weighted average based on distance
        total_weight = sum([1 / (d[0] + 0.0001) for d in nearest])
        
        predicted_alt = sum([d[1]['altitude'] / (d[0] + 0.0001) for d in nearest]) / total_weight
        predicted_humid = sum([d[1]['humidity'] / (d[0] + 0.0001) for d in nearest]) / total_weight
        predicted_temp = sum([d[1]['temperature'] / (d[0] + 0.0001) for d in nearest]) / total_weight
        predicted_voc = sum([d[1]['gas'] / (d[0] + 0.0001) for d in nearest]) / total_weight
        
        # Determine terrain type
        terrain_type = None
        min_diff = float('inf')
        for profile in terrain_profiles:
            diff = abs(predicted_alt - profile['avg_altitude'])
            if diff < min_diff:
                min_diff = diff
                terrain_type = profile['name']
        
        return {
            'latitude': lat,
            'longitude': lon,
            'predicted_altitude': predicted_alt,
            'predicted_humidity': predicted_humid,
            'predicted_temperature': predicted_temp,
            'predicted_voc': predicted_voc,
            'terrain_type': terrain_type,
            'confidence': 1 / (nearest[0][0] + 0.001)  # Higher confidence for closer samples
        }
    
    def generate_fukuoka_insights(self, data, terrain_profiles, historical_data=None):
        """
        Generate Fukuoka-style permaculture insights based on terrain analysis
        """
        insights = []
        
        insights.append("═══ FUKUOKA WISDOM: DO-NOTHING FARMING INSIGHTS ═══\n")
        
        # Terrain diversity analysis
        insights.append(f"🌏 TERRAIN DIVERSITY: {len(terrain_profiles)} distinct microclimates identified")
        insights.append("   'Nature knows best - observe the land's natural patterns'\n")
        
        # Altitude-based recommendations
        for profile in terrain_profiles:
            insights.append(f"\n━━━ {profile['name']} ({profile['avg_altitude']:.0f}m elevation) ━━━")
            insights.append(f"   Points sampled: {profile['point_count']}")
            insights.append(f"   Humidity: {profile['avg_humidity']:.1f}%")
            insights.append(f"   Temperature: {profile['avg_temp']:.1f}°C")
            insights.append(f"   VOC/Soil Activity: {profile['avg_voc']:.0f}Ω")
            
            # Fukuoka-style recommendations
            if "Riparian" in profile['name'] or "Lake" in profile['name']:
                insights.append("   🌾 Action: Let water-loving natives establish naturally")
                insights.append("   🐄 Grazing: Limit to dry season to protect riparian vegetation")
                insights.append("   💧 Fukuoka says: 'Water is the blood of the earth'")
                
            elif "Moist Forest" in profile['name']:
                insights.append("   🌳 Action: Minimal intervention - forest is self-regulating")
                insights.append("   🐄 Grazing: Rotational, limited to prevent soil compaction")
                insights.append("   🍄 Fukuoka says: 'The forest teaches us everything'")
                
            elif "Grassland" in profile['name'] or "Savanna" in profile['name']:
                insights.append("   🌾 Action: Ideal for seed dispersal during wet season")
                insights.append("   🐄 Grazing: Optimal zone - mimics natural herbivore patterns")
                insights.append("   ☀️ Fukuoka says: 'Grass and grazing animals evolved together'")
                
            elif "Exposed" in profile['name'] or "Ridge" in profile['name']:
                insights.append("   ⛰️ Action: Hardy, drought-tolerant species only")
                insights.append("   🐄 Grazing: Light grazing, watch for erosion")
                insights.append("   💨 Fukuoka says: 'Wind shapes the strongest plants'")
        
        # Historical comparison if available
        if historical_data is not None and len(historical_data) > 0:
            insights.append("\n\n═══ HISTORICAL PATTERN ANALYSIS ═══")
            insights.append(f"   Comparing current conditions to {len(historical_data)} previous surveys...")
            
            current_avg_humid = data['humidity'].mean()
            hist_humid = [h['humidity'].mean() for h in historical_data]
            avg_hist_humid = np.mean(hist_humid)
            
            humid_change = current_avg_humid - avg_hist_humid
            if abs(humid_change) > 5:
                direction = "WETTER" if humid_change > 0 else "DRIER"
                insights.append(f"\n   ⚠️ TREND DETECTED: Landscape is {humid_change:+.1f}% {direction} than historical average")
                insights.append(f"   🌱 Adaptation: {'Reduce seeding in low areas' if humid_change > 0 else 'Focus seeding near water sources'}")
            else:
                insights.append("\n   ✓ Conditions stable - historical patterns holding")
        
        # Landscape-scale recommendations
        insights.append("\n\n═══ LANDSCAPE-SCALE FUKUOKA STRATEGY ═══")
        insights.append("   🌍 'Think like the land - work with gravity and water'")
        
        # Find altitude gradient
        alt_range = data['altitude'].max() - data['altitude'].min()
        insights.append(f"\n   Vertical gradient: {alt_range:.0f}m elevation change")
        
        if alt_range > 100:
            insights.append("   📊 Steep terrain detected:")
            insights.append("      → Upper zones: Browse plants for goats/sheep")
            insights.append("      → Mid slopes: Mixed grasses for cattle")
            insights.append("      → Lower zones: Deep-rooted plants for water retention")
        else:
            insights.append("   📊 Gentle terrain detected:")
            insights.append("      → Uniform seeding strategy appropriate")
            insights.append("      → Focus on soil building through managed grazing")
        
        insights.append("\n   🐄 'Let the animals do the work - they are nature's seeders'")
        insights.append("   🌱 'Scatter seeds before rain - let nature decide what grows'")
        
        return "\n".join(insights)
    
    def find_similar_terrain_areas(self, target_coords, data, terrain_profiles, search_radius_km=2):
        """
        Find areas with similar microclimates to a target location
        Useful for expanding seed dispersal beyond sampled trails
        """
        target_lat, target_lon = target_coords
        
        # Find nearest sampled point
        min_dist = float('inf')
        nearest_point = None
        for idx, row in data.iterrows():
            dist = np.sqrt((target_lat - row['latitude'])**2 + (target_lon - row['longitude'])**2)
            if dist < min_dist:
                min_dist = dist
                nearest_point = row
        
        if nearest_point is None:
            return []
        
        # Find all points with similar characteristics
        similar_areas = []
        target_alt = nearest_point['altitude']
        target_humid = nearest_point['humidity']
        
        for idx, row in data.iterrows():
            # Calculate similarity score
            alt_diff = abs(row['altitude'] - target_alt)
            humid_diff = abs(row['humidity'] - target_humid)
            
            # Similar if within 20m altitude and 10% humidity
            if alt_diff < 20 and humid_diff < 10:
                similar_areas.append({
                    'lat': row['latitude'],
                    'lon': row['longitude'],
                    'altitude': row['altitude'],
                    'humidity': row['humidity'],
                    'similarity_score': 100 - (alt_diff + humid_diff)
                })
        
        return sorted(similar_areas, key=lambda x: x['similarity_score'], reverse=True)
