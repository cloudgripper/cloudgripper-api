import os
import json

# Base directory containing the JSON files
base_dir = "stack_from_scratch/recorded_data"

# Iterate through directories from 1 to 20
for x in range(1, 36):
    # Construct the path to the states.json file
    json_file_path = os.path.join(base_dir, str(x), "task", "states.json")

    # Check if the file exists
    if os.path.exists(json_file_path):
        try:
            # Read the JSON data from the file
            with open(json_file_path, "r") as file:
                data = json.load(file)

            # Check if data is not empty
            if data:
                # Get the initial time value
                initial_time = data[0]["time"]

                # Modify the time values to be relative to the initial time
                for entry in data:
                    entry["time"] = entry["time"] - initial_time

                # Write the modified data back to the JSON file
                with open(json_file_path, "w") as file:
                    json.dump(data, file, indent=4)
            else:
                print(f"No data found in {json_file_path}")

        except json.JSONDecodeError as e:
            print(f"Error decoding JSON in file {json_file_path}: {e}")
        except Exception as e:
            print(f"An error occurred while processing file {json_file_path}: {e}")

    else:
        print(f"File not found: {json_file_path}")

print("Time values updated successfully.")
