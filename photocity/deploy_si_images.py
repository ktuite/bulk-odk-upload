#!/usr/bin/env python3
"""
Complete workflow: Upload form, publish it, and submit all PhotoCity data
"""
import csv
from pyodk import Client

# Configuration - change these to deploy as a different form
FORM_ID = "smithsonian_images_filtered"
FORM_TITLE = "Smithsonian Images (Valid Coordinates Only)"

# Form XML embedded in the script
FORM_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>{FORM_TITLE}</h:title>
    <model>
      <instance>
        <data id="{FORM_ID}" version="1">
          <image_id/>
          <player_id/>
          <location/>
          <name/>
          <image_url/>
          <meta>
            <instanceID/>
          </meta>
        </data>
      </instance>
      <bind nodeset="/data/image_id" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/player_id" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/location" type="geopoint" required="true()" readonly="true()"/>
      <bind nodeset="/data/name" type="string" readonly="true()"/>
      <bind nodeset="/data/image_url" type="string" readonly="true()"/>
      <bind nodeset="/data/meta/instanceID" type="string" required="true()" readonly="true()"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/data/image_id">
      <label>Image ID</label>
    </input>
    <input ref="/data/player_id">
      <label>Player ID</label>
    </input>
    <input ref="/data/location">
      <label>Location</label>
    </input>
    <input ref="/data/name">
      <label>Building Name</label>
    </input>
    <input ref="/data/image_url">
      <label>Image URL</label>
    </input>
  </h:body>
</h:html>"""

def create_submission_xml(row):
    """Create ODK submission XML from a Smithsonian images CSV row"""
    # Generate location string from raw data (note: CSV uses 'lat'/'lng' instead of 'latitude'/'longitude')
    location = f"{row['lat']} {row['lng']} 0 0"
    instance_id = f"uuid:{__import__('uuid').uuid4()}"
    
    # Generate S3 image URL
    image_url = f"https://s3-us-west-2.amazonaws.com/photocity-archive/images/small/{row['image_id']}"
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<data xmlns:jr="http://openrosa.org/javarosa" id="{FORM_ID}" version="1">
  <image_id>{row['image_id']}</image_id>
  <player_id>{row['player_id']}</player_id>
  <location>{location}</location>
  <name>{row['name']}</name>
  <image_url>{image_url}</image_url>
  <meta>
    <instanceID>{instance_id}</instanceID>
  </meta>
</data>"""

def main():
    print("Setting up ODK client...")
    client = Client(config_path="odk-config.toml")
    client.open()
    
    # 1. Upload form
    print("\n1. Uploading form...")
    r = client.post(f'/projects/{client.project_id}/forms', data=FORM_XML, headers={'Content-Type': 'application/xml'})
    print(f"Upload: {r.status_code}")
    
    # 2. Publish form  
    print("\n2. Publishing form...")
    r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/draft/publish')
    print(f"Publish: {r.status_code}")
    
    # 3. Submit data
    print(f"\n3. Loading and submitting data from si_images.csv to {FORM_ID}...")
    images = []
    with open('data/si_images.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Only include images with real lat/lng coordinates (not 0,0)
            if row['lat'] != '0' and row['lng'] != '0':
                images.append(row)
    
    print(f"Submitting {len(images)} Smithsonian images with valid coordinates...")
    
    success_count = 0
    for i, image in enumerate(images, 1):
        xml = create_submission_xml(image)
        
        try:
            r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/submissions', xml)
            if r.status_code in [200, 201]:
                success_count += 1
                if i % 100 == 0:  # Progress every 100 submissions
                    print(f"✓ {i}/{len(images)} submitted")
        except Exception as e:
            print(f"✗ Error submitting {i}: {e}")
    
    print(f"\n🎉 Complete! {success_count}/{len(images)} Smithsonian images submitted to {FORM_ID}.")

if __name__ == "__main__":
    main()