import os
import geopandas as gpd
import pandas as pd
import numpy as np
import rasterio
from rasterio.features import rasterize

# Settings
input_raster = r"D:\Users\MRE\Scripts\Landuse_update\LUraster_bck.tif"
output_dir = r"D:\Users\MRE\Scripts\py_out"
lookup_path = r"D:\Users\MRE\Scripts\Landuse_update\lookup.xlsx"
merged_output_path = r"D:\Users\MRE\Scripts\py_out\Merged_Landuse.gpkg"
final_raster_path = r"D:\Users\MRE\Scripts\py_out\Merged_Landuse.tif"

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
    print("Rasterize process started...")
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
        "nodata": 0  # Set nodata value to 0
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
    
    print(f"Raster saved to: {output_tif_path}")
    print(f"Unique values in the raster: {np.unique(raster_array)}")

# Main execution
if __name__ == "__main__":
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the conversion
    convert_to_raster(
        merged_gpkg_path=merged_output_path, 
        output_tif_path=final_raster_path, 
        reference_raster_path=input_raster, 
        resolution=5
    )