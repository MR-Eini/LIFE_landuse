import os
import rasterio
import numpy as np
import geopandas as gpd
import pandas as pd

def compare_landuse_maps(new_raster_path, old_raster_path, output_dir):
    """
    Compare two land use raster maps and perform various analyses.
    
    Parameters:
    - new_raster_path: Path to the newer land use raster
    - old_raster_path: Path to the older land use raster
    - output_dir: Directory to save output files
    """
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Open raster files
    with rasterio.open(new_raster_path) as new_raster, \
         rasterio.open(old_raster_path) as old_raster:
        
        # Check Coordinate Reference System (CRS)
        print("New Raster CRS:", new_raster.crs)
        print("Old Raster CRS:", old_raster.crs)
        
        # Check if CRS are the same
        if new_raster.crs != old_raster.crs:
            print("WARNING: CRS are different! Reprojection might be necessary.")
        
        # Read raster data
        new_data = new_raster.read(1)  # read first band
        old_data = old_raster.read(1)
        
        # Check raster alignment and size
        if new_data.shape != old_data.shape:
            print("WARNING: Raster dimensions are different!")
            print("New raster shape:", new_data.shape)
            print("Old raster shape:", old_data.shape)
        
        # Count unique values and their frequencies
        new_unique, new_counts = np.unique(new_data, return_counts=True)
        old_unique, old_counts = np.unique(old_data, return_counts=True)
        
        # Create DataFrames for unique values and counts
        new_counts_df = pd.DataFrame({
            'Value': new_unique,
            'New_Count': new_counts,
            'New_Percentage': new_counts / new_data.size * 100
        })
        
        old_counts_df = pd.DataFrame({
            'Value': old_unique,
            'Old_Count': old_counts,
            'Old_Percentage': old_counts / old_data.size * 100
        })
        
        # Merge counts
        merged_counts = pd.merge(
            new_counts_df, 
            old_counts_df, 
            on='Value', 
            how='outer'
        ).fillna(0)
        
        # Calculate changes
        merged_counts['Count_Difference'] = merged_counts['New_Count'] - merged_counts['Old_Count']
        merged_counts['Percentage_Difference'] = merged_counts['New_Percentage'] - merged_counts['Old_Percentage']
        
        # Save counts to CSV
        counts_output_path = os.path.join(output_dir, 'landuse_counts_comparison.csv')
        merged_counts.to_csv(counts_output_path, index=False)
        print(f"Counts comparison saved to {counts_output_path}")
        
        # Create difference raster
        difference_raster = new_data - old_data
        
        # Save difference raster
        difference_output_path = os.path.join(output_dir, 'landuse_difference.tif')
        
        # Copy metadata from the new raster
        difference_profile = new_raster.profile.copy()
        difference_profile.update(
            dtype=rasterio.int16,
            count=1,
            compress='lzw'
        )
        
        with rasterio.open(difference_output_path, 'w', **difference_profile) as dst:
            dst.write(difference_raster.astype(rasterio.int16), 1)
        
        print(f"Difference raster saved to {difference_output_path}")
        
        return merged_counts

# Paths
new_raster_path = r'D:\Users\MRE\Scripts\py_out\Merged_Landuse.tif'
old_raster_path = r'D:\Users\MRE\Scripts\Landuse_update\LUraster_bck.tif'
output_directory = r'D:\Users\MRE\Scripts\py_out'

# Run comparison
comparison_results = compare_landuse_maps(new_raster_path, old_raster_path, output_directory)

# Optional: Print summary
print("\nComparison Summary:")
print(comparison_results)