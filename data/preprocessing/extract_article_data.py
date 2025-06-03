import json
import os


def extract_data_for_sql_tables(json_data):
    """
    Extracts data for SQL tables 'article' and 'article_lemma' from the given JSON data.
    """
    article_id = json_data["id"]
    main_lemma_id = json_data["mainLemma"]["id"]
    etymology = json_data["mainLemma"]["etymologies"][0]["description"] if json_data["mainLemma"][
        "etymologies"] else None

    article_data = {
        "main_lemma_id": main_lemma_id,
        "etymology": etymology
    }

    # Extracting all lemma IDs from the 'lemmas' branch
    lemmas = [{"lemma_id": lemma_id} for lemma_id in json_data["lemmas"].keys()]

    return {article_id: {"article": article_data, "article_lemma": lemmas}}


def process_directory(directory_path):
    combined_data = {}
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.json'):
            file_path = os.path.join(directory_path, file_name)
            with open(file_path, 'r') as file:
                json_data = json.load(file)
                extracted_data = extract_data_for_sql_tables(json_data)
                combined_data.update(extracted_data)
    return combined_data


# Directory containing JSON files
directory_path = '../articles/articles_raw'  # Update with the actual directory path

# Process the directory and get combined data
combined_data = process_directory(directory_path)

# Write the combined data to a file in JSON format
output_file_path = '../articles/articles_combined.json'
with open(output_file_path, 'w') as file:
    json.dump(combined_data, file, indent=4)

# Output the file path of the combined data
print(output_file_path)