import csv
from collections import defaultdict

# Input CSV file
input_file = 'lemma_senses.csv'

# Initialize data structures
language_codes = defaultdict(int)
lemmas_with_null = defaultdict(int)
lemmas_with_senses = defaultdict(int)
total_lemmas_per_language = defaultdict(int)

# Open the input CSV file
with open(input_file, mode='r', newline='') as csv_file:
    reader = csv.DictReader(csv_file, delimiter='\t')
    
    # Iterate through rows in the input CSV file
    for row in reader:
        language_code = row['language_code']
        senses = row['senses']
        
        # Count the number of unique language codes
        language_codes[language_code] += 1
        
        # Check if senses contain both "null" and another meaning
        if senses is not None and ('null' in senses and ',' in senses):
            lemmas_with_senses[language_code] += 1
        else:
            lemmas_with_null[language_code] += 1
        total_lemmas_per_language[language_code] += 1

# Print the requested information in an organized format
print("Summary of Lemmas in CSV:")
print("{:<10} {:<20} {:<20} {:<20}".format("Language", "Total Lemmas", "Lemmas with 'null'", "Lemmas with actual senses"))
print("="*80)

for code in sorted(language_codes.keys()):
    total_lemmas = total_lemmas_per_language[code]
    null_count = lemmas_with_null[code]
    senses_count = lemmas_with_senses[code]
    print(f"{code:<10} {total_lemmas:<20} {null_count:<20} {senses_count:<20}")
