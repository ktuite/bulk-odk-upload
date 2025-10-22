#!/usr/bin/env python3
"""
Deploy a small test set of Nigeria settlements to ODK Central (100 settlements only)
"""
import csv
from pyodk import Client

# Configuration - change these to deploy as a different form
FORM_ID = "nigeria_settlements_test"
FORM_TITLE = "Nigeria Settlements Test (100 settlements)"

# Form XML embedded in the script
FORM_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>{FORM_TITLE}</h:title>
    <model>
      <instance>
        <data id="{FORM_ID}" version="1">
          <settlement_id/>
          <settlement_name/>
          <location/>
          <ward_name/>
          <lga_name/>
          <state_name/>
          <state_code/>
          <meta>
            <instanceID/>
          </meta>
        </data>
      </instance>
      <bind nodeset="/data/settlement_id" type="string" required="true()"/>
      <bind nodeset="/data/settlement_name" type="string" required="true()"/>
      <bind nodeset="/data/location" type="geopoint" required="true()"/>
      <bind nodeset="/data/ward_name" type="string" required="true()"/>
      <bind nodeset="/data/lga_name" type="string" required="true()"/>
      <bind nodeset="/data/state_name" type="string" required="true()"/>
      <bind nodeset="/data/state_code" type="string" required="true()"/>
      <bind nodeset="/data/meta/instanceID" type="string" readonly="true()" calculate="concat('uuid:', uuid())"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/data/settlement_id">
      <label>Settlement ID</label>
    </input>
    <input ref="/data/settlement_name">
      <label>Settlement Name</label>
    </input>
    <input ref="/data/location">
      <label>Location</label>
      <hint>GPS coordinates of the settlement</hint>
    </input>
    <input ref="/data/ward_name">
      <label>Ward Name</label>
    </input>
    <input ref="/data/lga_name">
      <label>LGA Name</label>
    </input>
    <input ref="/data/state_name">
      <label>State Name</label>
    </input>
    <input ref="/data/state_code">
      <label>State Code</label>
    </input>
  </h:body>
</h:html>"""

def create_submission_xml(row):
    """Create ODK submission XML from a settlements CSV row"""
    instance_id = f"uuid:{__import__('uuid').uuid4()}"
    
    # Create settlement ID from existing data
    settlement_id = f"nga_set_{row['statecode'].lower()}_{row['set_id']}"
    
    # Create location from x,y coordinates (ODK format: lat lng alt acc)
    try:
        x = float(row['x'])  # longitude
        y = float(row['y'])  # latitude
        location = f"{y} {x} 0 0"
    except (ValueError, TypeError):
        location = "0 0 0 0"  # fallback
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<data xmlns:jr="http://openrosa.org/javarosa" id="{FORM_ID}" version="1">
  <settlement_id>{settlement_id}</settlement_id>
  <settlement_name>{row['set_name']}</settlement_name>
  <location>{location}</location>
  <ward_name>{row['wardname']}</ward_name>
  <lga_name>{row['lganame']}</lga_name>
  <state_name>{row['statename']}</state_name>
  <state_code>{row['statecode']}</state_code>
  <meta>
    <instanceID>{instance_id}</instanceID>
  </meta>
</data>"""

def main():
    print("Setting up ODK client...")
    client = Client(config_path="odk-config.toml")
    client.open()
    
    # 1. Upload form
    print("\\n1. Uploading test settlements form...")
    r = client.post(f'/projects/{client.project_id}/forms', data=FORM_XML, headers={'Content-Type': 'application/xml'})
    if r.status_code == 200:
        print("✅ Form uploaded successfully")
    elif r.status_code == 409:
        print("⚠️  Form already exists")
    else:
        print(f"❌ Error uploading form: {r.status_code} - {r.text}")
        return
    
    # 2. Publish form
    print("\\n2. Publishing test settlements form...")
    r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/draft/publish')
    if r.status_code == 200:
        print("✅ Form published successfully")
    elif r.status_code == 409:
        print("⚠️  Form already published")
    elif r.status_code == 404:
        print("⚠️  Form already published or no draft to publish")
    else:
        print(f"❌ Error publishing form: {r.status_code} - {r.text}")
        return
    
    # 3. Read and submit TEST data (only first 100 settlements)
    data_file = 'ng_data/Settlements_in_Nigeria_587705110540301247.csv'
    print(f"\\n3. Reading TEST data from {data_file} (first 100 settlements only)")
    
    submissions = []
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if count >= 100:  # Only take first 100 settlements
                break
            
            # Skip rows with invalid coordinates
            try:
                float(row['x'])
                float(row['y'])
            except (ValueError, TypeError):
                continue
                
            xml = create_submission_xml(row)
            submissions.append(xml)
            print(f"   Selected: {row['set_name']} in {row['lganame']} ({row['statename']})")
            count += 1
    
    print(f"\\n4. Submitting {len(submissions)} TEST settlement records...")
    
    # Submit in batches
    batch_size = 10
    total_submitted = 0
    
    for i in range(0, len(submissions), batch_size):
        batch = submissions[i:i + batch_size]
        print(f"   Submitting batch {i//batch_size + 1} ({len(batch)} records)...")
        
        for j, xml in enumerate(batch):
            try:
                r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/submissions', 
                              data=xml, headers={'Content-Type': 'application/xml'})
                if r.status_code == 200:
                    total_submitted += 1
                else:
                    print(f"     ❌ Submission failed: {r.status_code} - {r.text}")
                    break
            except Exception as e:
                print(f"     ❌ Submission error: {e}")
                break
    
    client.close()
    
    if total_submitted == len(submissions):
        print(f"\\n✅ Successfully submitted all {total_submitted} TEST settlement records!")
    else:
        print(f"\\n⚠️  Submitted {total_submitted} out of {len(submissions)} records")
    
    print(f"\\n🎉 Test deployment complete!")
    print(f"Form ID: {FORM_ID}")
    print(f"You can view the test settlements form at your ODK Central server")

if __name__ == "__main__":
    main()