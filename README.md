# Land Use Raster Processing Script

## Overview

This Python script is designed for comprehensive geospatial data processing, specifically for handling multiple land use datasets, filtering, merging, and converting them into a single priority-based raster file.

## Features

- Processes multiple land use datasets:
  - Crops 2024
  - Forest 2022
  - Forest Plots (VMT_MKD)
  - Abandoned Lands 2024
  - Land Use (GDR) 2024
  - Impervious Surfaces 2024

- Advanced geospatial processing capabilities:
  - CRS validation and reprojection
  - Geometry cleaning
  - Priority-based layer merging
  - Rasterization with configurable resolution
  - Comprehensive logging

## Prerequisites

### Python Dependencies
- geopandas
- pandas
- numpy
- rasterio
- fiona
- openpyxl (for Excel file reading)

### Installation

1. Clone the repository
2. Create a virtual environment (recommended)
3. Install required packages:
   ```bash
   pip install geopandas pandas numpy rasterio fiona openpyxl
   ```

## Configuration

### settings.py
Create a `settings.py` file with the following configuration:

```python
# Paths to input data
boundary_gpkg = "/path/to/boundary.gpkg"
input_layers = {
    "crops": "/path/to/crops2024.gpkg",
    "forest": "/path/to/forest2022.gpkg",
    "vmt": "/path/to/VMT_MKD.gdb",
    "abandoned": "/path/to/abandoned_2024.gpkg",
    "gdr": "/path/to/gdr2024.gpkg",
    "imperv": "/path/to/imperv2024.gpkg"
}
lookup_path = "/path/to/lookup_table.xlsx"
output_dir = "./output"
merged_output_path = "./output/merged_landuse.gpkg"
final_raster_path = "./output/final_landuse_raster.tif"
```

### Lookup Table
Prepare an Excel file with columns:
- `LU`: Land Use identifier
- `raster_id`: Numeric ID for rasterization (1-50)

## Usage

```bash
python landuse_raster_processing.py
```

## Processing Steps

1. Load boundary and CRS information
2. Process and filter individual land use datasets
3. Validate and clean geometries
4. Merge layers with priority-based resolution
5. Rasterize layers (default 5m resolution)
6. Create a combined priority raster

## Output

- Filtered GeoPackage files for each land use dataset
- Individual raster files for each dataset
- Combined priority raster (`combined_raster.tif`)
- Detailed log file (`process_landuse_r.log`)

## Logging

Logging is configured to:
- Write to console
- Save detailed logs to `output/process_landuse_r.log`
- Track processing steps, warnings, and errors

## Customization

- Modify `raster_resolution` to change output resolution
- Adjust `priority_layers` to change layer merging priority
- Edit filtering criteria in individual processing steps

## Error Handling

The script includes comprehensive error handling:
- CRS validation and reprojection
- Geometry cleaning
- Invalid data filtering
- Detailed logging of processing issues

## Performance Notes

- Uses garbage collection for memory management
- Supports large geospatial datasets
- Configurable processing for different land use types

## Troubleshooting

- Ensure all input paths are correct
- Check input data CRS and geometry validity
- Review log file for detailed error information

## Contributors

Mohammad Reza Eini - Warsaw University of Life Sciences 
