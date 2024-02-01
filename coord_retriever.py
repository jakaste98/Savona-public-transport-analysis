# -*- coding: utf-8 -*-
"""
Created on Wed Jan 31 14:57:38 2024

@author: giaco
"""

import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter


csv_file_path = 'C:\\Users\\giaco\\OneDrive\\Desktop\\all_routes.csv'
df = pd.read_csv(csv_file_path,delimiter=';')

# Initialize Nominatim Geocoder
geolocator = Nominatim(user_agent="Savona_urban_mobility_analysis")

# To prevent spamming the service with requests, wrap the geocode call in a RateLimiter
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Define a function to append ', Savona, Italy' to the stop name and geocode it
def geocode_stop(stop):
    try:
        # Append ', Savona, Italy' to the stop name to specify the location
        location = geocode(f"{stop}, Savona, Italy")
        return (location.latitude, location.longitude) if location else (None, None)
    except Exception as e:
        print(f"Error geocoding {stop}: {e}")
        return None, None

# Create new columns for latitude and longitude
df['Latitude'] = None
df['Longitude'] = None

# Iterate over the stop names in the DataFrame and geocode them
for index, stop_name in enumerate(df['Stop Name'].unique()):
    lat, lon = geocode_stop(stop_name)
    df.loc[df['Stop Name'] == stop_name, 'Latitude'] = lat
    df.loc[df['Stop Name'] == stop_name, 'Longitude'] = lon

# Save the updated DataFrame to a new CSV file
# Save to a new CSV file
# it is now insert as commented, having already the outcome file in /data
output_csv_path = 'C:\\Users\\giaco\\OneDrive\\Desktop\\all_routes_with_coords.csv'
df.to_csv(output_csv_path, index=False)

# Show the first few rows of the updated DataFrame
print(df.head())
