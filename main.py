import os  # For directory management
import gc  # For memory cleanup
import logging  # For logging
import geopandas as gpd  # For handling GeoPackage and spatial data
import pandas as pd  # For handling tabular data
import numpy as np  # For numerical calculation
import rasterio  # For reading raster files and handling CRS
from rasterio.features import rasterize  # For rasterizing vector data
from rasterio.mask import mask  # For masking the raster
from rasterio.transform import from_origin
import fiona  # For listing layers in GeoPackage
import math
from settings import (  # Import paths and configurations from the settings file
    boundary_gpkg,  # Path to the boundary GeoPackage file
    output_dir,  # Directory for saving processed files
    input_layers,  # Paths to input GeoPackage layers
    lookup_path,  # Path to the lookup table
    merged_output_path,  # Path to save the merged GeoPackage
    final_raster_path,  # Path to save the final GeoTIFF raster
)

###################################################
# Utility Functions
###################################################

def path_exists(filepath, logger):
    """
    Check if a given file or directory exists on disk.

    Args:
        filepath (str): Path to the file or directory.
        logger (logging.Logger): Logger object for logging messages.

    Returns:
        bool: True if file or directory exists, False otherwise.
    """
    if os.path.isfile(filepath):
        logger.debug(f"File exists: {filepath}")
        return True
    elif os.path.isdir(filepath):
        logger.debug(f"Directory exists: {filepath}")
        return True
    else:
        logger.debug(f"Path does not exist: {filepath}")
        return False

def clean_geometries(gdf):
    """
    Comprehensive geometry cleaning function
    """
    # Remove duplicate geometries
    gdf = gdf.drop_duplicates(subset=['geometry'])
    
    # Validate and make geometries valid
    gdf['geometry'] = gdf.geometry.buffer(0)
    
    # Simplify geometries to reduce complexity
    gdf['geometry'] = gdf.geometry.simplify(tolerance=1.0, preserve_topology=True)
    
    # Remove empty geometries
    gdf = gdf[~gdf.geometry.is_empty]
    
    return gdf

def validate_crs(layers, logger):
    """
    Ensure all layers have the same Coordinate Reference System
    """
    if len(set(layer.crs for layer in layers)) > 1:
        logger.info("CRS mismatch detected. Reprojecting to match first layer's CRS.")
        base_crs = layers[0].crs
        layers = [layer.to_crs(base_crs) if layer.crs != base_crs else layer for layer in layers]
    return layers

###################################################
# Priority Union Function
###################################################

def priority_union_layers(union_layers_with_names, layer_priority, logger):
    """
    Perform a union of layers with priority-based overlap resolution.
    
    Args:
        union_layers_with_names (list of tuples): List of tuples (layer_name, GeoDataFrame) to union
        layer_priority (list): List of layer names in order of priority (first = highest)
        logger (logging.Logger): Logger for tracking process
    
    Returns:
        GeoDataFrame: Unioned GeoDataFrame with highest priority layers preserved in overlaps
    """
    # Sort the layers based on priority
    sorted_layers = sorted(union_layers_with_names, key=lambda x: layer_priority.index(x[0]))
    
    # Assign priority index (lower index = higher priority)
    for i, (layer_name, layer) in enumerate(sorted_layers):
        layer['_layer_priority'] = i
    
    # Start with the highest priority layer
    result = sorted_layers[0][1].copy()
    
    # Process subsequent layers
    for layer_name, next_layer in sorted_layers[1:]:
        # Find overlapping geometries
        spatial_index = result.sindex
        
        # Prepare a list to store non-overlapping and resolved geometries
        updated_geometries = []
        
        # Iterate through next layer's geometries
        for idx, row in next_layer.iterrows():
            # Find potential intersections
            possible_matches_index = list(spatial_index.intersection(row.geometry.bounds))
            
            # Check for actual intersections
            intersecting = result.iloc[possible_matches_index][
                result.iloc[possible_matches_index].intersects(row.geometry)
            ]
            
            if not intersecting.empty:
                # Compare priorities in overlapping areas
                max_priority_intersecting = intersecting['_layer_priority'].max()
                
                # If current layer has higher priority, replace intersecting geometries
                if next_layer['_layer_priority'].iloc[0] < max_priority_intersecting:
                    # Remove lower priority intersecting geometries
                    result = result[
                        (result['_layer_priority'] > next_layer['_layer_priority'].iloc[0]) | 
                        (~result.intersects(row.geometry))
                    ]
                    
                    # Add the new geometry
                    updated_geometries.append(row)
                elif next_layer['_layer_priority'].iloc[0] > max_priority_intersecting:
                    # Current layer has lower priority, so skip
                    continue
            else:
                # No intersection, add the geometry
                updated_geometries.append(row)
        
        # Append non-overlapping or priority-resolved geometries
        if updated_geometries:
            new_geometries = gpd.GeoDataFrame(updated_geometries, columns=next_layer.columns)
            new_geometries['_layer_priority'] = next_layer['_layer_priority']
            result = pd.concat([result, new_geometries], ignore_index=True)
        
        logger.info(f"After processing layer '{layer_name}': {len(result)} records")
    
    # Clean final result and remove priority column
    result = clean_geometries(result)
    if '_layer_priority' in result.columns:
        result = result.drop(columns=['_layer_priority'])
    
    return result

###################################################
# Configure the Output Directory and Logging
###################################################

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir, exist_ok=True)

# Configure the logging
logging.basicConfig(
    level=logging.INFO,  # Set to INFO to exclude DEBUG messages
    format='%(asctime)s - %(levelname)s - %(message)s',  # Log message format
    handlers=[
        logging.FileHandler(os.path.join(output_dir, 'process_landuse_r.log')),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)

# Create a logger object
logger = logging.getLogger(__name__)

# Log the creation or existence of the output directory
if path_exists(output_dir, logger):
    logger.info(f"Output directory already exists: {output_dir}")
else:
    logger.info(f"Created output directory: {output_dir}")

###################################################
# Utility Function for Cropping
###################################################

def crop_merged_to_boundary(merged_gpkg_path, boundary_gpkg_path, output_cropped_gpkg_path, logger):
    """
    Crop the merged GeoPackage based on the boundary GeoPackage and save as a new GeoPackage.
    Args:
        merged_gpkg_path (str): Path to the merged GeoPackage file.
        boundary_gpkg_path (str): Path to the boundary GeoPackage file.
        output_cropped_gpkg_path (str): Path to save the cropped GeoPackage.
        logger (logging.Logger): Logger object for logging messages.
    """
    try:
        logger.info("Step 8a: Starting cropping of merged GeoPackage based on boundary.")
        
        # Load the merged GeoPackage
        merged_data = gpd.read_file(merged_gpkg_path, layer="merged_layer")
        logger.info(f"Step 8a: Loaded merged GeoPackage with {len(merged_data)} records.")
        
        # Validate merged data geometries
        merged_data['is_valid'] = merged_data.geometry.is_valid
        invalid_merged = merged_data[~merged_data['is_valid']]
        if not invalid_merged.empty:
            logger.warning(f"Step 8a: {len(invalid_merged)} invalid geometries found in merged data. Attempting repair.")
            merged_data.loc[~merged_data['is_valid'], 'geometry'] = merged_data.loc[~merged_data['is_valid'], 'geometry'].buffer(0)
        
        # Load the boundary GeoPackage
        boundary = gpd.read_file(boundary_gpkg_path)
        logger.info(f"Step 8a: Loaded boundary GeoPackage with {len(boundary)} records.")
        
        # Validate boundary geometries
        boundary['is_valid'] = boundary.geometry.is_valid
        invalid_boundary = boundary[~boundary['is_valid']]
        if not invalid_boundary.empty:
            logger.warning(f"Step 8a: {len(invalid_boundary)} invalid geometries found in boundary. Attempting repair.")
            boundary.loc[~boundary['is_valid'], 'geometry'] = boundary.loc[~boundary['is_valid'], 'geometry'].buffer(0)
        
        # Ensure both datasets have the same CRS
        if merged_data.crs != boundary.crs:
            logger.info("Step 8a: CRS mismatch detected. Reprojecting boundary to match merged data CRS.")
            boundary = boundary.to_crs(merged_data.crs)
            logger.info("Step 8a: Reprojection completed.")
        
        # Perform spatial clipping with a more robust method
        try:
            logger.info("Step 8a: Clipping merged data with boundary using gpd.clip().")
            merged_clipped = gpd.clip(merged_data, boundary)
            logger.info(f"Step 8a: Clipping completed. {len(merged_clipped)} records after clipping.")
        except Exception as clip_error:
            logger.warning(f"Step 8a: gpd.clip() failed. Attempting alternative intersection method. Error: {clip_error}")
            try:
                # Fallback to overlay method
                merged_clipped = gpd.overlay(merged_data, boundary, how='intersection')
                logger.info(f"Step 8a: Intersection completed. {len(merged_clipped)} records after intersection.")
            except Exception as overlay_error:
                logger.error(f"Step 8a: Both clipping methods failed. Error: {overlay_error}")
                raise
        
        # Ensure no empty geometries remain
        merged_clipped = merged_clipped[~merged_clipped.geometry.is_empty]
        logger.info(f"Step 8a: Removed {len(merged_clipped[merged_clipped.geometry.is_empty])} empty geometries.")
        
        # Save the cropped GeoPackage
        merged_clipped.to_file(output_cropped_gpkg_path, layer="merged_clipped", driver="GPKG")
        logger.info(f"Step 8a: Cropped GeoPackage saved to: {output_cropped_gpkg_path} with {len(merged_clipped)} records.")
        
        # Clean up memory
        del merged_data, boundary, merged_clipped
        gc.collect()
        
    except Exception as e:
        logger.error(f"Step 8a: Comprehensive cropping failure: {e}")
        # Optionally, add more detailed logging or error diagnosis
        raise

################################################################################
# Step 1: Load CRS and Bounds from Boundary GeoPackage
################################################################################

try:
    # Load the boundary GeoPackage
    boundary = gpd.read_file(boundary_gpkg)
    logger.info("Step 1: Boundary GeoPackage loaded.")

    # Extract CRS
    target_crs = boundary.crs.to_string()
    logger.info(f"Step 1: Target CRS: {target_crs}")

    # Extract total bounds (minx, miny, maxx, maxy)
    total_bounds = boundary.total_bounds
    logger.info(f"Step 1: Boundary bounds: {total_bounds}")

except Exception as e:
    logger.error(f"Step 1: Failed to load boundary GeoPackage: {e}")
    raise

################################################################################
# Load the Lookup Table
################################################################################

try:
    # Load the lookup table
    lookup = pd.read_excel(lookup_path)
    logger.info("Step 1: Lookup table loaded.")

    # Ensure 'raster_id' in lookup is integer and within 1-50
    if 'raster_id' not in lookup.columns:
        logger.critical("Step 1: The lookup table must contain a 'raster_id' column.")
        raise KeyError("The lookup table must contain a 'raster_id' column.")

    # Convert 'raster_id' to integer
    lookup['raster_id'] = pd.to_numeric(lookup['raster_id'], errors='coerce').astype('Int64')

    # Validate 'raster_id' range
    if not lookup['raster_id'].between(1, 50).all():
        invalid_ids = lookup[~lookup['raster_id'].between(1, 50)]
        logger.critical(f"Step 1: Invalid 'raster_id' values found: {invalid_ids['raster_id'].unique()}")
        raise ValueError(f"Invalid 'raster_id' values found: {invalid_ids['raster_id'].unique()}")

    logger.info("Step 1: 'raster_id' in lookup table validated as integers between 1 and 50.")

except Exception as e:
    logger.error(f"Step 1: Failed to process lookup table: {e}")
    raise

# List to store paths of processed files
processed_files = []

################################################################################
# Step 2: Process Crops2024
################################################################################

# Define output path
crops_out = os.path.join(output_dir, "Crops2024_filtered.gpkg")

# Check if output file already exists
if path_exists(crops_out, logger):
    logger.info(f"Step 2: {crops_out} already exists. Skipping processing Crops2024.")
    processed_files.append(crops_out)  # Append existing file to processed_files
else:
    try:
        # Read the GeoPackage file for Crops2024
        crops = gpd.read_file(input_layers["crops"])
        logger.info("Processing Crops2024...(Step 2 out of 9)")

        # Filter and process data
        crops = crops[["KODAS", "geometry"]]  # Keep only the "KODAS" column and geometry
        crops = crops[~crops["KODAS"].isin(["NEP", "TPN"])]  # Exclude rows with "NEP" or "TPN"
        crops["LU"] = "C_" + crops["KODAS"].astype(str)  # Add prefix to "KODAS"

        # Merge with lookup table to add `raster_id`
        crops = crops.merge(lookup, how="left", on="LU")

        # Ensure 'raster_id' is integer and within 1-50
        crops['raster_id'] = pd.to_numeric(crops['raster_id'], errors='coerce').astype('Int64')
        valid_crops = crops[crops['raster_id'].between(1, 50)]
        invalid_crops = crops[~crops['raster_id'].between(1, 50)]
        if not invalid_crops.empty:
            logger.warning(f"Step 2: {len(invalid_crops)} Crops2024 records have invalid 'raster_id' and will be excluded.")
        crops = valid_crops

        # Save processed file as GeoPackage
        crops.to_file(crops_out, layer="Crops2024", driver="GPKG")
        processed_files.append(crops_out)
        logger.info(f"Step 2: Processed Crops2024 saved to: {crops_out} with {len(crops)} records.")

    except Exception as e:
        logger.error(f"Step 2: Failed to process Crops2024: {e}")
        raise
    finally:
        # Clean up memory
        del crops
        gc.collect()

################################################################################
# Step 3: Process forest2022
################################################################################

# Define output path
forest_out = os.path.join(output_dir, "forest2022_filtered.gpkg")

# Check if output file already exists
if path_exists(forest_out, logger):
    logger.info(f"Step 3: {forest_out} already exists. Skipping processing forest2022.")
    processed_files.append(forest_out)  # Append existing file to processed_files
else:
    try:
        # Read the GeoPackage file for forest2022
        forest = gpd.read_file(input_layers["forest"])
        logger.info("Processing forest2022...(Step 3 out of 9)")

        # Filter and process data
        forest = forest[["augaviete", "geometry"]]  # Keep only the "augaviete" column and geometry
        forest = forest[forest["augaviete"].isin(["Pa", "Pan", "Pb"])]  # Include rows with these values
        forest["LU"] = "W_" + forest["augaviete"].astype(str)  # Add prefix to "augaviete"

        # Merge with lookup table to add `raster_id`
        forest = forest.merge(lookup, how="left", on="LU")

        # Ensure 'raster_id' is integer and within 1-50
        forest['raster_id'] = pd.to_numeric(forest['raster_id'], errors='coerce').astype('Int64')
        valid_forest = forest[forest['raster_id'].between(1, 50)]
        invalid_forest = forest[~forest['raster_id'].between(1, 50)]
        if not invalid_forest.empty:
            logger.warning(f"Step 3: {len(invalid_forest)} forest2022 records have invalid 'raster_id' and will be excluded.")
        forest = valid_forest

        # Save processed file as GeoPackage
        forest.to_file(forest_out, layer="forest2022", driver="GPKG")
        processed_files.append(forest_out)
        logger.info(f"Step 3: Processed forest2022 saved to: {forest_out} with {len(forest)} records.")

    except Exception as e:
        logger.error(f"Step 3: Failed to process forest2022: {e}")
        raise
    finally:
        # Clean up memory
        del forest
        gc.collect()

################################################################################
# Step 4: Process Misko_sklypai from VMT_MKD.gdb
################################################################################

# Define output path
vmt_out = os.path.join(output_dir, "VMT_MKD_filtered.gpkg")  # Original naming

# Alternatively, rename to include layer name for consistency
vmt_out = os.path.join(output_dir, "Misko_sklypai_filtered.gpkg")  # Updated naming

# Check if output file already exists
if path_exists(vmt_out, logger):
    logger.info(f"Step 4: {vmt_out} already exists. Skipping processing Misko_sklypai.")
    processed_files.append(vmt_out)  # Append existing file to processed_files
else:
    try:
        # Read the layer "Misko_sklypai" from the GeoPackage/Geodatabase
        vmt = gpd.read_file(input_layers["vmt"], layer="Misko_sklypai")
        logger.info("Processing Misko_sklypai...(Step 4 out of 9)")

        # Ensure the required columns are present
        required_columns = ["zkg", "VMR", "geometry"]
        missing_columns = [col for col in required_columns if col not in vmt.columns]
        if missing_columns:
            logger.critical(f"Step 4: Required columns {missing_columns} are missing in the 'Misko_sklypai' layer.")
            raise KeyError(f"Required columns {missing_columns} are missing in the 'Misko_sklypai' layer.")

        # Filter to keep only the relevant columns
        vmt = vmt[["zkg", "VMR", "geometry"]]

        # ### **Added Filtering Step: Exclude 'zkg' codes 0, 2, 4, 5**
        filtered_codes = [0, 2, 4, 5]
        vmt = vmt[~vmt['zkg'].isin(filtered_codes)]
        logger.info(f"Step 4: Filtered out 'zkg' codes {filtered_codes}. Remaining records: {len(vmt)}")

        # Generate a new column "LU" based on "zkg" and "VMR"
        vmt["LU"] = "F_" + vmt["zkg"].astype(str) + "_" + vmt["VMR"].fillna("None").astype(str)

        # Merge with lookup table to add `raster_id`
        vmt = vmt.merge(lookup, how="left", on="LU")

        # Ensure 'raster_id' is integer and within 1-50
        vmt['raster_id'] = pd.to_numeric(vmt['raster_id'], errors='coerce').astype('Int64')
        valid_vmt = vmt[vmt['raster_id'].between(1, 50)]
        invalid_vmt = vmt[~vmt['raster_id'].between(1, 50)]
        if not invalid_vmt.empty:
            logger.warning(f"Step 4: {len(invalid_vmt)} Misko_sklypai records have invalid 'raster_id' and will be excluded.")
        vmt = valid_vmt

        # Save processed file as GeoPackage with updated layer name if necessary
        vmt.to_file(vmt_out, layer="Misko_sklypai", driver="GPKG")
        processed_files.append(vmt_out)
        logger.info(f"Step 4: Processed Misko_sklypai saved to: {vmt_out} with {len(vmt)} records.")

    except Exception as e:
        logger.error(f"Step 4: Failed to process Misko_sklypai: {e}")
        raise
    finally:
        # Clean up memory
        del vmt
        gc.collect()

################################################################################
# Step 5: Process abandoned_2024
################################################################################

# Define output path
aband_out = os.path.join(output_dir, "abandoned_2024_filtered.gpkg")

# Check if output file already exists
if path_exists(aband_out, logger):
    logger.info(f"Step 5: {aband_out} already exists. Skipping processing abandoned_2024.")
    processed_files.append(aband_out)  # Append existing file to processed_files
else:
    try:
        # Read the GeoPackage file for abandoned_2024
        aband = gpd.read_file(input_layers["abandoned"])
        logger.info("Processing abandoned_2024...(Step 5 out of 9)")

        # Process data
        aband["LU"] = "A_"  # Add prefix for all rows

        # Merge with lookup table to add `raster_id`
        aband = aband.merge(lookup, how="left", on="LU")

        # Ensure 'raster_id' is integer and within 1-50
        aband['raster_id'] = pd.to_numeric(aband['raster_id'], errors='coerce').astype('Int64')
        valid_aband = aband[aband['raster_id'].between(1, 50)]
        invalid_aband = aband[~aband['raster_id'].between(1, 50)]
        if not invalid_aband.empty:
            logger.warning(f"Step 5: {len(invalid_aband)} abandoned_2024 records have invalid 'raster_id' and will be excluded.")
        aband = valid_aband

        # Save processed file as GeoPackage
        aband.to_file(aband_out, layer="abandoned_2024", driver="GPKG")
        processed_files.append(aband_out)
        logger.info(f"Step 5: Processed abandoned_2024 saved to: {aband_out} with {len(aband)} records.")

    except Exception as e:
        logger.error(f"Step 5: Failed to process abandoned_2024: {e}")
        raise
    finally:
        # Clean up memory
        del aband
        gc.collect()

################################################################################
# Step 6: Process gdr2024
################################################################################

# Define output path
gdr_out = os.path.join(output_dir, "gdr2024_filtered.gpkg")

# Check if output file already exists
if path_exists(gdr_out, logger):
    logger.info(f"Step 6: {gdr_out} already exists. Skipping processing gdr2024.")
    processed_files.append(gdr_out)  # Append existing file to processed_files
else:
    try:
        # Read the GeoPackage file for gdr2024
        gdr = gpd.read_file(input_layers["gdr"])
        logger.info("Processing gdr2024...(Step 6 out of 9)")

        # Filter and process data
        gdr = gdr[["GKODAS", "geometry"]]  # Keep only the "GKODAS" column and geometry
        gdr = gdr[~gdr["GKODAS"].isin(["pu0", "pu3"])]  # Exclude rows with these values
        gdr["LU"] = "G_" + gdr["GKODAS"].astype(str)  # Add prefix to "GKODAS"

        # Merge with lookup table to add `raster_id`
        gdr = gdr.merge(lookup, how="left", on="LU")

        # Ensure 'raster_id' is integer and within 1-50
        gdr['raster_id'] = pd.to_numeric(gdr['raster_id'], errors='coerce').astype('Int64')
        valid_gdr = gdr[gdr['raster_id'].between(1, 50)]
        invalid_gdr = gdr[~gdr['raster_id'].between(1, 50)]
        if not invalid_gdr.empty:
            logger.warning(f"Step 6: {len(invalid_gdr)} gdr2024 records have invalid 'raster_id' and will be excluded.")
        gdr = valid_gdr

        # Save processed file as GeoPackage
        gdr.to_file(gdr_out, layer="gdr2024", driver="GPKG")
        processed_files.append(gdr_out)
        logger.info(f"Step 6: Processed gdr2024 saved to: {gdr_out} with {len(gdr)} records.")

    except Exception as e:
        logger.error(f"Step 6: Failed to process gdr2024: {e}")
        raise
    finally:
        # Clean up memory
        del gdr
        gc.collect()

################################################################################
# Step 7: Process imperv2024
################################################################################

# Define output path
imperv_out = os.path.join(output_dir, "imperv2024_filtered.gpkg")

# Check if output file already exists
if path_exists(imperv_out, logger):
    logger.info(f"Step 7: {imperv_out} already exists. Skipping processing imperv2024.")
    processed_files.append(imperv_out)  # Append existing file to processed_files
else:
    try:
        # Read the GeoPackage file for imperv2024
        imperv = gpd.read_file(input_layers["imperv"])
        logger.info("Processing imperv2024...(Step 7 out of 9)")

        # Process data
        imperv["LU"] = "U_" + imperv["Cat"].astype(str)  # Add prefix to "Cat" values

        # Merge with lookup table to add `raster_id`
        imperv = imperv.merge(lookup, how="left", on="LU")

        # Ensure 'raster_id' is integer and within 1-50
        imperv['raster_id'] = pd.to_numeric(imperv['raster_id'], errors='coerce').astype('Int64')
        valid_imperv = imperv[imperv['raster_id'].between(1, 50)]
        invalid_imperv = imperv[~imperv['raster_id'].between(1, 50)]
        if not invalid_imperv.empty:
            logger.warning(f"Step 7: {len(invalid_imperv)} imperv2024 records have invalid 'raster_id' and will be excluded.")
        imperv = valid_imperv

        # Save processed file as GeoPackage
        imperv.to_file(imperv_out, layer="imperv2024", driver="GPKG")
        processed_files.append(imperv_out)
        logger.info(f"Step 7: Processed imperv2024 saved to: {imperv_out} with {len(imperv)} records.")

    except Exception as e:
        logger.error(f"Step 7: Failed to process imperv2024: {e}")
        raise
    finally:
        # Clean up memory
        del imperv
        gc.collect()

################################################################################
# Step 8: Rasterize Filtered Layers Based on raster_id
################################################################################

# Define rasterization parameters
raster_resolution = 5  # Resolution in meters

# Define the output directory for rasters
rasters_output_dir = os.path.join(output_dir, "rasters")
if not os.path.exists(rasters_output_dir):
    os.makedirs(rasters_output_dir, exist_ok=True)
    logger.info(f"Created rasters output directory: {rasters_output_dir}")
else:
    logger.info(f"Rasters output directory already exists: {rasters_output_dir}")

# Extract boundary information for raster extent and CRS
boundary_bounds = total_bounds  # [minx, miny, maxx, maxy]
boundary_crs = boundary.crs

# Calculate the number of pixels in x and y directions based on 5m resolution
width = math.ceil((boundary_bounds[2] - boundary_bounds[0]) / raster_resolution)
height = math.ceil((boundary_bounds[3] - boundary_bounds[1]) / raster_resolution)
logger.info(f"Raster dimensions: width={width}, height={height}")

# Define the transform for the raster
transform = from_origin(
    west=boundary_bounds[0],
    north=boundary_bounds[3],
    xsize=raster_resolution,
    ysize=raster_resolution
)

# Define the raster metadata with uint8 data type and nodata as 0
raster_meta = {
    "driver": "GTiff",
    "dtype": "uint8",       # Use uint8 for smaller file size
    "nodata": 0,             # 0 represents no-data
    "width": width,
    "height": height,
    "count": 1,
    "crs": boundary_crs,
    "transform": transform,
    "compress": "lzw"        # LZW compression to reduce file size
}

# Iterate through each processed GeoPackage file
for gpkg_path in processed_files:
    try:
        # Extract the layer name from the file name (without extension)
        layer_name = os.path.splitext(os.path.basename(gpkg_path))[0]
        logger.info(f"Rasterizing layer: {layer_name}")

        # Define the output raster file path
        raster_filename = f"{layer_name}.tif"
        raster_path = os.path.join(rasters_output_dir, raster_filename)

        # Check if the raster file already exists
        if os.path.exists(raster_path):
            logger.info(f"Raster file '{raster_filename}' already exists. Skipping rasterization for layer '{layer_name}'.")
            continue  # Skip rasterizing this layer

        # Read the GeoPackage layer
        gdf = gpd.read_file(gpkg_path)
        logger.info(f"Loaded {len(gdf)} features from {gpkg_path}")

        # Ensure the GeoDataFrame is in the target CRS
        if gdf.crs != boundary_crs:
            logger.info(f"Reprojecting {layer_name} to match boundary CRS.")
            gdf = gdf.to_crs(boundary_crs)

        # Check if GeoDataFrame is empty after reprojection
        if gdf.empty:
            logger.warning(f"No features to rasterize in layer '{layer_name}'. Skipping.")
            continue

        # Prepare shapes for rasterization: (geometry, raster_id)
        shapes = ((geom, value) for geom, value in zip(gdf.geometry, gdf['raster_id']))

        # Rasterize the GeoDataFrame
        logger.info(f"Starting rasterization for layer: {layer_name}")
        rasterized = rasterize(
            shapes=shapes,
            out_shape=(height, width),
            transform=transform,
            fill=0,                # 0 represents no-data
            all_touched=True,      # Pixels touched by geometries are burned
            dtype='uint8'          # Ensure raster data type is uint8
        )

        # Define the output raster file path (reiterated for clarity)
        # raster_filename = f"{layer_name}.tif"  # Already defined above
        # raster_path = os.path.join(rasters_output_dir, raster_filename)

        # Update metadata for the current raster
        current_meta = raster_meta.copy()
        current_meta.update({"count": 1, "dtype": "uint8"})  # Ensure dtype remains uint8

        # Write the raster to file
        with rasterio.open(raster_path, 'w', **current_meta) as dst:
            dst.write(rasterized, 1)
        logger.info(f"Saved raster: {raster_path}")

        # Clean up
        del rasterized
        gc.collect()

    except Exception as e:
        logger.error(f"Failed to rasterize GeoPackage '{gpkg_path}': {e}")
        continue  # Skip to the next layer

logger.info("Step 8: Rasterization of all filtered layers completed successfully.")

################################################################################
# Step 9: Combine Rasters Based on Priority
################################################################################

# Define the priority order (from highest to lowest)
priority_layers = [
    "Crops2024_filtered",
    "forest2022_filtered",
    "Misko_sklypai_filtered",
    "abandoned_2024_filtered",
    "gdr2024_filtered",
    "imperv2024_filtered"
]

# Define the output path for the combined raster
combined_raster_path = os.path.join(output_dir, "combined_raster.tif")

# Define the directory where rasters are stored
rasters_dir = os.path.join(output_dir, "rasters")

# Initialize variables to store metadata and the combined array
combined_array = None
raster_meta = None

# Flag to check if any rasters were successfully processed
rasters_processed = False

# Iterate through the priority layers
for layer in priority_layers:
    raster_filename = f"{layer}.tif"
    raster_path = os.path.join(rasters_dir, raster_filename)
    
    if not os.path.exists(raster_path):
        logger.error(f"Raster file not found: {raster_path}. Skipping this layer.")
        continue  # Skip to the next layer
    
    try:
        with rasterio.open(raster_path) as src:
            logger.info(f"Processing raster: {raster_filename}")
            
            # Read the raster data as uint8
            current_array = src.read(1).astype('uint8')
            
            # Initialize combined_array and raster_meta with the first raster
            if combined_array is None:
                combined_array = np.copy(current_array)
                raster_meta = src.meta.copy()
                rasters_processed = True
                logger.info(f"Initialized combined raster with {raster_filename}")
                continue  # Proceed to the next layer
            
            # Validate that current raster matches the combined raster's metadata
            if (src.width != raster_meta['width'] or
                src.height != raster_meta['height'] or
                src.transform != raster_meta['transform'] or
                src.crs != raster_meta['crs']):
                logger.error(f"Raster {raster_filename} does not match the combined raster's metadata. Skipping this layer.")
                continue  # Skip to the next layer
            
            # Identify cells in the combined raster that are currently no-data (0)
            # and need to be filled by the current lower priority raster
            mask = combined_array == raster_meta['nodata']
            
            # Update combined raster where mask is True and current raster has non-zero values
            # This ensures that only cells that are no-data in combined raster are filled
            fill_mask = (current_array != raster_meta['nodata']) & (current_array != 0)
            combined_array[mask & fill_mask] = current_array[mask & fill_mask]
            
            logger.info(f"Updated combined raster with {raster_filename}")
            
            # Clean up
            del current_array
            gc.collect()
            
    except Exception as e:
        logger.error(f"Failed to process raster {raster_filename}: {e}")
        continue  # Skip to the next layer

# After processing all layers, check if any rasters were successfully processed
if not rasters_processed:
    logger.error("No valid rasters were processed. Combined raster was not created.")
else:
    # Update metadata for the combined raster
    raster_meta.update({
        "dtype": "uint8",
        "count": 1,
        "compress": "lzw",
        "nodata": 0
    })
    
    try:
        # Write the combined raster to file
        with rasterio.open(combined_raster_path, 'w', **raster_meta) as dst:
            dst.write(combined_array, 1)
        logger.info(f"Combined raster saved to: {combined_raster_path}")
    except Exception as e:
        logger.error(f"Failed to write the combined raster: {e}")

# Clean up
if combined_array is not None:
    del combined_array
    gc.collect()
