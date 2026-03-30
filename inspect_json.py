import json

# Corrected the file path to be relative to the script's execution directory
file_path = 'udise_api_dumps/tabular_map117_stateall_year22.json'

with open(file_path, 'r') as f:
    data = json.load(f)

# Check if 'rowValue' exists and is a list with at least one element
if 'rowValue' in data and isinstance(data['rowValue'], list) and len(data['rowValue']) > 0:
    # Get the first record from the 'rowValue' list
    first_record = data['rowValue'][0]
    
    # Print all keys in the first record, sorted for readability
    print("Keys available in the data records:")
    for key in sorted(first_record.keys()):
        print(key)
else:
    print("Could not find 'rowValue' or it is empty in the JSON file.")
