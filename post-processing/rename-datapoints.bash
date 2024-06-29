#!/bin/bash

rename_subdirectories() {
  local base_directory=$1
  local temp_directory="$base_directory/temp_rename"

  # Create a temporary directory to avoid name conflicts during renaming
  mkdir -p "$temp_directory"

  # Find all directories with integer names and sort them
  local -a directories=($(find "$base_directory" -maxdepth 1 -mindepth 1 -type d -regex '.*/[0-9]+' | sort -V))

  # Rename directories to temporary names to avoid conflicts
  local count=1
  for dir in "${directories[@]}"; do
    mv "$dir" "$temp_directory/$count"
    ((count++))
  done

  # Move directories back to the base directory with new names
  mv "$temp_directory"/* "$base_directory"
  rmdir "$temp_directory"

  echo "Renaming complete. Directories have been renamed in ascending order starting from 1."
}

main() {
  # Example usage
  local base_directory="stack_from_scratch/recorded_data"
  rename_subdirectories "$base_directory"
}

# Run the main function
main
