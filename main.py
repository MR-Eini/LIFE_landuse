import os  # For directory management
import gc  # For memory cleanup
import geopandas as gpd  # For handling GeoPackage and spatial data
import pandas as pd  # For handling tabular data
import numpy as np
import rasterio  # For reading raster files and handling CRS
from rasterio.features import rasterize  # For rasterizing vector data
from settings import (  # Import paths and configurations from the settings file
    input_raster,  # Path to the reference raster file
    output_dir,  # Directory for saving processed files
    input_layers,  # Paths to input GeoPackage layers
    lookup_path,  # Path to the lookup table
    merged_output_path,  # Path to save the merged GeoPackage
    final_raster_path,  # Path to save the final GeoTIFF raster
)

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

################################################################################
# Step 1: Load CRS from Reference Raster
################################################################################

# Load CRS from the reference raster file
with rasterio.open(input_raster) as src:
    target_crs = src.crs.to_string()  # CRS as a string (e.g., "EPSG:3346")
    print(f"Target CRS: {target_crs}")

# Load the lookup table
lookup = pd.read_excel(lookup_path)
print(" Step 1: Lookup table loaded.")

# List to store paths of processed files
processed_files = []

################################################################################
# Step 2: Process Crops2024
################################################################################

# Define output path
crops_out = os.path.join(output_dir, "Crops2024_filtered.gpkg")

# Read the GeoPackage file for Crops2024
crops = gpd.read_file(input_layers["crops"])
print("Processing Crops2024...(Step 2 out of 9)")

# Filter and process data
crops = crops[["KODAS", "geometry"]]  # Keep only the "KODAS" column and geometry
crops = crops[~crops["KODAS"].isin(["NEP", "TPN"])]  # Exclude rows with "NEP" or "TPN"
crops["LU"] = "C_" + crops["KODAS"].astype(str)  # Add prefix to "KODAS"

# Merge with lookup table to add `raster_id`
crops = crops.merge(lookup, how="left", on="LU")

# Save processed file as GeoPackage
crops.to_file(crops_out, layer="Crops2024", driver="GPKG")
processed_files.append(crops_out)
print(f"Step 2: Processed Crops2024 saved to: {crops_out}")

# Clean up memory
del crops
gc.collect()

################################################################################
# Step 3: Process forest2022
################################################################################

# Define output path
forest_out = os.path.join(output_dir, "forest2022_filtered.gpkg")

# Read the GeoPackage file for forest2022
forest = gpd.read_file(input_layers["forest"])
print("Processing forest2022...(Step 3 out of 9)")

# Filter and process data
forest = forest[["augaviete", "geometry"]]  # Keep only the "augaviete" column and geometry
forest = forest[forest["augaviete"].isin(["Pa", "Pan", "Pb"])]  # Include rows with these values
forest["LU"] = "W_" + forest["augaviete"].astype(str)  # Add prefix to "augaviete"

# Merge with lookup table to add `raster_id`
forest = forest.merge(lookup, how="left", on="LU")

# Save processed file as GeoPackage
forest.to_file(forest_out, layer="forest2022", driver="GPKG")
processed_files.append(forest_out)
print(f"Step 3: Processed forest2022 saved to: {forest_out}")

# Clean up memory
del forest
gc.collect()

################################################################################
# Step 4: Process Misko_sklypai from VMT_MKD.gdb
################################################################################

# Define output path
vmt_out = os.path.join(output_dir, "VMT_MKD_filtered.gpkg")

# Read the layer "Misko_sklypai" from the file "VMT_MKD.gdb"
vmt = gpd.read_file(input_layers["vmt"], layer="Misko_sklypai")
print("Processing Misko_sklypai...(Step 4 out of 9)")

# Ensure the required columns are present
if "zkg" not in vmt.columns or "VMR" not in vmt.columns:
    raise KeyError("Required columns 'zkg' or 'VMR' are missing in the 'Misko_sklypai' layer.")

# Filter to keep only the relevant columns
vmt = vmt[["zkg", "VMR", "geometry"]]

# Generate a new column "LU" based on "zkg" and "VMR"
vmt["LU"] = "F_" + vmt["zkg"].astype(str) + "_" + vmt["VMR"].fillna("None").astype(str)

# Merge with lookup table to add `raster_id`
vmt = vmt.merge(lookup, how="left", on="LU")

# Save processed file as GeoPackage
vmt.to_file(vmt_out, layer="Misko_sklypai", driver="GPKG")
processed_files.append(vmt_out)
print(f"Step 4: Processed Misko_sklypai saved to: {vmt_out}")

# Clean up memory
del vmt
gc.collect()

################################################################################
# Step 5: Process abandoned_2024
################################################################################

# Define output path
aband_out = os.path.join(output_dir, "abandoned_2024_filtered.gpkg")

# Read the GeoPackage file for abandoned_2024
aband = gpd.read_file(input_layers["abandoned"])
print("Processing abandoned_2024...(Step 5 out of 9)")

# Process data
aband["LU"] = "A_"  # Add prefix for all rows

# Merge with lookup table to add `raster_id`
aband = aband.merge(lookup, how="left", on="LU")

# Save processed file as GeoPackage
aband.to_file(aband_out, layer="abandoned_2024", driver="GPKG")
processed_files.append(aband_out)
print(f"Step 5: Processed abandoned_2024 saved to: {aband_out}")

# Clean up memory
del aband
gc.collect()

################################################################################
# Step 6: Process gdr2024
################################################################################

# Define output path
gdr_out = os.path.join(output_dir, "gdr2024_filtered.gpkg")

# Read the GeoPackage file for gdr2024
gdr = gpd.read_file(input_layers["gdr"])
print("Processing gdr2024...(Step 6 out of 9)")

# Filter and process data
gdr = gdr[["GKODAS", "geometry"]]  # Keep only the "GKODAS" column and geometry
gdr = gdr[~gdr["GKODAS"].isin(["pu0", "pu3"])]  # Exclude rows with these values
gdr["LU"] = "G_" + gdr["GKODAS"].astype(str)  # Add prefix to "GKODAS"

# Merge with lookup table to add `raster_id`
gdr = gdr.merge(lookup, how="left", on="LU")

# Save processed file as GeoPackage
gdr.to_file(gdr_out, layer="gdr2024", driver="GPKG")
processed_files.append(gdr_out)
print(f"Step 6: Processed gdr2024 saved to: {gdr_out}")

# Clean up memory
del gdr
gc.collect()

################################################################################
# Step 7: Process imperv2024
################################################################################

# Define output path
imperv_out = os.path.join(output_dir, "imperv2024_filtered.gpkg")

# Read the GeoPackage file for imperv2024
imperv = gpd.read_file(input_layers["imperv"])
print("Processing imperv2024...(Step 7 out of 9)")

# Process data
imperv["LU"] = "U_" + imperv["Cat"].astype(str)  # Add prefix to "Cat" values

# Merge with lookup table to add `raster_id`
imperv = imperv.merge(lookup, how="left", on="LU")

# Save processed file as GeoPackage
imperv.to_file(imperv_out, layer="imperv2024", driver="GPKG")
processed_files.append(imperv_out)
print(f"Step 7: Processed imperv2024 saved to: {imperv_out}")

# Clean up memory
del imperv
gc.collect()

################################################################################
# Step 8: Merge All Processed Files into a Single GeoPackage
################################################################################

# Combine all processed GeoPackages into a single merged GeoPackage
print("Merging all processed files...(Step 8 out of 9)")
merged_layers = [gpd.read_file(fp) for fp in processed_files]
merged_data = gpd.GeoDataFrame(pd.concat(merged_layers, ignore_index=True), geometry='geometry')

# Save the merged data as a GeoPackage
merged_data.to_file(merged_output_path, layer="merged_layer", driver="GPKG")
print(f"Step 8: Merged GeoPackage saved to: {merged_output_path}")
print("Merging completed successfully.")

################################################################################
# Step 9: Rasterize, 5 meter resolution GeoTIFF file 
################################################################################
def convert_to_raster(merged_gpkg_path, output_tif_path, reference_raster_path, resolution=5):
    """
    Convert a GeoPackage file to a GeoTIFF using integer `raster_id` as cell values.

    Args:
        merged_gpkg_path: Path to the merged GeoPackage file.
        output_tif_path: Path to save the GeoTIFF file.
        reference_raster_path: Path to the reference raster for CRS and extent.
        resolution: Desired resolution of the raster in meters.
    """
    # Load the merged GeoPackage
    print("Rasterize process...(Step 9 out of 9)")
    merged_data = gpd.read_file(merged_gpkg_path, layer="merged_layer")
    if "raster_id" not in merged_data.columns:
        raise ValueError("The 'raster_id' column is missing in the merged GeoPackage.")
    
    # Filter out non-integer raster_id values
    merged_data = merged_data[pd.to_numeric(merged_data['raster_id'], errors='coerce').notnull()]
    merged_data['raster_id'] = merged_data['raster_id'].astype(int)
    
    print(f"Loaded merged data with {len(merged_data)} features after filtering non-integer raster_id.")

    # Open the reference raster to get CRS and bounds
    with rasterio.open(reference_raster_path) as ref_raster:
        ref_crs = ref_raster.crs
        ref_bounds = ref_raster.bounds

    # Ensure the merged data has the same CRS as the reference raster
    merged_data = merged_data.to_crs(ref_crs)

    # Calculate raster dimensions based on bounds and resolution
    width = int((ref_bounds.right - ref_bounds.left) / resolution)
    height = int((ref_bounds.top - ref_bounds.bottom) / resolution)

    # Define raster metadata
    transform = rasterio.transform.from_bounds(
        ref_bounds.left, ref_bounds.bottom, ref_bounds.right, ref_bounds.top, width, height
    )
    raster_meta = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,  # Single band raster
        "dtype": "int32",
        "crs": ref_crs,
        "transform": transform,
    }

    # Rasterize the merged GeoPackage data
    print("Rasterizing merged data...")
    shapes = ((geom, value) for geom, value in zip(merged_data.geometry, merged_data["raster_id"]))
    raster_array = rasterize(
        shapes,
        out_shape=(height, width),
        transform=transform,
        fill=0,  # Default value for cells without data
        dtype="int32"
    )

    # Save the raster to a GeoTIFF file
    with rasterio.open(output_tif_path, "w", **raster_meta) as dst:
        dst.write(raster_array, 1)  # Write the data to the first band
    print(f"Step 9: Raster saved to: {output_tif_path}")

# Define paths
merged_gpkg_path = merged_output_path  # Path to the merged GeoPackage file
output_tif_path = final_raster_path  # Output GeoTIFF file
reference_raster_path = input_raster  # Reference raster for CRS and extent

# Convert the merged GeoPackage to GeoTIFF
convert_to_raster(merged_gpkg_path, output_tif_path, reference_raster_path, resolution=5)

################################################################################
# All steps completed successfully.
################################################################################
print("All processing completed successfully.")