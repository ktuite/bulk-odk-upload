#!/usr/bin/env python3
"""
Deploy ALL Nigeria settlements to ODK Central (~292K settlements with rate limiting)
"""
import csv
import time
from pyodk import Client

# Configuration - change these to deploy as a different form
FORM_ID = "nigeria_settlements_full"
FORM_TITLE = "Nigeria Settlements Full Dataset"

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
    print("\\n1. Uploading full settlements form...")
    r = client.post(f'/projects/{client.project_id}/forms', data=FORM_XML, headers={'Content-Type': 'application/xml'})
    if r.status_code == 200:
        print("✅ Form uploaded successfully")
    elif r.status_code == 409:
        print("⚠️  Form already exists")
    else:
        print(f"❌ Error uploading form: {r.status_code} - {r.text}")
        return
    
    # 2. Publish form
    print("\\n2. Publishing full settlements form...")
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
    
    # 3. Read and submit ALL settlement data
    data_file = 'ng_data/Settlements_in_Nigeria_587705110540301247.csv'
    print(f"\\n3. Reading ALL settlement data from {data_file}")
    print("⚠️  This will take a LONG time (~292K settlements)...")
    
    # First pass: count valid settlements and prepare submissions
    print("\\n   Preparing settlements data...")
    submissions = []
    skipped = 0
    
    with open(data_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, 1):
            if i % 10000 == 0:
                print(f"   Processing record {i:,}...")
                
            # Skip rows with invalid coordinates
            try:
                float(row['x'])
                float(row['y'])
            except (ValueError, TypeError):
                skipped += 1
                continue
                
            xml = create_submission_xml(row)
            submissions.append((xml, row))
    
    print(f"\\n   Prepared {len(submissions):,} valid settlements ({skipped:,} skipped due to invalid coordinates)")
    
    # 4. Submit ALL settlements with rate limiting
    print(f"\\n4. Submitting {len(submissions):,} settlement records with rate limiting...")
    print("   📊 Progress will be shown every 100 submissions")
    print("   ⏱️  Rate limiting: 0.1 second delay between submissions")
    print("   🚫 Press Ctrl+C to stop gracefully")
    
    batch_size = 100  # Report progress every 100 submissions
    submission_delay = 0.01  # 100ms delay between submissions
    total_submitted = 0
    start_time = time.time()
    
    try:
        for i, (xml, row) in enumerate(submissions):
            try:
                r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/submissions', 
                              data=xml, headers={'Content-Type': 'application/xml'})
                if r.status_code == 200:
                    total_submitted += 1
                    
                    # Progress reporting
                    if total_submitted % batch_size == 0:
                        elapsed = time.time() - start_time
                        rate = total_submitted / elapsed
                        remaining = len(submissions) - total_submitted
                        eta_seconds = remaining / rate if rate > 0 else 0
                        eta_hours = eta_seconds / 3600
                        
                        print(f"   📈 {total_submitted:,}/{len(submissions):,} submitted "
                              f"({total_submitted/len(submissions)*100:.1f}%) "
                              f"| Rate: {rate:.1f}/sec "
                              f"| ETA: {eta_hours:.1f}h")
                        
                        # Last settlement info
                        print(f"      Latest: {row['set_name']} in {row['lganame']}, {row['statename']}")
                    
                    # Rate limiting
                    time.sleep(submission_delay)
                    
                else:
                    print(f"     ❌ Submission {i+1} failed: {r.status_code} - {r.text}")
                    break
                    
            except KeyboardInterrupt:
                print(f"\\n\\n⚠️  Interrupted by user after {total_submitted:,} submissions")
                break
            except Exception as e:
                print(f"     ❌ Submission {i+1} error: {e}")
                # Continue with next submission for transient errors
                continue
                
    except KeyboardInterrupt:
        print(f"\\n\\n⚠️  Interrupted by user after {total_submitted:,} submissions")
    
    client.close()
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\\n{'='*60}")
    if total_submitted == len(submissions):
        print(f"✅ Successfully submitted ALL {total_submitted:,} settlement records!")
    else:
        print(f"⚠️  Submitted {total_submitted:,} out of {len(submissions):,} records")
        print(f"   ({total_submitted/len(submissions)*100:.1f}% completed)")
    
    print(f"⏱️  Total time: {total_time/3600:.1f} hours ({total_time/60:.1f} minutes)")
    print(f"📊 Average rate: {total_submitted/total_time:.1f} submissions/second")
    print(f"🎉 Deployment complete!")
    print(f"Form ID: {FORM_ID}")

if __name__ == "__main__":
    main()