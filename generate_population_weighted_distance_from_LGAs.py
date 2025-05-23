#  Created by Stephen Northey, University of Technology Sydney

import googlemaps
import csv
import configparser


def import_LGA_data(filename, state_filter="Australia"):
    lga_data = []
    with open(filename, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if state_filter == "Australia" or row.get("State") == state_filter:
                try:
                    lga_data.append({"State": str(row["State"]),
                                     "LGA": str(row['LGA']),
                                     "Name": str(row["Name"]),
                                     "Population": float(row["Population"]),
                                     "lat": float(row["Latitude"]),
                                     "lng": float(row["Longitude"])})
                except (ValueError, KeyError):
                    continue  # Skip rows with invalid or missing data
    return lga_data

def extract_origins_coordinates(lga_data):
    return [(d["lat"], d["lng"]) for d in lga_data]


def batch_distance_matrix(gmaps, origins, destination, batch_size=25):
    results = []
    for i in range(0, len(origins), batch_size):
        batch_origins = origins[i:i + batch_size]
        try:
            response = gmaps.distance_matrix(batch_origins, [destination], mode="driving", units="metric")
            results.extend(response["rows"])
        except Exception as e:
            print(f"Error in batch {i // batch_size + 1}: {e}")
            results.extend([{"elements": [{"status": "ERROR"}]}] * len(batch_origins))
    return results


def save_population_weighted_distance(lga_data, distance_results, output_filename_lga, output_filename_weighted_average):
    total_population = sum(d["Population"] for d in lga_data)
    total_weighted_distance = 0

    with open(output_filename_lga, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["State", "LGA", "Name", "Population", "Latitude", "Longitude", "Distance", "Population x Distance"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, result in enumerate(distance_results):
            distance_info = result["elements"][0]
            if distance_info["status"] == "OK":
                distance_value = distance_info["distance"]["value"] / 1000  # Convert meters to kilometers
                population_x_distance = float(lga_data[i]["Population"]) * distance_value
                total_weighted_distance += population_x_distance
                writer.writerow({
                    "State": lga_data[i]["State"],
                    "LGA":  lga_data[i]["LGA"],
                    "Name": lga_data[i]["Name"],
                    "Population": lga_data[i]["Population"],
                    "Latitude": lga_data[i]["lat"],
                    "Longitude": lga_data[i]["lng"],
                    "Distance": distance_value,
                    "Population x Distance": population_x_distance
                })
            else:
                writer.writerow({
                    "State": lga_data[i]["State"],
                    "LGA":  lga_data[i]["LGA"],
                    "Name": lga_data[i]["Name"],
                    "Population": lga_data[i]["Population"],
                    "Latitude": lga_data[i]["lat"],
                    "Longitude": lga_data[i]["lng"],
                    "Distance": "N/A",
                    "Population x Distance": "N/A"
                })

    weighted_average_distance = total_weighted_distance / total_population
    with open(output_filename_weighted_average, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Population Weighted Average Distance"])
        writer.writerow([weighted_average_distance])


if __name__ == "__main__":
    # Load configuration
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Google Maps API key
    api_key = config['googlemaps']['api_key']
    gmaps = googlemaps.Client(key=api_key)

    # File paths
    input_filename = config['files']['input_filename']
    output_filename_lga = config['files']['output_filename_lga']
    output_filename_weighted_average = config['files']['output_filename_weighted_average']

    # Destination coordinates
    destination = (float(config['destination']['latitude']), float(config['destination']['longitude']))

    # Import LGA data and extract origin locations and population
    lga_data = import_LGA_data(input_filename, state_filter=str(config['destination']['state_filter']))  # state_filter="New South Wales"
    origins = extract_origins_coordinates(lga_data)

    distance_results = batch_distance_matrix(gmaps, origins, destination, batch_size=int(config['googlemaps']['batch_size']))

    save_population_weighted_distance(lga_data, distance_results, "results_lga.csv", "results_weighted_average.csv")
