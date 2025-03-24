import pandas as pd

# Extract: Read data from a CSV file
def extract(file_path):
    return pd.read_csv(file_path)

# Transform: Clean and transform the data
def transform(data):
    # Normalize column names
    data.columns = data.columns.str.strip().str.lower()
    
    # Handle 'age' column: convert to numeric, drop NaNs, filter > 25
    if 'age' in data.columns:
        data['age'] = pd.to_numeric(data['age'], errors='coerce')
        before_rows = data.shape[0]
        data = data[data['age'] > 25].copy()  # <-- Make a copy here
        after_rows = data.shape[0]
        print(f"Filtered out {before_rows - after_rows} rows with age <= 25 or invalid age.")
    else:
        print("Warning: 'age' column not found. Skipping age filter.")

    # Handle 'salary' column
    if 'salary' in data.columns:
        data['salary'] = pd.to_numeric(data['salary'], errors='coerce')
        data['bonus'] = data['salary'] * 0.1
    else:
        print("Warning: 'salary' column not found. Skipping bonus calculation.")

    # Rename 'name' column
    if 'name' in data.columns:
        data.rename(columns={'name': 'full_name'}, inplace=True)
    else:
        print("Info: 'name' column not found. No renaming applied.")

    return data

# Load: Write the data to a new CSV file
def load(data, output_path):
    data.to_csv(output_path, index=False)
    print(f"Data successfully saved to {output_path}")

# Main ETL process
def etl_process(input_file, output_file):
    print("Starting ETL process...")
    try:
        # Extract
        data = extract(input_file)
        print("Extraction complete.")
        
        # Transform
        transformed_data = transform(data)
        print("Transformation complete.")
        
        # Load
        load(transformed_data, output_file)
        print("Load complete.")
    except Exception as e:
        print(f"ETL process failed: {e}")

# Example usage
if __name__ == "__main__":
    input_file = "input_data.csv"       # Replace with your input file path
    output_file = "output_data.csv"     # Replace with your output file path
    etl_process(input_file, output_file)
