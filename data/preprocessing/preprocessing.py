import csv
from collections import defaultdict
import json
import re

# Input CSV file and output CSV file
input_file = '../lemma_senses/csv/lemma_senses.csv'
output_file = '../lemma_senses/csv/lemma_senses_prep.csv'

# Function to remove "null" values and tags from the senses column
def remove_null_senses(senses_str):
    try:
        # Define a regular expression pattern to match and remove various XML-like tags
        pattern = r'<[^>]+>'

        # Parse the JSON string
        senses_list = json.loads(senses_str)

        # Remove "null" and None values from the list
        cleaned_senses = []
        for sense in senses_list:
            if sense is not None and sense != "null":
                # Remove tags from the sense text
                cleaned_sense = re.sub(pattern, '', sense)
                cleaned_senses.append(cleaned_sense.strip())  # Strip leading/trailing whitespace

        # Join cleaned senses with ';' as the separator
        cleaned_senses_str = '; '.join(cleaned_senses)

        return cleaned_senses_str
    except Exception as e:
        return senses_str  # Return the original string if there was an error

# Open input and output files
with open(input_file, mode='r', newline='') as input_csv, \
     open(output_file, mode='w', newline='') as output_csv:

    # Create CSV reader and writer objects
    reader = csv.DictReader(input_csv, delimiter='\t')
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(output_csv, fieldnames=fieldnames, delimiter='\t')

    # Initialize counters
    total_entries_before = 0
    total_entries_after = 0
    language_code_counts_before = defaultdict(int)
    language_code_counts_after = defaultdict(int)

    # Write the header to the output file
    writer.writeheader()

    # Iterate through rows in the input CSV file
    for row in reader:
        # Increment the total entries before cleaning
        total_entries_before += 1

        # Count entries for each language code before cleaning
        language_code_counts_before[row['language_code']] += 1

        # Check if the "senses" column contains any variations of [null], '?', or None
        senses = row['senses']
        if senses and senses != '[null]' and senses != '[null, null]' and '?' not in senses:
            # Remove "null" and None values from the 'senses' column and tags
            row['senses'] = remove_null_senses(row['senses'])

            # Write the row to the output CSV file
            writer.writerow(row)

            total_entries_after += 1
            # Count entries for each language code after cleaning
            language_code_counts_after[row['language_code']] += 1

print(f"Number of entries before cleaning: {total_entries_before}")
print(f"Number of entries after cleaning: {total_entries_after}")
print("Entries with variations of [null], '?', or None in the 'senses' column have been removed.")

# Print number of entries for each language code
print("\nNumber of entries for each language code before cleaning:")
for code, count in language_code_counts_before.items():
    print(f"{code}: {count}")

print("\nNumber of entries for each language code after cleaning:")
for code, count in language_code_counts_after.items():
    print(f"{code}: {count}")

