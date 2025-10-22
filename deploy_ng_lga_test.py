#!/usr/bin/env python3
"""
Deploy a small test set of Nigeria LGA boundaries to ODK Central (5 LGAs only)
"""
import csv
from pyodk import Client

# Configuration - change these to deploy as a different form
FORM_ID = "nigeria_lga_test"
FORM_TITLE = "Nigeria LGA Test (5 LGAs)"

# Form XML embedded in the script
FORM_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>{FORM_TITLE}</h:title>
    <model>
      <instance>
        <data id="{FORM_ID}" version="1">
          <lga_id/>
          <lga_name/>
          <boundary/>
          <state_name/>
          <state_code/>
          <meta>
            <instanceID/>
          </meta>
        </data>
      </instance>
      <bind nodeset="/data/lga_id" type="string" required="true()"/>
      <bind nodeset="/data/lga_name" type="string" required="true()"/>
      <bind nodeset="/data/boundary" type="geoshape" required="true()"/>
      <bind nodeset="/data/state_name" type="string" required="true()"/>
      <bind nodeset="/data/state_code" type="string" required="true()"/>
      <bind nodeset="/data/meta/instanceID" type="string" readonly="true()" calculate="concat('uuid:', uuid())"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/data/lga_id">
      <label>LGA ID</label>
    </input>
    <input ref="/data/lga_name">
      <label>LGA Name</label>
    </input>
    <input ref="/data/boundary">
      <label>LGA Boundary</label>
      <hint>Draw or import the LGA boundary polygon</hint>
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
    """Create ODK submission XML from an LGA boundaries CSV row"""
    instance_id = f"uuid:{__import__('uuid').uuid4()}"
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<data xmlns:jr="http://openrosa.org/javarosa" id="{FORM_ID}" version="1">
  <lga_id>{row['lga_id']}</lga_id>
  <lga_name>{row['lga_name']}</lga_name>
  <boundary>{row['boundary']}</boundary>
  <state_name>{row['state_name']}</state_name>
  <state_code>{row['state_code']}</state_code>
  <meta>
    <instanceID>{instance_id}</instanceID>
  </meta>
</data>"""

def main():
    print("Setting up ODK client...")
    client = Client(config_path="odk-config.toml")
    client.open()
    
    # 1. Upload form
    print("\\n1. Uploading test form...")
    r = client.post(f'/projects/{client.project_id}/forms', data=FORM_XML, headers={'Content-Type': 'application/xml'})
    if r.status_code == 200:
        print("✅ Form uploaded successfully")
    elif r.status_code == 409:
        print("⚠️  Form already exists")
    else:
        print(f"❌ Error uploading form: {r.status_code} - {r.text}")
        return
    
    # 2. Publish form
    print("\\n2. Publishing test form...")
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
    
    # 3. Read and submit TEST data (only first 5 LGAs)
    data_file = 'ng_data/lga_boundaries.csv'
    print(f"\\n3. Reading TEST data from {data_file} (first 5 LGAs only)")
    
    submissions = []
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            if count >= 5:  # Only take first 5 LGAs
                break
            xml = create_submission_xml(row)
            submissions.append(xml)
            print(f"   Selected: {row['lga_name']} ({row['state_name']})")
            count += 1
    
    print(f"\\n4. Submitting {len(submissions)} TEST LGA boundary records...")
    
    total_submitted = 0
    for i, xml in enumerate(submissions, 1):
        try:
            r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/submissions', 
                          data=xml, headers={'Content-Type': 'application/xml'})
            if r.status_code == 200:
                total_submitted += 1
                print(f"   ✅ Submitted {i}/{len(submissions)}")
            else:
                print(f"   ❌ Submission {i} failed: {r.status_code} - {r.text}")
                break
        except Exception as e:
            print(f"   ❌ Submission {i} error: {e}")
            break
    
    client.close()
    
    if total_submitted == len(submissions):
        print(f"\\n✅ Successfully submitted all {total_submitted} TEST LGA boundary records!")
    else:
        print(f"\\n⚠️  Submitted {total_submitted} out of {len(submissions)} records")
    
    print(f"\\n🎉 Test deployment complete!")
    print(f"Form ID: {FORM_ID}")
    print(f"You can view the test form at your ODK Central server")

if __name__ == "__main__":
    main()