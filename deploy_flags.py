#!/usr/bin/env python3
"""
Complete workflow: Upload form, publish it, and submit all PhotoCity data
"""
import csv
import json
from pyodk import Client

# Configuration - change these to deploy as a different form
FORM_ID = "photocity_flags"
FORM_TITLE = "PhotoCity Game Flags"

# Form XML embedded in the script
FORM_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<h:html xmlns="http://www.w3.org/2002/xforms" xmlns:h="http://www.w3.org/1999/xhtml" xmlns:jr="http://openrosa.org/javarosa" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <h:head>
    <h:title>{FORM_TITLE}</h:title>
    <model>
      <instance>
        <data id="{FORM_ID}" version="1">
          <flag_id/>
          <model_id/>
          <location/>
          <winning_team_id/>
          <winning_player_id/>
          <team1_score/>
          <team2_score/>
          <team3_score/>
          <team4_score/>
          <disputed/>
          <collectable/>
          <collector/>
          <meta>
            <instanceID/>
          </meta>
        </data>
      </instance>
      <bind nodeset="/data/flag_id" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/model_id" type="string" required="true()" readonly="true()"/>
      <bind nodeset="/data/location" type="geopoint" required="true()" readonly="true()"/>
      <bind nodeset="/data/winning_team_id" type="string" readonly="true()"/>
      <bind nodeset="/data/winning_player_id" type="string" readonly="true()"/>
      <bind nodeset="/data/team1_score" type="string" readonly="true()"/>
      <bind nodeset="/data/team2_score" type="string" readonly="true()"/>
      <bind nodeset="/data/team3_score" type="string" readonly="true()"/>
      <bind nodeset="/data/team4_score" type="string" readonly="true()"/>
      <bind nodeset="/data/disputed" type="string" readonly="true()"/>
      <bind nodeset="/data/collectable" type="string" readonly="true()"/>
      <bind nodeset="/data/collector" type="string" readonly="true()"/>
      <bind nodeset="/data/meta/instanceID" type="string" required="true()" readonly="true()"/>
    </model>
  </h:head>
  <h:body>
    <input ref="/data/flag_id">
      <label>Flag ID</label>
    </input>
    <input ref="/data/model_id">
      <label>Model ID</label>
    </input>
    <input ref="/data/location">
      <label>Location</label>
    </input>
    <input ref="/data/winning_team_id">
      <label>Winning Team ID</label>
    </input>
    <input ref="/data/winning_player_id">
      <label>Winning Player ID</label>
    </input>
    <input ref="/data/team1_score">
      <label>Team 1 Score</label>
    </input>
    <input ref="/data/team2_score">
      <label>Team 2 Score</label>
    </input>
    <input ref="/data/team3_score">
      <label>Team 3 Score</label>
    </input>
    <input ref="/data/team4_score">
      <label>Team 4 Score</label>
    </input>
    <input ref="/data/disputed">
      <label>Disputed</label>
    </input>
    <input ref="/data/collectable">
      <label>Collectable</label>
    </input>
    <input ref="/data/collector">
      <label>Collector</label>
    </input>
  </h:body>
</h:html>"""

def create_submission_xml(row):
    """Create ODK submission XML from a flags CSV row"""
    # Generate location string from raw data
    location = f"{row['latitude']} {row['longitude']} 0 0"
    instance_id = f"uuid:{__import__('uuid').uuid4()}"
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<data xmlns:jr="http://openrosa.org/javarosa" id="{FORM_ID}" version="1">
  <flag_id>{row['flag_id']}</flag_id>
  <model_id>{row['model_id']}</model_id>
  <location>{location}</location>
  <winning_team_id>{row['winning_team_id']}</winning_team_id>
  <winning_player_id>{row['winning_player_id']}</winning_player_id>
  <team1_score>{row['team1']}</team1_score>
  <team2_score>{row['team2']}</team2_score>
  <team3_score>{row['team3']}</team3_score>
  <team4_score>{row['team4']}</team4_score>
  <disputed>{row['disputed']}</disputed>
  <collectable>{row['collectable']}</collectable>
  <collector>{row['collector']}</collector>
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
    print(f"\n3. Loading and submitting data from flags.csv to {FORM_ID}...")
    flags = []
    with open('data/flags.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            flags.append(row)
    
    print(f"Submitting {len(flags)} flags...")
    
    success_count = 0
    for i, flag in enumerate(flags, 1):
        xml = create_submission_xml(flag)
        
        try:
            r = client.post(f'/projects/{client.project_id}/forms/{FORM_ID}/submissions', xml)
            if r.status_code in [200, 201]:
                success_count += 1
                if i % 100 == 0:  # Progress every 100 submissions (lots of flags)
                    print(f"✓ {i}/{len(flags)} submitted")
        except Exception as e:
            print(f"✗ Error submitting {i}: {e}")
    
    print(f"\n🎉 Complete! {success_count}/{len(flags)} flags submitted to {FORM_ID}.")

if __name__ == "__main__":
    main()