import matplotlib.pyplot as plt

# Step 1: Read the txt file
file_name = "./txt/foam_triple_occu_rate_new.txt"  # Replace with the name of your txt file

with open(file_name, 'r') as f:
    lines = f.readlines()

# Convert lines to float
values = [float(line.strip()) for line in lines]

# Step 2: Create the histogram
bins = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
counts, _, patches = plt.hist(values, bins=bins, edgecolor='black')

# Annotate the number of data points in each bin
for count, patch in zip(counts, patches):
    plt.text(patch.get_x() + patch.get_width() / 2, patch.get_height(), f'{int(count)}', ha='center', va='bottom')

# Add title and labels
plt.title(f"Histogram of Numbers from {file_name}")
plt.xlabel("Value Range")
plt.ylabel("Frequency")

# Step 3: Save the figure with the name of the txt file
png_file_name = file_name.rsplit('.', 1)[0] + '.png'  # Replace the last '.' with '.png'
plt.savefig(png_file_name)

# Show the plot
plt.show()
