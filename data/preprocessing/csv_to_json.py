import pandas as pd

# Load the CSV file
file_path = '../lemma_senses/csv/lemma_senses_prep.csv'
data = pd.read_csv(file_path, sep='\t')

#Convert the DataFrame to JSON format
json_data = data.to_json(orient='records')

#Saving the JSON data to a file
output_file_path = '../lemma_senses/json/lemma_senses.json'
with open(output_file_path, 'w') as file:
    file.write(json_data)
