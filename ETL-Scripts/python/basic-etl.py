import pandas as pd

# Extract: Read data from a CSV file
def extract(file_path):
    return pd.read_csv(file_path)

# Transform: Perform some data processing
def transform(data):
    # Example transformation: Add a new column with uppercase values of an existing column
    if 'name' in data.columns:
        data['name_uppercase'] = data['name'].str.upper()
    return data

# Load: Write the data to a new CSV file
def load(data, output_path):
    data.to_csv(output_path, index=False)

# Main ETL process
def etl_process(input_file, output_file):
    # Extract
    data = extract(input_file)
    print("Extraction complete.")

    # Transform
    transformed_data = transform(data)
    print("Transformation complete.")

    # Load
    load(transformed_data, output_file)
    print("Load complete.")

# Example usage
if __name__ == "__main__":
    input_file = "input_data.csv"  # Replace with your input file path
    output_file = "output_data.csv"  # Replace with your desired output file path

    etl_process(input_file, output_file)