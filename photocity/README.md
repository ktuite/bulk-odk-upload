# PhotoCity Data - ODK Deployment

## Overview
PhotoCity was a crowdsourced 3D building reconstruction game. This directory contains scripts to deploy various PhotoCity datasets to ODK Central for map testing and visualization.

## Available Datasets

### 3D Building Models
- **Scripts**: 
  - `deploy_model_locations.py` - Deploy models as point locations
  - `deploy_model_bounding_boxes.py` - Deploy models with bounding box polygons
- **Data**: `data/model_registry.csv` - 290 crowdsourced 3D building models with locations
- **Features**: S3 image URLs, geolocations, zone classifications

### Geographic Zones
- **Script**: `deploy_zones.py`
- **Data**: `data/zones.csv` - Zone classifications and boundaries
- **Features**: Zone polygons, colors, and metadata

### Flags/Markers
- **Script**: `deploy_flags.py`
- **Data**: `data/flags.csv` - Flag/marker locations and metadata
- **Features**: Point locations with flag data

### Smithsonian Images
- **Script**: `deploy_si_images.py`
- **Data**: `data/si_images.csv` - Smithsonian Institution image locations
- **Features**: Geolocated historical images

## Usage
1. **Configure ODK**: Ensure `../odk-config.toml` is set up with your ODK Central credentials
2. **Choose dataset**: Pick the appropriate deployment script for your needs
3. **Edit form ID**: Update the `FORM_ID` variable in the script if needed
4. **Run deployment**: `python deploy_<dataset>.py`

## Data Format
All datasets are converted to ODK-compatible formats:
- **Points**: `"lat lon 0 0"` for geopoint display
- **Polygons**: Semicolon-separated coordinate lists for geoshape fields
- **Images**: Direct S3 URLs for image display