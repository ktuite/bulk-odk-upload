#!/usr/bin/env python3
"""
Complete workflow: Upload form, publish it, and submit all PhotoCity data
"""
import csv
from pyodk import Client

# Configuration - change these to deploy as a different form
FORM_ID = "photocity_zones"
FORM_TITLE = "PhotoCity Game Zones"

# Form XML embedded in the script
FORM_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>{FORM_TITLE}</h:title>
    <model>
      <instance>
        <data id="{FORM_ID}" version="1">
          <zone_id/>
          <zone_name/>
          <zone_city/>
          <location/>
          <zoom/>
          <description/>
          <start_date/>
          <end_date/>
          <meta>
            <instanceID/>
          </meta>
        </data>
      </instance>
      <bind nodeset="/data/zone_id" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/zone_name" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/zone_city" type="string" readonly="true()"/>
      <bind nodeset="/data/location" type="geopoint" required="true()" readonly="true()"/>
      <bind nodeset="/data/zoom" type="string" readonly="true()"/>
      <bind nodeset="/data/description" type="string" readonly="true()"/>
      <bind nodeset="/data/start_date" type="date" readonly="true()"/>
      <bind nodeset="/data/end_date" type="date" readonly="true()"/>
      <bind nodeset="/data/meta/instanceID" type="string" required="true()" readonly="true()"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/data/zone_id">
      <label>Zone ID</label>
    </input>
    <input ref="/data/zone_name">
      <label>Zone Name</label>
    </input>
    <input ref="/data/zone_city">
      <label>City</label>
    </input>
    <input ref="/data/location">
      <label>Location</label>
    </input>
    <input ref="/data/zoom">
      <label>Zoom Level</label>
    </input>
    <input ref="/data/description">
      <label>Description</label>
    </input>
    <input ref="/data/start_date">
      <label>Start Date</label>
    </input>
    <input ref="/data/end_date">
      <label>End Date</label>
    </input>
  </h:body>
</h:html>"""

def create_submission_xml(row):
    """Create ODK submission XML from a zones CSV row"""
    # Generate location string from raw data
    location = f"{row['latitude']} {row['longitude']} 0 0"
    instance_id = f"uuid:{__import__('uuid').uuid4()}"
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<data xmlns:jr="http://openrosa.org/javarosa" id="{FORM_ID}" version="1">
  <zone_id>{row['zone_id']}</zone_id>
  <zone_name>{row['zone_name']}</zone_name>
  <zone_city>{row['zone_city']}</zone_city>
  <location>{location}</location>
  <zoom>{row['zoom']}</zoom>
  <description>{row['description']}</description>
  <start_date>{row['start_date']}</start_date>
  <end_date>{row['end_date']}</end_date>
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
    print(f"\n3. Loading and submitting data from zones.csv to {FORM_ID}...")
    zones = []
    with open('data/zones.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            zones.append(row)
    
    print(f"Submitting {len(zones)} zones...")
    
    success_count = 0
    for i, zone in enumerate(zones, 1):
        xml = create_submission_xml(zone)
        
        try:
            r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/submissions', xml)
            if r.status_code in [200, 201]:
                success_count += 1
                if i % 10 == 0:  # Progress every 10 submissions (fewer zones than models)
                    print(f"✓ {i}/{len(zones)} submitted")
        except Exception as e:
            print(f"✗ Error submitting {i}: {e}")
    
    print(f"\n🎉 Complete! {success_count}/{len(zones)} zones submitted to {FORM_ID}.")

if __name__ == "__main__":
    main()