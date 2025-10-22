#!/usr/bin/env python3
"""
Complete workflow: Upload form, publish it, and submit all PhotoCity data
"""
import csv
from pyodk import Client

# Configuration - change these to deploy as a different form
FORM_ID = "model_bounding_boxes"
FORM_TITLE = "PhotoCity Model Bounding Boxes"

# Form XML embedded in the script
FORM_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>{FORM_TITLE}</h:title>
    <model>
      <instance>
        <data id="{FORM_ID}" version="1">
          <name/>
          <model_id/>
          <image_url/>
          <bounding_box/>
          <zone_id/>
          <color/>
          <meta>
            <instanceID/>
          </meta>
        </data>
      </instance>
      <bind nodeset="/data/name" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/model_id" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/image_url" type="string" readonly="true()"/>
      <bind nodeset="/data/bounding_box" type="geoshape" required="true()" readonly="true()"/>
      <bind nodeset="/data/zone_id" type="string" readonly="true()"/>
      <bind nodeset="/data/color" type="string" readonly="true()"/>
      <bind nodeset="/data/meta/instanceID" type="string" required="true()" readonly="true()"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/data/name">
      <label>Model Name</label>
    </input>
    <input ref="/data/model_id">
      <label>Model ID</label>
    </input>
    <input ref="/data/image_url">
      <label>Image URL</label>
    </input>
    <input ref="/data/bounding_box">
      <label>Bounding Box</label>
    </input>
    <input ref="/data/zone_id">
      <label>Zone ID</label>
    </input>
    <input ref="/data/color">
      <label>Color</label>
    </input>
  </h:body>
</h:html>"""

def create_submission_xml(row):
    """Create ODK submission XML with bounding box polygon from model_registry CSV row"""
    # Generate image URL and bounding box polygon from raw data
    image_url = f"https://s3-us-west-2.amazonaws.com/photocity-archive/render/{row['model_id']}/0"
    
    # Create bounding box polygon (rectangle)
    n, s, e, w = row['north'], row['south'], row['east'], row['west']
    bounding_box = f"{n} {w} 0 0;{n} {e} 0 0;{s} {e} 0 0;{s} {w} 0 0;{n} {w} 0 0"
    
    instance_id = f"uuid:{__import__('uuid').uuid4()}"
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<data xmlns:jr="http://openrosa.org/javarosa" id="{FORM_ID}" version="1">
  <name>{row['name']}</name>
  <model_id>{row['model_id']}</model_id>
  <image_url>{image_url}</image_url>
  <bounding_box>{bounding_box}</bounding_box>
  <zone_id>{row['zone_id']}</zone_id>
  <color>{row['color']}</color>
  <meta>
    <instanceID>{instance_id}</instanceID>
  </meta>
</data>"""

def main():
    print("Setting up ODK client...")
    client = Client(config_path="../odk-config.toml")
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
    print(f"\n3. Loading and submitting data from model_registry.csv to {FORM_ID}...")
    models = []
    with open('data/model_registry.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            models.append(row)
    
    print(f"Submitting {len(models)} models...")
    
    success_count = 0
    for i, model in enumerate(models, 1):
        xml = create_submission_xml(model)
        
        try:
            r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/submissions', xml)
            if r.status_code in [200, 201]:
                success_count += 1
                if i % 50 == 0:  # Progress every 50 submissions
                    print(f"✓ {i}/{len(models)} submitted")
        except Exception as e:
            print(f"✗ Error submitting {i}: {e}")
    
    print(f"\n🎉 Complete! {success_count}/{len(models)} models submitted to {FORM_ID}.")

if __name__ == "__main__":
    main()