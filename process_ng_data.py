#!/usr/bin/env python3
"""
Process Nigeria LGA boundary data for ODK forms
"""
import json
import csv
import uuid

def load_nigeria_geojson():
    """Load the Nigeria LGA boundaries GeoJSON file"""
    with open('ng_data/NGA_LGA_Boundaries_2_-2954311847614747693.geojson', 'r') as f:
        return json.load(f)

def polygon_to_odk_geoshape(coordinates):
    """Convert GeoJSON polygon coordinates to ODK geoshape format"""
    if not coordinates or len(coordinates) == 0:
        return ""
    
    # Get the exterior ring (first coordinate array)
    exterior = coordinates[0]
    
    # Handle malformed coordinates where first point is nested
    if len(exterior) > 0 and isinstance(exterior[0], list) and len(exterior[0]) > 0 and isinstance(exterior[0][0], list):
        # This is a malformed structure - flatten it
        print(f"  Warning: Detected malformed coordinates, attempting to flatten...")
        exterior = exterior[0]  # Take the nested array
    
    # Convert to ODK format: "lat lng alt acc;lat lng alt acc;..."
    points = []
    for point in exterior:
        if len(point) >= 2:
            lng, lat = point[0], point[1]
            # ODK format: lat lng altitude accuracy
            points.append(f"{lat} {lng} 0 0")
    
    return ";".join(points)

def main():
    print("Processing Nigeria LGA boundary data...")
    
    # Load GeoJSON data
    geojson_data = load_nigeria_geojson()
    
    # Create output list for boundaries
    lga_boundaries = []
    state_summary = {}
    
    # Process each LGA feature
    for feature in geojson_data['features']:
        props = feature['properties']
        geometry = feature['geometry']
        
        # Extract LGA information
        lga_name = props.get('lganame', 'Unknown')
        lga_code = props.get('lgacode', '')
        state_name = props.get('statename', 'Unknown')
        state_code = props.get('statecode', '')
        
        # Generate unique ID
        lga_id = f"nga_{state_code.lower()}_{lga_code}"
        instance_id = f"uuid:{uuid.uuid4()}"
        
        # Get boundary as geoshape
        boundary = polygon_to_odk_geoshape(geometry['coordinates'])
        
        # LGA boundary (full polygon)
        lga_boundaries.append([
            lga_id, lga_name, boundary, state_name, state_code, instance_id
        ])
        
        # Track state statistics
        if state_name not in state_summary:
            state_summary[state_name] = 0
        state_summary[state_name] += 1
    
    # Write CSV file
    print("Writing CSV file...")
    
    # LGA boundaries (full polygons)
    with open('ng_data/lga_boundaries.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['lga_id', 'lga_name', 'boundary', 'state_name', 'state_code', 'instance_id'])
        writer.writerows(lga_boundaries)
    
    print(f"\nProcessed {len(lga_boundaries)} LGAs from {len(state_summary)} states:")
    for state, count in sorted(state_summary.items()):
        print(f"  {state}: {count} LGAs")
    
    print("\nCreated file:")
    print("- ng_data/lga_boundaries.csv")

if __name__ == "__main__":
    main()