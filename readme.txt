##################################################################################
1. Overview
The provided scripts automate the processing of spatial data related to land use. 
The pipeline includes filtering, merging, and rasterizing GeoPackage layers, 
ultimately producing a high-resolution raster file. 
The scripts use Python and require libraries such as GeoPandas, Rasterio, 
and Pandas.
##################################################################################
2. Files Overview
A. Main Script: main.py
Purpose: Orchestrates the processing steps:
Loading data.
Filtering and processing individual GeoPackage layers.
Merging processed layers.
Rasterizing the merged data to a GeoTIFF file.
B. Standalone Script: Standalone_Rasterization_Script.py
Purpose: Provides a focused script for converting a merged GeoPackage to a 
raster file. Ideal for standalone rasterization tasks.
C. Settings File: settings.py
Purpose: Centralized configuration file specifying paths to inputs, outputs, 
and essential parameters.
##################################################################################
3. Dependencies
Required Python Libraries:
GeoPandas
Rasterio
Pandas
NumPy
os
##################################################################################
##################################################################################
4. Workflow:

Step 1: Setup Configuration
Update settings.py with correct paths:
Input Layers:
Example: "crops": "path_to_Crops2024.gpkg"
Output Paths:
Example: output_dir = "path_to_output_directory"
Reference Raster:
Example: input_raster = "path_to_reference_raster.tif"
Lookup Table:
Excel file mapping land-use (LU) codes to raster_id.
                             
Step 2: Run main.py
Key Steps:
Load CRS: Reads the coordinate reference system from the input raster.
Filter and Process Layers:
Each layer is filtered based on predefined criteria.
Relevant columns are retained, and new attributes like LU are calculated.
Merge Layers:
Processed layers are merged into a single GeoPackage.
Rasterize:
Converts the merged GeoPackage into a GeoTIFF file at 5-meter resolution.
Outputs:
Processed GeoPackages (*.gpkg) for each layer.
Merged GeoPackage (Merged_Landuse.gpkg).
Final raster (Merged_Landuse.tif).
                             
Optional Step 3: Use Standalone_Rasterization_Script.py
If the merged GeoPackage already exists, use this script to create a raster.
##################################################################################
##################################################################################
5. Important Functions
A. convert_to_raster
Purpose: Converts vector data into a raster format.
Inputs:
merged_gpkg_path: Path to the merged GeoPackage.
output_tif_path: Output raster path.
reference_raster_path: Reference raster for CRS and extent.
resolution: Raster resolution (default: 5 meters).
B. Processing Steps in main.py
Each layer undergoes specific filters and transformations:
Example: The "crops" layer excludes rows with KODAS values "NEP" or "TPN".
##################################################################################
6. Error Handling
Missing Columns:
Scripts will raise errors if required columns are absent.
Example: "KeyError: 'Required columns zkg or VMR are missing'"
Lookup Failures:
If LU codes do not match the lookup table, rows may have NaN in raster_id.
##################################################################################
8. File Details
Input Files:
GeoPackage or GeoDatabase layers (e.g., crops, forest).
Reference raster for CRS and extent.
Lookup table mapping LU codes to raster_id.
Output Files:
Processed GeoPackages for each layer.
Merged GeoPackage (Merged_Landuse.gpkg).
Raster file (Merged_Landuse.tif).
##################################################################################
9. Notes
Ensure all paths in settings.py are valid before running scripts.
Output directories are automatically created if they do not exist.
Keep input GeoPackages consistent with the lookup table to avoid mismatches.
##################################################################################

