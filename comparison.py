import os
import rasterio
import numpy as np
import pandas as pd

def process_raster(raster_path, output_dir, raster_label):
    """
    Process a raster to count unique non-zero values and their frequencies.

    Parameters:
    - raster_path: Path to the raster file
    - output_dir: Directory to save output files
    - raster_label: Label for the raster ('new' or 'old')

    Returns:
    - None
    """
    try:
        with rasterio.open(raster_path) as raster:
            print(f"\nProcessing {raster_label.capitalize()} Raster:")
            print(f"Path: {raster_path}")

            # Read the first band
            data = raster.read(1)
            print(f"Raster Shape: {data.shape}")

            # Exclude zero values
            mask = data != 0
            data_masked = data[mask]
            print(f"Non-zero pixels: {data_masked.size}")

            # Count unique values and frequencies
            unique, counts = np.unique(data_masked, return_counts=True)
            print(f"Unique non-zero values: {unique}")

            # Create DataFrame for counts
            counts_df = pd.DataFrame({
                'Value': unique,
                f'{raster_label.capitalize()}_Count': counts,
                f'{raster_label.capitalize()}_Percentage': (counts / data_masked.size) * 100
            })

            # Save counts to CSV
            counts_output_path = os.path.join(output_dir, f'{raster_label}_landuse_counts_arcmap.csv')
            counts_df.to_csv(counts_output_path, index=False)
            print(f"{raster_label.capitalize()} counts saved to {counts_output_path}")

    except rasterio.errors.RasterioIOError as e:
        print(f"Error opening {raster_label} raster: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {raster_label} raster: {e}")

def main():
    # Define paths
    new_raster_path = r"D:\Users\MRE\Scripts\py_out\Arc_map_output.tif"
    old_raster_path = r"D:\Users\MRE\Scripts\Landuse_update\LUraster_bck.tif"
    output_directory = r"D:\Users\MRE\Scripts\py_out"

    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # Process new raster
    process_raster(new_raster_path, output_directory, 'new')

    # Process old raster
    process_raster(old_raster_path, output_directory, 'old')

if __name__ == "__main__":
    main()
