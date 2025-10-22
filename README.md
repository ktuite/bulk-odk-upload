# Bulk ODK Upload Scripts

## Overview
Collection of Python scripts for bulk uploading various geospatial datasets to ODK Central, including PhotoCity game data, Nigeria administrative boundaries, settlements data, and other geographic datasets.

## Setup
1. **Install dependencies**: `pip install pyodk`
2. **Configure ODK**: Create `odk-config.toml` with your ODK Central credentials (see Configuration section below)
3. **Download data files**: See individual data directories for download instructions

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
1. **Configure form ID**: Edit the `FORM_ID` variable in each deployment script
2. **Run deployment**: `python deploy_<dataset>.py`
3. **Check ODK Central**: Forms and submissions will be created automatically

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