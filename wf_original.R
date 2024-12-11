# Load required packages
library(sf)
library(dplyr)
library(terra)
library(readxl)
gc()

################################################################################
# PART 1: Cleaning and filtering input files 
################################################################################
# Define paths
output_dir <- "D:\\Users\\MRE\\Landuse_output"

# 1. Process Crops2024.gpkg
crops_path <- "G:\\LIFE_AAA\\swat_lt\\Data\\LandUse\\Landuse_update\\2024\\inputs\\Crops2024.gpkg"
crops <- st_read(crops_path, quiet = TRUE) %>%
  select(KODAS) %>%
  filter(!KODAS %in% c("NEP", "TPN")) %>%  # Remove rows with "NEP" or "TPN"
  mutate(LU = paste0("C_", KODAS)) %>%    # Add "C_" before all remaining KODAS
  select(LU)                             # Keep only the LU column

# View the first few rows of the processed data
print("Head of processed Crops2024 with LU column:")
print(head(crops))

# Save the processed file
crops_out <- file.path(output_dir, "Crops2024_filtered.gpkg")
st_write(crops, crops_out, delete_layer = TRUE, quiet = TRUE)

# Cleanup
rm(crops)
gc()
###########################################

# 2. Process forest2022.gpkg
forest_path <- "G:\\LIFE_AAA\\swat_lt\\Data\\Landuse\\Landuse_update\\inputs\\forest2022.gpkg"
forest <- st_read(forest_path, quiet = TRUE) %>%
  select(augaviete) %>%
  filter(augaviete %in% c("Pa", "Pan", "Pb")) %>%
  mutate(
    # Create LU column with "W_" + augaviete
    LU = paste0("W_", augaviete)
  ) %>%
  select(LU)  # Keep only the LU column

# View the first few rows of the processed data
print("Head of processed forest2022 with LU column:")
print(head(forest))

# Save the processed file
forest_out <- file.path(output_dir, "forest2022_filtered.gpkg")
st_write(forest, forest_out, delete_layer = TRUE, quiet = TRUE)

# Cleanup
rm(forest)
gc()
###########################################

# 3. Process VMT_MKD.gdb (Misko_sklypai layer)
vmt_path <- "G:\\LIFE_AAA\\swat_lt\\Data\\LandUse\\Landuse_update\\2024\\raw\\forest\\VMT_MKD.gdb"
vmt <- st_read(vmt_path, layer = "Misko_sklypai", quiet = TRUE) %>%
  select(zkg, VMR) %>%
  mutate(
    # Create LU column with "F_" + zkg + "_" + VMR
    LU = paste0("F_", zkg, "_", ifelse(is.na(VMR), "None", VMR))
  ) %>%
  select(LU)  # Keep only the LU column

# View the first few rows of the processed data
print("Head of processed VMT_MKD with LU column:")
print(head(vmt))

# Save the processed file
vmt_out <- file.path(output_dir, "VMT_MKD_filtered.gpkg")
st_write(vmt, vmt_out, delete_layer = TRUE, quiet = TRUE)

# Cleanup
rm(vmt)
gc()
###########################################

# 4. Process abandoned_2024.gpkg
aband_path <- "G:\\LIFE_AAA\\swat_lt\\Data\\LandUse\\Landuse_update\\2024\\inputs\\abandoned_2024.gpkg"
aband <- st_read(aband_path, quiet = TRUE) %>%
  mutate(LU = "A_") %>%  # Add LU column with "A_" for all rows
  select(LU)             # Keep only the LU column

# View the first few rows of the processed data
print("Head of processed abandoned_2024 with LU column:")
print(head(aband))

# Save the processed file
aband_out <- file.path(output_dir, "abandoned_2024_filtered.gpkg")
st_write(aband, aband_out, delete_layer = TRUE, quiet = TRUE)

# Cleanup
rm(aband)
gc()
###########################################

# 5. Process gdr2024.gpkg
gdr_path <- "G:\\LIFE_AAA\\swat_lt\\Data\\LandUse\\Landuse_update\\2024\\inputs\\gdr2024.gpkg"
gdr <- st_read(gdr_path, quiet = TRUE) %>%
  select(GKODAS) %>%
  filter(!GKODAS %in% c("pu0", "pu3")) %>%  # Remove rows with "pu0" or "pu3"
  mutate(LU = paste0("G_", GKODAS)) %>%    # Add "G_" before GKODAS
  select(LU)                              # Keep only the LU column

# View the first few rows of the processed data
print("Head of processed gdr2024 with LU column:")
print(head(gdr))

# Save the processed file
gdr_out <- file.path(output_dir, "gdr2024_filtered.gpkg")
st_write(gdr, gdr_out, delete_layer = TRUE, quiet = TRUE)

# Cleanup
rm(gdr)
gc()
###########################################

# 6. Process imperv2024.gpkg
imperv_path <- "G:\\LIFE_AAA\\swat_lt\\Data\\LandUse\\Landuse_update\\2024\\inputs\\imperv2024.gpkg"
imperv <- st_read(imperv_path, quiet = TRUE) %>%
  select(Cat) %>%
  mutate(LU = paste0("U_", Cat)) %>%  # Add "U_" before Cat values
  select(LU)                          # Keep only the LU column

# View the first few rows of the processed data
print("Head of processed imperv2024 with LU column:")
print(head(imperv))

# Save the processed file
imperv_out <- file.path(output_dir, "imperv2024_filtered.gpkg")
st_write(imperv, imperv_out, delete_layer = TRUE, quiet = TRUE)

# Cleanup
rm(imperv)
gc()

################################################################################
####### Optional: 
####### To check if there are new LU codes and should be compared with lookup.csv
################################################################################
### Open filtered maps, extract unique LU values, and save results to CSV
# Define file paths for filtered datasets
filtered_files <- list(
  list(file = crops_out, csv = file.path(output_dir, "unique_LU_Crops2024.csv")),
  list(file = forest_out, csv = file.path(output_dir, "unique_LU_forest2022.csv")),
  list(file = vmt_out, csv = file.path(output_dir, "unique_LU_VMT_MKD.csv")),
  list(file = aband_out, csv = file.path(output_dir, "unique_LU_abandoned_2024.csv")),
  list(file = gdr_out, csv = file.path(output_dir, "unique_LU_gdr2024.csv")),
  list(file = imperv_out, csv = file.path(output_dir, "unique_LU_imperv2024.csv"))
)

# Process each file
for (entry in filtered_files) {
  # Read the filtered file
  filtered_data <- st_read(entry$file, quiet = TRUE)
  
  # Extract unique LU values
  unique_lu <- unique(filtered_data$LU)
  
  # Save the unique LU values to a CSV file
  write.csv(data.frame(LU = unique_lu), entry$csv, row.names = FALSE)
  
  # Print a message
  cat("Unique LU values saved to:", entry$csv, "\n")
  
  # Clean up to free memory
  rm(filtered_data, unique_lu)
  gc()
}
################################################################################
# End PART 1 
################################################################################


################################################################################
# PART 2: Create New Raster
################################################################################
gc()

# Define paths
output_dir <- "D:\\Users\\MRE\\Landuse_output"
reference_raster_path <- "D:\\Users\\MRE\\LUraster_bck.tif"
lookup_path <- "G:\\LIFE_AAA\\swat_lt\\Data\\LandUse\\landuse_MRE\\lookup.xlsx"
previous_raster_path <- "D:\\Users\\MRE\\LUraster.tif"

# Paths to filtered datasets
crops_out <- file.path(output_dir, "Crops2024_filtered.gpkg")
forest_out <- file.path(output_dir, "forest2022_filtered.gpkg")
vmt_out <- file.path(output_dir, "VMT_MKD_filtered.gpkg")
aband_out <- file.path(output_dir, "abandoned_2024_filtered.gpkg")
gdr_out <- file.path(output_dir, "gdr2024_filtered.gpkg")
imperv_out <- file.path(output_dir, "imperv2024_filtered.gpkg")

# Output raster path
final_raster_path <- file.path(output_dir, "Final_Landuse_Raster.tif")
comparison_csv_path <- file.path(output_dir, "Landuse_Change_Comparison.csv")

# Load lookup table
lookup <- read_excel(lookup_path)

# Paths to filtered datasets
filtered_files <- list(
  crops_out = crops_out,
  forest_out = forest_out,
  vmt_out = vmt_out,
  aband_out = aband_out,
  gdr_out = gdr_out,
  imperv_out = imperv_out
)

# Load reference raster to define extent, resolution, and CRS
ref_raster <- rast(reference_raster_path)

# Fix CRS issue by explicitly setting a compatible CRS
custom_crs <- "PROJCS[\"LKS94 / Lithuania TM\", 
    GEOGCS[\"LKS94\", 
        DATUM[\"Lithuania_1994\", 
            SPHEROID[\"GRS 1980\",6378137,298.257222101]], 
        PRIMEM[\"Greenwich\",0], 
        UNIT[\"degree\",0.0174532925199433]], 
    PROJECTION[\"Transverse_Mercator\"], 
    PARAMETER[\"latitude_of_origin\",0], 
    PARAMETER[\"central_meridian\",24], 
    PARAMETER[\"scale_factor\",0.9998], 
    PARAMETER[\"false_easting\",500000], 
    PARAMETER[\"false_northing\",0], 
    UNIT[\"metre\",1]]"
crs(ref_raster) <- custom_crs

# Initialize the final raster with NA values
final_raster <- rast(ref_raster)
values(final_raster) <- NA

# Rasterize and merge layers in sequence using lookup
for (file_name in names(filtered_files)) {
  file_path <- filtered_files[[file_name]]
  
  # Load the filtered vector file
  layer <- st_read(file_path, quiet = TRUE)
  
  # Fix CRS for vector layer if needed
  if (!st_crs(layer) == st_crs(custom_crs)) {
    cat("Transforming CRS for:", file_name, "\n")
    layer <- st_transform(layer, custom_crs)
  }
  
  # Join with lookup table to get raster_id
  layer <- layer %>%
    left_join(lookup, by = c("LU" = "LU")) %>%
    filter(!is.na(raster_id))  # Ensure raster_id is present
  
  # Rasterize using raster_id
  layer_raster <- rasterize(
    vect(layer),          # Vector data
    ref_raster,           # Template raster
    field = "raster_id",  # Field to rasterize
    touches = TRUE        # Allow overlapping polygons
  )
  
  # Update final raster: keep values in final_raster, fill only NA cells with layer_raster
  final_raster <- cover(final_raster, layer_raster)
  
  # Clean up to save memory
  rm(layer, layer_raster)
  gc()
}

# Save the final merged raster
writeRaster(final_raster, final_raster_path, overwrite = TRUE)
cat("Final merged raster saved to:", final_raster_path, "\n")

# QA: Compare previous raster with the new raster
if (file.exists(previous_raster_path)) {
  previous_raster <- rast(previous_raster_path)
  
  # Fix CRS for previous raster if needed
  if (!crs(previous_raster) == custom_crs) {
    cat("Transforming CRS for previous raster.\n")
    crs(previous_raster) <- custom_crs
  }
  
  # Ensure same extent and resolution
  previous_raster <- resample(previous_raster, ref_raster, method = "near")
  
################################################################################
####### Optional: 
####### Compare previous raster with the new raster
################################################################################
  
  # Compare cell values
  comparison <- crosstab(previous_raster, final_raster, long = TRUE)
  names(comparison) <- c("Previous", "New", "Count")
  
  # Save comparison as CSV
  write.csv(comparison, comparison_csv_path, row.names = FALSE)
  cat("Landuse change comparison saved to:", comparison_csv_path, "\n")
  
  # Cleanup
  rm(previous_raster, comparison)
  gc()
} else {
  cat("Previous raster not found. Skipping comparison.\n")
}


################################################################################
# End PART 2 
################################################################################

