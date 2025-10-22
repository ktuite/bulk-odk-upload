# Bulk ODK Upload Scripts

## Overview
Collection of Python scripts for bulk uploading various geospatial datasets to ODK Central, including PhotoCity game data, Nigeria administrative boundaries, settlements data, and other geographic datasets.

## Setup

### 1. Create and Activate Virtual Environment (Recommended)
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install pyodk
```

### 3. Configure ODK Central
Create `odk-config.toml` in this directory with your ODK Central credentials (don't check this file in)

```toml
[central]
base_url = "http://localhost:8383 or https://your-odk-server.com"
username = "your-email@example.com"
password = "your-password"
default_project_id = 1
```


### 4. Download Data Files
Some data is already in this repo. See individual data directories for download instructions

## Available Datasets

### PhotoCity Data
- **Location**: `photocity/` directory
- **Data**: Multiple deployment options for 3D models, zones, flags, and images (not all 100K, just ~3K imaages from the Smithsonian / National Mall zone)
- **Details**: See `photocity/README.md` for complete documentation

### Nigeria Administrative Data
- **Location**: `ng_data/` directory
- **Data**: Nigeria LGA boundaries (774 areas) and settlements (+200K)
- **Source**: [GRID3 Nigeria datasets](ng_data/README.md)

## Usage

**Prerequisites before running any script:**
1. Make sure you have activated your virtual environment: `source .venv/bin/activate`
2. Ensure `odk-config.toml` is configured with your ODK Central credentials
3. Optionally edit the `FORM_ID` variable in the deployment script if you want to send data to a new version of a form

### Running Scripts
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# PhotoCity scripts (run from photocity directory)
cd photocity/
python deploy_zones.py
python deploy_model_locations.py
python deploy_model_bounding_boxes.py
python deploy_si_images.py
python deploy_flags.py

# Nigeria data scripts small test ones (run from root directory)  
python deploy_ng_lga_test.py
python deploy_ng_settlements_test.py

# Nigeria data scripts (run from root directory)  
python deploy_ng_lga_boundaries.py
python deploy_ng_settlements_full.py
```
