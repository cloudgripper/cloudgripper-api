#!/bin/bash

delete_fail_subdirectories() {
  local base_directory=$1

  # Iterate through all items in the base directory
  for item in "$base_directory"/*; do
    if [ -d "$item" ] && [[ $(basename "$item") =~ ^[0-9]+$ ]]; then
      status_file="$item/status.txt"
      final_image_directory="$item/task/Final_Image"

      # Check if status.txt exists in the directory
      if [ -f "$status_file" ]; then
        status_content=$(< "$status_file")

        # Check if the status file contains only the word "fail"
        if [ "$status_content" == "fail" ]; then
          # Delete the subdirectory
          rm -rf "$item"
          echo "Deleted directory: $item"
        fi
      else
        # Create status.txt with content "success" if it doesn't exist
        echo "success" > "$status_file"
        echo "Created status.txt with content 'success' in $item"
      fi

      # Check if Final_Image directory is empty
      if [ -d "$final_image_directory" ] && [ -z "$(ls -A "$final_image_directory")" ]; then
        # Delete the subdirectory
        rm -rf "$item"
        echo "Deleted directory due to empty Final_Image: $item"
      fi
    fi
  done
}

main() {
  # Example usage
  local base_directory="stack_from_scratch/recorded_data"
  delete_fail_subdirectories "$base_directory"
}

# Run the main function
main
