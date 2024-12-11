# Path to the reference raster file
# Used for setting CRS and aligning outputs
input_raster = r"D:\Users\MRE\Scripts\Landuse_update\LUraster_bck.tif"

# Directory for the output files
# All processed GeoPackages and the final raster will be saved here
output_dir = r"D:\Users\MRE\Scripts\py_out"

# Paths to input GeoPackage layers
# Each input corresponds to a GeoPackage or Geodatabase file containing spatial data
input_layers = {
    "crops": r"D:\Users\MRE\Scripts\Landuse_update\2024\inputs\Crops2024.gpkg",  # Crops layer
    "forest": r"D:\Users\MRE\Scripts\Landuse_update\2024\inputs\forest2022.gpkg",  # Forest layer
    "vmt": r"D:\Users\MRE\Scripts\Landuse_update\2024\inputs\raw\forest\VMT_MKD.gdb",  # VMT data layer
    "abandoned": r"D:\Users\MRE\Scripts\Landuse_update\2024\inputs\abandoned_2024.gpkg",  # Abandoned land
    "gdr": r"D:\Users\MRE\Scripts\Landuse_update\2024\inputs\gdr2024.gpkg",  # General drainage layer
    "imperv": r"D:\Users\MRE\Scripts\Landuse_update\2024\inputs\imperv2024.gpkg",  # Impervious surfaces
}

# Path to the lookup table
# Used to map `LU` codes to `raster_id` values
lookup_path = r"D:\Users\MRE\Scripts\Landuse_update\lookup.xlsx"

# Path to save the merged output GeoPackage
# All individual layers will be combined into this file
merged_output_path = r"D:\Users\MRE\Scripts\py_out\Merged_Landuse.gpkg"

# Path to save the final GeoTIFF raster file
# Converted from the merged GeoPackage with 5-meter resolution
final_raster_path = r"D:\Users\MRE\Scripts\py_out\Merged_Landuse.tif"
