# Nigeria Data - ODK Deployment

## Overview
Successfully processed and deployed Nigeria LGA (Local Government Area) boundary data and settlements data to ODK Central.

## Required Data Files
Download these files and place them in the `ng_data/` directory before running the deployment scripts:

### LGA Boundaries
- **File**: `NGA_LGA_Boundaries_2_-2954311847614747693.geojson`
- **Source**: [GRID3 Nigeria Operational LGA Boundaries](https://data.grid3.org/datasets/GRID3::grid3-nga-operational-lga-boundaries/about)
- **Format**: Download as GeoJSON

### Settlements
- **File**: `Settlements_in_Nigeria_587705110540301247.csv`
- **Source**: [GRID3 Nigeria Settlement Names](https://data.grid3.org/datasets/GRID3::grid3-nga-settlement-names/about)
- **Format**: Download as CSV

## Data Processing
- **Script**: `process_ng_data.py`
- **Output**: `ng_data/lga_boundaries.csv`

## Statistics
- **Total LGAs**: 774
- **Total States**: 37 (including FCT)
- **Format**: GeoJSON polygons converted to ODK geoshape format

### State Breakdown
```
Abia: 17 LGAs          Adamawa: 21 LGAs       Akwa Ibom: 31 LGAs     
Anambra: 21 LGAs       Bauchi: 20 LGAs        Bayelsa: 8 LGAs        
Benue: 23 LGAs         Borno: 27 LGAs         Cross River: 18 LGAs   
Delta: 25 LGAs         Ebonyi: 13 LGAs        Edo: 18 LGAs           
Ekiti: 16 LGAs         Enugu: 17 LGAs         FCT: 6 LGAs            
Gombe: 11 LGAs         Imo: 27 LGAs           Jigawa: 27 LGAs        
Kaduna: 23 LGAs        Kano: 44 LGAs          Katsina: 34 LGAs       
Kebbi: 21 LGAs         Kogi: 21 LGAs          Kwara: 16 LGAs         
Lagos: 20 LGAs         Nasarawa: 13 LGAs      Niger: 25 LGAs         
Ogun: 20 LGAs          Ondo: 18 LGAs          Osun: 30 LGAs          
Oyo: 33 LGAs           Plateau: 17 LGAs       Rivers: 23 LGAs        
Sokoto: 23 LGAs        Taraba: 16 LGAs        Yobe: 17 LGAs          
Zamfara: 14 LGAs
```

## ODK Form Details
- **Form ID**: `nigeria_lga_boundaries`
- **Form Title**: Nigeria LGA Boundaries
- **Deployment Script**: `deploy_ng_lga_boundaries.py`

### Form Fields
- `lga_id`: Unique LGA identifier (e.g., "nga_lg_20001")
- `lga_name`: LGA name (e.g., "Aba North")
- `boundary`: Full polygon boundary in ODK geoshape format
- `state_name`: State name (e.g., "Abia")
- `state_code`: State code (e.g., "AB")

## Data Format
Each boundary is stored as an ODK geoshape - a semicolon-separated list of coordinates in the format:
```
lat lng alt acc;lat lng alt acc;...
```

## Usage
1. **Process Data**: `python process_ng_data.py`
2. **Deploy to ODK**: `python deploy_ng_lga_boundaries.py`

## Files Created
- `ng_data/lga_boundaries.csv` - Processed boundary data
- `deploy_ng_lga_boundaries.py` - ODK deployment script

## Notes
- All 774 LGA boundaries successfully uploaded to ODK Central
- Boundaries include full polygon geometry suitable for mapping applications
- Data follows Nigeria's official LGA structure as of the source dataset timestamp