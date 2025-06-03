import json
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm

# Database connection parameters
db_params = {
    'database': 'fr_oot_7117',
    'user': 'owner',
    'password': 'llrrYtkbCPrrRnjHeFmg',
    'host': '172.23.49.21',
    'port': 5065
}

# Connect to your database
conn = psycopg2.connect(**db_params)
cursor = conn.cursor()

# Truncate both lemma_senses and article tables
cursor.execute("TRUNCATE TABLE lemma_senses RESTART IDENTITY CASCADE")
conn.commit()

# Path to your JSON file
lemma_senses_file_path = '../../../data/lemma_senses/json/lemma_senses_prep.json'

# Read the JSON file
with open(lemma_senses_file_path, 'r') as lemma_senses_file:
    lemma_senses_data = json.load(lemma_senses_file)

# Prepare a list of tuples for batch insertion
values_to_insert = []
for item in tqdm(lemma_senses_data, desc="Preparing records"):
    parsed_lemma_id = item['lemma_id'] if item['lemma_id'] is not None else None
    parsed_lemma_form = item['lemma_form'] if item['lemma_form'] is not None else None
    parsed_senses = json.dumps(item['senses']) if item['senses'] is not None else None
    parsed_language_code = item['language_code'] if item['language_code'] is not None else None
    values_to_insert.append((parsed_lemma_id, parsed_lemma_form, parsed_senses, parsed_language_code))

# SQL query for batch insertion
insert_query = """
    INSERT INTO lemma_senses (lemma_id, lemma_form, senses, language_code)
    VALUES %s
"""

# Execute batch insertion
execute_values(cursor, insert_query, values_to_insert)

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()