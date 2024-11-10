import os

# Set the root directory
root_dir = "recorded_data"
counter = 0

# Iterate through the directories in the root directory
for x_dir in os.listdir(root_dir):
    x_path = os.path.join(root_dir, x_dir)
    
    # Check if it's a directory and contains a status.txt file
    status_file = os.path.join(x_path, "status.txt")
    if os.path.isdir(x_path) and os.path.isfile(status_file):
        with open(status_file, "r") as file:
            status = file.read().strip()
            if status == "success":
                counter+=1
                print(f"{x_dir} has success in status file.")
print(counter)
