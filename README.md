# PhotoCity Data for ODK

## Overview
Converting PhotoCity game data (crowdsourced 3D building models) into ODK forms and submissions for map testing.

## Files
- `data/model_registry.csv` - Original PhotoCity data (~290 3D models with locations)
- `deploy_model_locations.py` - Complete script: creates form, uploads, and submits all data
- `process_data.py` - Processes model_registry into clean CSV files (optional)
- `odk-config.toml` - ODK Central server configuration

## Usage
1. **Change form ID** (if needed): Edit `FORM_ID` variable at top of deploy script
2. **Run deployment**: `python deploy_model_locations.py`

This creates an ODK form with:
- Model names
- Model IDs  
- S3 image URLs (`https://s3-us-west-2.amazonaws.com/photocity-archive/render/{model_id}/0`)
- Geolocations (lat/lon points)
- Zone IDs and colors

## Data Format
Each submission includes location as `"lat lon 0 0"` for ODK geopoint display on maps.

## Status
✅ Successfully deployed 290 PhotoCity models to ODK Central project 48