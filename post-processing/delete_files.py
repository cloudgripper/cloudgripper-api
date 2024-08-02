import os
import shutil


def delete_files_and_directories(root_dir, x_range):
    for x in x_range:
        status_json_path = os.path.join(
            root_dir, f"stack_from_scratch/recorded_data/{x}/status.txt"
        )
        orders_json_path = os.path.join(
            root_dir, f"stack_from_scratch/recorded_data/{x}/task/orders.json"
        )
        final_image_dir = os.path.join(
            root_dir, f"stack_from_scratch/recorded_data/{x}/task/Final_Image"
        )
        restore_dir = os.path.join(
            root_dir, f"stack_from_scratch/recorded_data/{x}/restore"
        )

        # Delete status.json
        if os.path.exists(status_json_path):
            os.remove(status_json_path)
            print(f"Deleted: {status_json_path}")

        # Delete orders.json
        if os.path.exists(orders_json_path):
            os.remove(orders_json_path)
            print(f"Deleted: {orders_json_path}")

        # Delete Final_Image directory and its contents
        if os.path.exists(final_image_dir):
            shutil.rmtree(final_image_dir)
            print(f"Deleted directory: {final_image_dir}")

        # Delete restore directory and its contents
        if os.path.exists(restore_dir):
            shutil.rmtree(restore_dir)
            print(f"Deleted directory: {restore_dir}")


# Example usage:
root_directory = ""
x_values_range = range(1, 207)  # Example range, adjust as needed
delete_files_and_directories(root_directory, x_values_range)
