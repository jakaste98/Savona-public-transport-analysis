# Savona_public_transport_analysis

## Overview
This repository contains the Urban Mobility Analysis project, focused on analyzing and optimizing the public transportation network in Savona. Utilizing data retrieved from TPL Savona site, the project aims to identify inefficiencies in the bus network and propose optimizations for improved urban mobility.

## Contents

**ORARI_MERGED.csv**: raw CSV file with data retrieved from the PDF timetables in Savona's TPL site.  
**all_routes**: CSV outcome of the ORARI_MERGED data cleaning process  
**all_routes_with_coords.csv**: CSV file containing bus routes, stop names, times, and coordinates.  
**requirements.txt**: List of Python packages required to run the project.  
**public_transport**: Python script to initially implement a data cleaning.  
**coord_retriever**: Python script to retrieve the coordinates.  
**optimizer_final.py**: Main Python script containing data processing, analysis, and visualization code.  
**visualizations**: containing all generated visualizations (maps, network graphs).

## Project Structure

**Data Preprocessing**: Standardizing and cleaning the provided transportation data.  
**Geospatial Analysis**: Mapping and analyzing the geographical distribution of bus stops.  
**Network Analysis**: Constructing and visualizing a network graph of the bus routes.  
**Outlier Analysis**: Identifying and removing outliers to refine the network analysis.  
**Route Optimization**: Analyzing the network for overlapping and under-served routes and proposing optimizations.  
**Hypothetical Adjustments**: Simulating proposed changes to the network and visualizing the adjusted network.

## Setup and Installation
To set up this project locally, follow these steps:
  
Clone this repository.  
Install the required Python packages: pip install -r requirements.txt.  
Run the urban_mobility_analysis.py script to reproduce the analysis.  
## Methodologies and Tools  

**Data Preprocessing**: Pandas for data cleaning and manipulation performed initially using ORARI_MERGED as data file and public_transport.py for the code. Then, by using the outcome of the aforementioned code (all_routes) in combination with coord_retriever for code part, the coordinates are retrieved to then move to optimizer_final.py (code) and all_routes_with_coords (data file - outcome of all_routes.csv) 
 
**Geospatial Analysis**: Geopandas and Folium for mapping bus stops.  
**Network Analysis**: NetworkX for constructing and analyzing the bus route network, and Matplotlib for visualization.  
**Simulation of Adjustments**: Hypothetical scenarios of route optimizations.

## Results and Visualizations
The project includes several visualizations:

Maps showing the geographical distribution of bus stops.  
Network graphs depicting the bus network, both original and post-optimization.  
Graphs highlighting areas of high and low connectivity.  
These visualizations are available in the visualizations folder.
