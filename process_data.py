#!/usr/bin/env python3
import csv
import uuid

# Read and process data
locations = []
bboxes = []

with open('data/model_registry.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # Model location (point)
        location = f"{row['lat']} {row['lng']} 0 0"
        locations.append([
            row['model_id'], row['name'], location, 
            row['zone_id'], row['color'], f"uuid:{uuid.uuid4()}"
        ])
        
        # Model bounding box (polygon)
        n, s, e, w = row['north'], row['south'], row['east'], row['west']
        points = [f"{n} {w} 0 0", f"{n} {e} 0 0", f"{s} {e} 0 0", f"{s} {w} 0 0", f"{n} {w} 0 0"]
        bbox = ";".join(points)
        bboxes.append([
            row['model_id'], row['name'], bbox,
            row['zone_id'], row['color'], f"uuid:{uuid.uuid4()}"
        ])

# Write locations CSV
with open('data/model_locations.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['model_id', 'name', 'location', 'zone_id', 'color', 'instance_id'])
    writer.writerows(locations)

# Write bounding boxes CSV  
with open('data/model_bounding_boxes.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['model_id', 'name', 'bounding_box', 'zone_id', 'color', 'instance_id'])
    writer.writerows(bboxes)

print(f"Created {len(locations)} records each:")
print("- data/model_locations.csv")
print("- data/model_bounding_boxes.csv")