import json
import os
import sys

def load_json(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def find_latest_order(time, orders):
    latest_order = None
    for order in orders:
        if order['time'] <= time:
            if latest_order is None or order['time'] > latest_order['time']:
                latest_order = order
    return latest_order

def combine_robot_data(states, orders):
    combined_data = []
    for state in states:
        latest_order = find_latest_order(state['time'], orders)
        combined_entry = state.copy()
        if latest_order:
            combined_entry.update(latest_order)
        combined_data.append(combined_entry)
    return combined_data

def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

def process_directory(directory):
    states_path = os.path.join(directory, 'states.json')
    orders_path = os.path.join(directory, 'orders.json')
    if os.path.exists(states_path) and os.path.exists(orders_path):
        robot_states = load_json(states_path)
        robot_orders = load_json(orders_path)

        combined_data = combine_robot_data(robot_states, robot_orders)

        output_path = os.path.join(directory, 'combined_robot_data.json')
        save_json(combined_data, output_path)
        print(f"Combined data has been saved to {output_path}")

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <min_x> <max_x>")
        sys.exit(1)
    
    min_x = int(sys.argv[1])
    max_x = int(sys.argv[2])
    
    base_directory = 'stack_from_scratch/recorded_data'
    for root, dirs, files in os.walk(base_directory):
        for dir_name in dirs:
            try:
                x = int(dir_name)
                if min_x <= x <= max_x:
                    process_directory(os.path.join(root, dir_name))
            except ValueError:
                # Skip directories that do not match the expected format
                continue

if __name__ == "__main__":
    main()

