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

# Truncate the article_lemma table
cursor.execute("TRUNCATE TABLE article_lemma RESTART IDENTITY CASCADE")

# File path to your combined JSON file
combined_json_path = '../../../data/articles/articles_combined.json'

# Prepare list for batch insertion
article_lemma_values_to_insert = []

# Process the combined JSON file
with open(combined_json_path, 'r') as file:
    try:
        articles_data = json.load(file)
    except json.JSONDecodeError as e:
        print(f"JSON decode error in file {combined_json_path}: {e}")
    else:
        for article_id, article_info in tqdm(articles_data.items(), desc=f"Processing {combined_json_path}"):
            try:
                # Iterating over article_lemma entries
                for lemma_entry in article_info['article_lemma']:
                    lemma_id = lemma_entry['lemma_id']
                    article_lemma_values_to_insert.append((article_id, lemma_id))
            except KeyError as e:
                print(f"Key error processing article {article_id}: {e}")
            except TypeError as e:
                print(f"Type error processing article {article_id}: {e}")

# SQL query for batch insertion into the article_lemma table
insert_article_lemma_query = """
    INSERT INTO article_lemma (article_id, lemma_id)
    VALUES %s
    ON CONFLICT (article_id, lemma_id) DO NOTHING
"""

# Execute batch insertion for article_lemmas with exception handling
try:
    execute_values(cursor, insert_article_lemma_query, article_lemma_values_to_insert)
except Exception as e:
    print(f"Error inserting into article_lemma table: {e}")

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()