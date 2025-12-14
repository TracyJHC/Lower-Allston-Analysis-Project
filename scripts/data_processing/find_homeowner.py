import pandas as pd
import re

# --- Step 1: File Paths & Loading ---
# Make sure these filenames match what you have saved locally.
# If your script and data are in different folders, provide the full path.
voter_file = 'fa25-team-a/data/processed/voter_list_cleaned.csv'
property_file = 'fa25-team-a/data/raw/fy2025-property-assessment-data_12_30_2024.csv'

try:
    voters_df = pd.read_csv(voter_file, on_bad_lines='skip')
    properties_df = pd.read_csv(property_file, low_memory=False)
    print("✅ Two data files have been successfully loaded.")

except FileNotFoundError:
    print(f"❌ File loading error: File not found.")
    print("Please ensure the script and your two CSV files are located in the same folder, and that the filenames match the variables in the code.")
    exit()


# --- Step 2: Data Cleaning and Preparation ---

voters_df.columns = voters_df.columns.str.strip()
properties_df.columns = properties_df.columns.str.strip()

def standardize_address_string(text_series):
    """A powerful function for cleaning and standardizing address strings."""
    if not pd.api.types.is_string_dtype(text_series):
        text_series = text_series.astype(str)
    
    s = text_series.str.upper().str.strip()
    s = s.str.replace(r'[^\w\s]', '', regex=True)
    
    replacements = {
        r'\bSTREET\b': 'ST', r'\bAVENUE\b': 'AVE', r'\bROAD\b': 'RD',
        r'\bDRIVE\b': 'DR', r'\bPLACE\b': 'PL', r'\bBOULEVARD\b': 'BLVD',
        r'\bPARKWAY\b': 'PKWY', r'\bTERRACE\b': 'TER', r'\bCOMMONWEALTH\b': 'COMM'
    }
    for pattern, replacement in replacements.items():
        s = s.str.replace(pattern, replacement, regex=True)
    
    s = s.str.replace(r'\s+', ' ', regex=True)
    return s.fillna('')

# --- Step 3: Create standardized “full addresses” for both files for matching purposes. ---

# --- Processing Voter Files ---
voter_street_num = voters_df['Street .'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
voter_street_name = standardize_address_string(voters_df['Street Name'])
voters_df['full_address'] = (voter_street_num + ' ' + voter_street_name).str.strip().str.replace(r'\s+', ' ', regex=True)


# --- Processing Property File) ---
prop_street_num = properties_df['ST_NUM'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
prop_street_name = standardize_address_string(properties_df['ST_NAME'])
properties_df['full_address'] = (prop_street_num + ' ' + prop_street_name).str.strip().str.replace(r'\s+', ' ', regex=True)


# --- Step 4: [Debugging Phase] Inspect the cleaned address samples. ---
print("\n--- Debugging Information: Standardized Address Samples ---")
print("## ✅ Sample Voter Document Address:")
print(voters_df['full_address'].head(10))
print("\n## ✅ Sample Property Document Address:")
print(properties_df['full_address'].head(10))
print("-----------------------------------------------------\n")


# --- Step 5: Merge the two datasets ---

merged_df = pd.merge(voters_df, properties_df, on='full_address', how='inner')
print(f"📊 Inital match: according to street adresses，found {len(merged_df)} potential matches")

merged_df['Apt .'] = merged_df['Apt .'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.upper().replace(['NAN', ''], 'NO_APT')
merged_df['UNIT_NUM'] = merged_df['UNIT_NUM'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.upper().replace(['NAN', ''], 'NO_APT')

final_matches = merged_df[merged_df['Apt .'] == merged_df['UNIT_NUM']].copy()
print(f"📊 Precicse match: After filtering by apartment/unit number, {len(final_matches)} exact matches remain.")


# --- Step 6: Screen homeowners and compile final results ---

homeowners_df = final_matches[final_matches['OWN_OCC'] == 'Y']

final_columns = ['Res ID', 'Last Name', 'First Name', 'MI', 'DOB', 'Occupation', 'Street .', 'Sffx', 'Street Name', 'Apt .', 'Zip', 'Ward', 'Precinct']
final_columns_exist = [col for col in final_columns if col in homeowners_df.columns]
homeowner_voters = homeowners_df[final_columns_exist].copy()
homeowner_voters.drop_duplicates(subset=['Res ID'], inplace=True)


# --- Step 7: Output the results ---

if len(homeowner_voters) > 0:
    homeowner_voters.to_csv('fa25-team-a/data/processed/homeowner_voters_list.csv', index=False)
    print(f"\n🎉 Success！Recongnized {len(homeowner_voters)} homeowners")
    print("Result saved to: 'homeowner_voters_list.csv'")
else:
    print("\n❌ Processing completed, but no homeowner voters were found.")