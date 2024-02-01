import pandas as pd

# Path to the CSV file
csv_file_path = 'C:\\Users\\giaco\\OneDrive\\Desktop\\ORARI_MERGED.csv'

# Read the CSV file, assuming that semicolon is the delimiter
df = pd.read_csv(csv_file_path, delimiter=';')

# Initialize an empty DataFrame to store all routes
all_routes = pd.DataFrame()

# Variables to keep track of the current bus route and stops
current_route = None
stops_data = []

# Iterate over each row in the dataframe
for index, row in df.iterrows():
    # Check for 'LINEA' to indicate a new route
    if str(row[0]).startswith('LINEA'):
        # If there's an existing route being processed, convert it to a DataFrame
        if current_route and stops_data:
            # Determine the number of columns based on the maximum number of columns encountered
            num_columns = max(len(stop_times) for stop_times in stops_data)
            columns = ['Stop Name'] + [f'Time {i}' for i in range(1, num_columns)]
            route_df = pd.DataFrame(stops_data, columns=columns)
            route_df.insert(0, 'Route', current_route)  # Insert the route name as the first column
            all_routes = pd.concat([all_routes, route_df])  # Concatenate to the main DataFrame
            stops_data = []  # Reset for the next route
        current_route = str(row[0]).split(' ')[1]  # Extract the route number or name
    else:
        # Collect stop names and times, filtering out any empty strings
        stop_times = [item for item in row if pd.notna(item) and str(item) != '']
        if stop_times:  # If the list is not empty, append it to the stops_data
            stops_data.append(stop_times)

# Don't forget to add the last route's data after the loop ends
if current_route and stops_data:
    # Determine the number of columns based on the maximum number of columns encountered
    num_columns = max(len(stop_times) for stop_times in stops_data)
    columns = ['Stop Name'] + [f'Time {i}' for i in range(1, num_columns)]
    route_df = pd.DataFrame(stops_data, columns=columns)
    route_df.insert(0, 'Route', current_route)
    all_routes = pd.concat([all_routes, route_df])

# Reset the index of the final DataFrame
all_routes.reset_index(drop=True, inplace=True)

# Save to a new CSV file or process further
all_routes.to_csv('C:\\Users\\giaco\\OneDrive\\Desktop\\all_routes.csv', index=False)

# Print out a sample to check
print(all_routes.head())
