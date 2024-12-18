![Project Logo](https://webgate.ec.europa.eu/life/publicWebsite/assets/life/images/logoLife.png)

## Table of Contents

- [Overview](#overview)
- [Project Description](#project-description)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Processing Steps](#processing-steps)
- [Code Structure](#code-structure)
- [Outputs](#outputs)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

Welcome to the **LIFE Land Use Data Processing Pipeline**! This repository is an integral part of the **Integrated Water Management in Lithuania** project. It provides scripts to automate the processing of spatial data, from filtering and merging GeoPackage layers to creating high-resolution raster files. The scripts are written in Python and leverage powerful geospatial libraries to ensure efficient and accurate data handling.

## Project Description

The **Integrated Water Management in Lithuania** project aims to implement the National Water Sector Plan, ensuring the elimination or mitigation of significant impacts of prevailing pressures and contributing to achieving good status of surface and marine waters. This initiative aligns with the Water Framework Directive (WFD) and Marine Strategy Framework Directive (MSFD). Key objectives of the project include:

- **Improving Assessment Methods:** Enhancing techniques for evaluating surface water bodies.
- **Developing Tools & Methodologies:** Creating advanced tools for pressure and impact analysis on water bodies.
- **Setting Environmental Objectives:** Utilizing an ecosystem services approach to establish clear environmental goals.
- **Testing Measures:** Demonstrating effective measures to address pressures that deteriorate water quality.
- **Innovative Technologies:** Implementing remote sensing technologies for pollution identification and monitoring.

### Learn More

- [Project Page](https://webgate.ec.europa.eu/life/publicWebsite/project/LIFE22-IPE-LT-LIFE-SIP-Vanduo-101104645/integrated-water-management-in-lithuania)

## Code Developer

- **Mohammad Reza Eini - SGGW**

## Project Details

- **Reference:** LIFE22-IPE-LT-LIFE-SIP-Vanduo/101104645
- **Acronym:** LIFE22-IPE-LT-LIFE SIP Vanduo

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
python main.py
```

## Processing Steps

1. Load boundary and CRS information
2. Process and filter individual land use datasets
3. Validate and clean geometries
4. Merge layers with priority-based resolution
5. Rasterize layers (default 5m resolution)
6. Create a combined priority raster

## Code Structure

The script is organized into several key sections:
- Utility functions for file and geometry handling
- Individual dataset processing functions
- Rasterization and priority-based merging logic
- Comprehensive logging and error handling

## Outputs

- Filtered GeoPackage files for each land use dataset
- Individual raster files for each dataset
- Combined priority raster (`combined_raster.tif`)
- Detailed log file (`process_landuse_r.log`)

## Logging

Logging is configured to:
- Write to console
- Save detailed logs to `output/process_landuse_r.log`
- Track processing steps, warnings, and errors

## Troubleshooting

- Ensure all input paths are correct
- Check input data CRS and geometry validity
- Review log file for detailed error information
- Verify Python and library versions compatibility

## Contributing

Contributions are welcome! Please:
- Fork the repository
- Create a feature branch
- Submit a pull request
- Ensure code follows project's coding standards


**Note:** This project is part of the LIFE Programme, a EU funding instrument supporting environmental and climate action projects.


```
life-landuse-processing/
│
├── main/
│   └── main.py
│
├── settings.py
│
├── data/
│   ├── input/
│   │   ├── crops2024.gpkg
│   │   ├── forest2022.gpkg
│   │   ├── VMT_MKD.gdb
│   │   ├── abandoned_2024.gpkg
│   │   ├── gdr2024.gpkg
│   │   └── imperv2024.gpkg
│   │
│   └── lookup_table.xlsx
│
├── output/
│   ├── rasters/
│   │   ├── Crops2024_filtered.tif
│   │   ├── forest2022_filtered.tif
│   │   └── ...
│   │
│   ├── combined_raster.tif
│   └── process_landuse_r.log
│
├── requirements.txt
│
├── README.md
│
└── .gitignore
```

## Directory Explanation

- `main/`: Contains the primary processing script
- `settings.py`: Configuration file for paths and parameters
- `data/input/`: Source geospatial and lookup data
- `output/`: Generated raster files and processing logs
- `requirements.txt`: Python package dependencies
- `README.md`: Project documentation
