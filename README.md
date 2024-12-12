# Land Use Data Processing Pipeline

This repository is part of the **Integrated Water Management in Lithuania** project. Learn more about the project here:

- [Project Page](https://webgate.ec.europa.eu/life/publicWebsite/project/LIFE22-IPE-LT-LIFE-SIP-Vanduo-101104645/integrated-water-management-in-lithuania)

### Project Description

The project implements the National Water Sector Plan, ensuring the elimination or mitigation of significant impacts of prevailing pressures and contributing to achieving good status of surface and marine waters. The initiative aligns with the Water Framework and Marine Strategy Framework Directives. Key highlights include:

- Improving methods for assessing surface water bodies.
- Developing tools and methodologies for pressure and impact analysis.
- Setting environmental objectives using an ecosystem services approach.
- Testing and demonstrating measures to address pressures deteriorating water quality.
- Leveraging innovative technologies like remote sensing for pollution identification.

### Code Developer

- **Mohammad Reza Eini - SGGW**

### Project Details

- **Reference**: LIFE22-IPE-LT-LIFE-SIP-Vanduo/101104645
- **Acronym**: LIFE22-IPE-LT-LIFE SIP Vanduo

---

Welcome to the **Land Use Data Processing Pipeline**! This repository provides scripts to automate the processing of spatial data, from filtering and merging GeoPackage layers to creating high-resolution raster files. The scripts are written in Python and leverage powerful geospatial libraries.

---

## Features

- **Automated Workflow**: Process, merge, and rasterize GeoPackage layers.
- **Configurable**: Centralized settings for input/output paths and parameters.
- **High-Resolution Output**: Generates raster files with a resolution of 5 meters.
- **Error Handling**: Clear and informative error messages to streamline debugging.

---

## Table of Contents

1. [Files Overview](#files-overview)
2. [Dependencies](#dependencies)
3. [Workflow](#workflow)
4. [Important Functions](#important-functions)
5. [Error Handling](#error-handling)
6. [Input and Output Details](#input-and-output-details)
7. [Notes](#notes)

---

## Files Overview

### 1. **Main Script: `main.py`**
   - **Purpose**: Orchestrates the entire processing pipeline.
   - **Key Functions**:
     - Load data.
     - Filter and process GeoPackage layers.
     - Merge processed layers.
     - Rasterize merged data to create a GeoTIFF file.

### 2. **Standalone Script: `Standalone_Rasterization_Script.py`**
   - **Purpose**: Focused script for converting merged GeoPackages to raster files.
   - **Ideal Use Case**: Standalone rasterization tasks.

### 3. **Settings File: `settings.py`**
   - **Purpose**: Configurable file for specifying paths to inputs, outputs, and essential parameters.

---

## Dependencies

Ensure the following Python libraries are installed:

```bash
pip install geopandas rasterio pandas numpy
```

- `GeoPandas`: For vector data processing.
- `Rasterio`: For raster data handling.
- `Pandas`: For table manipulation and lookups.
- `NumPy`: For numerical computations.
- `os`: For file and directory operations.

---

## Workflow

### Step 1: Setup Configuration

Update `settings.py` with correct paths:

- **Input Layers**:
  ```python
  input_layers = {
      "crops": "path_to_Crops2024.gpkg",
      "forest": "path_to_Forest2024.gpkg",
  }
  ```
- **Output Paths**:
  ```python
  output_dir = "path_to_output_directory"
  ```
- **Reference Raster**:
  ```python
  input_raster = "path_to_reference_raster.tif"
  ```
- **Lookup Table**:
  An Excel file mapping land-use (LU) codes to `raster_id`.

### Step 2: Run `main.py`

1. **Key Steps**:
   - Load CRS: Reads the coordinate reference system from the input raster.
   - Filter and Process Layers: Filters layers based on criteria and computes new attributes like `LU`.
   - Merge Layers: Combines processed layers into a single GeoPackage.
   - Rasterize: Converts the merged GeoPackage into a GeoTIFF file at 5-meter resolution.

2. **Outputs**:
   - Processed GeoPackages for each layer.
   - Merged GeoPackage (`Merged_Landuse.gpkg`).
   - Final raster (`Merged_Landuse.tif`).

### Optional Step 3: Use `Standalone_Rasterization_Script.py`

If the merged GeoPackage already exists, use this script for raster creation.

---

## Important Functions

### 1. `convert_to_raster`
   - **Purpose**: Converts vector data into raster format.
   - **Inputs**:
     - `merged_gpkg_path`: Path to the merged GeoPackage.
     - `output_tif_path`: Path for the output raster.
     - `reference_raster_path`: Reference raster for CRS and extent.
     - `resolution`: Raster resolution (default: 5 meters).

### 2. Processing Steps in `main.py`
   - **Example**:
     - The `crops` layer excludes rows with `KODAS` values of "NEP" or "TPN".

---

## Error Handling

- **Missing Columns**:
  - Scripts will raise errors if required columns are absent.
  - Example: `KeyError: 'Required columns zkg or VMR are missing'`

- **Lookup Failures**:
  - If LU codes do not match the lookup table, rows may have `NaN` in `raster_id`.

---

## Input and Output Details

- **Input Files**:
  - GeoPackage or GeoDatabase layers (e.g., crops, forest).
  - Reference raster for CRS and extent.
  - Lookup table mapping LU codes to `raster_id`.

- **Output Files**:
  - Processed GeoPackages for each layer.
  - Merged GeoPackage (`Merged_Landuse.gpkg`).
  - Raster file (`Merged_Landuse.tif`).

---

## Notes

- Ensure all paths in `settings.py` are valid before running scripts.
- Output directories are automatically created if they do not exist.
- Keep input GeoPackages consistent with the lookup table to avoid mismatches.
