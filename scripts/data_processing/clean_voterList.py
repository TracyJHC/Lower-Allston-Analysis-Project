import pandas as pd

# Define the columns of interest
columns_of_interest = [
    "Res ID",
    "Last Name",
    "First Name",
    "Street .",
    "Sffx",
    "Street Name",
    "Apt .",
    "Zip",
    "Ward",
    "Precinct",
    "DOB",
    "Occupation"
]

# Path to the raw voter list Excel file
input_path = "fa25-team-a/data/raw/Voter List - Ward 21 and 22.xls"

# Read the Excel file
df = pd.read_excel(input_path)

# Select only the columns of interest (keep only those that exist in the file)
existing_cols = [col for col in columns_of_interest if col in df.columns]
cleaned_df = df[existing_cols]

# Save the cleaned dataset to a new file
output_path = "fa25-team-a/data/processed/voter_list_cleaned.csv"
cleaned_df.to_csv(output_path, index=False)

print(f"Cleaned voter list saved to {output_path}")
