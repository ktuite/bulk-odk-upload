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
Create `odk-config.toml` with your ODK Central credentials (see Configuration section below)

### 4. Download Data Files
See individual data directories for download instructions

## Available Datasets

### PhotoCity Data
- **Location**: `photocity/` directory
- **Scripts**: Multiple deployment options for 3D models, zones, flags, and Smithsonian images
- **Details**: See `photocity/README.md` for complete documentation

### Nigeria Administrative Data
- **Scripts**: `deploy_ng_lga_boundaries.py`, `deploy_ng_settlements_full.py`, `deploy_ng_settlements_test.py`
- **Data**: Nigeria LGA boundaries (774 areas) and settlement names
- **Source**: [GRID3 Nigeria datasets](ng_data/README.md)

## Usage

**Prerequisites before running any script:**
1. Make sure you have activated your virtual environment: `source .venv/bin/activate`
2. Ensure `odk-config.toml` is configured with your ODK Central credentials
3. Edit the `FORM_ID` variable in the deployment script you want to run

### Running Scripts
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# PhotoCity scripts (run from root directory)
python photocity/deploy_zones.py
python photocity/deploy_flags.py
python photocity/deploy_model_locations.py
python photocity/deploy_model_bounding_boxes.py
python photocity/deploy_si_images.py

# Nigeria data scripts (run from root directory)  
python deploy_ng_lga_boundaries.py
python deploy_ng_lga_test.py
python deploy_ng_settlements_full.py
python deploy_ng_settlements_test.py
```

**Note**: Forms and submissions will be created automatically in ODK Central

## Data Processing
- `process_data.py` - Process PhotoCity model registry
- `process_ng_data.py` - Convert Nigeria GeoJSON boundaries to ODK format

## Configuration
Create `odk-config.toml` with your ODK Central server details:
```toml
[central]
base_url = "https://your-odk-server.com"
username = "your-email@example.com"
password = "your-password"
default_project_id = 1
```
**Note**: Keep this file secure and don't commit it to version control (it's already in .gitignore)