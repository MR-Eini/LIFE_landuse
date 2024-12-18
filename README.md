# LIFE Land Use Data Processing Pipeline

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
- [License](#license)

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

- **Data Loading & Validation:** Efficiently loads and validates multiple GeoPackage layers and lookup tables.
- **Geometry Cleaning:** Removes duplicate and invalid geometries, ensuring data integrity.
- **Coordinate Reference System (CRS) Management:** Ensures all spatial data layers share a consistent CRS.
- **Priority-Based Union:** Merges multiple layers based on predefined priority to resolve overlaps.
- **Rasterization:** Converts vector data into raster format with customizable resolution.
- **Combined Raster Output:** Generates a single raster dataset that integrates all processed layers based on priority.
- **Comprehensive Logging:** Tracks processing steps and errors for easy debugging and monitoring.
- **Memory Management:** Utilizes garbage collection to optimize memory usage during processing.

## Prerequisites

Before setting up the pipeline, ensure that your system meets the following requirements:

- **Operating System:** Windows, macOS, or Linux
- **Python Version:** Python 3.8 or higher

## Installation

1. **Clone the Repository**
   
   ```bash
   git clone https://github.com/MR-Eini/LIFE_landuse.git
   cd LIFE_landuse
