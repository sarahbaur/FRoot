from transformers import CamembertTokenizer, CamembertModel
import torch
import psycopg2
import pickle
from tqdm import tqdm
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Establish database connection
connection = psycopg2.connect(
    host=os.environ.get('DB_HOST'),
    port=os.environ.get('DB_PORT'),
    dbname=os.environ.get('DB_NAME'),
    user=os.environ.get('DB_USER'),
    password=os.environ.get('DB_PASSWORD')
)
cursor = connection.cursor()

# Load the CamemBERT model
model_name = "camembert-base"
tokenizer = CamembertTokenizer.from_pretrained(model_name)
model = CamembertModel.from_pretrained(model_name)

def get_embedding(text):
    # Ensure the text is a string
    if not isinstance(text, str):
        raise ValueError(f"Expected a string, but got {type(text)}")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze()


def process_batch(texts):
    embeddings = {}
    for lemma_id, text in texts:
        # Skip the entry if text is None
        if text is None:
            print(f"Skipping lemma_id {lemma_id} due to None value.")
            continue

        try:
            embedding = get_embedding(text)
            embeddings[lemma_id] = embedding.detach().cpu().numpy()
        except Exception as e:
            print(f"Error processing lemma_id {lemma_id}. Error: {e}")
            # Optionally, skip this entry or handle the error differently
    return embeddings



# Define batch size
batch_size = 100  # Adjust based on your memory constraints

# Fetch text data from your database
cursor.execute("SELECT lemma_id, senses FROM lemma_senses")
texts = cursor.fetchall()

# Process in batches with tqdm progress bar
for i in tqdm(range(0, len(texts), batch_size), desc="Processing batches"):
    batch_texts = texts[i:i+batch_size]
    batch_embeddings = process_batch(batch_texts)

    # Update database with embeddings in the same batch
    for lemma_id, embedding in batch_embeddings.items():
        serialized_embedding = pickle.dumps(embedding)
        update_query = "UPDATE lemma_senses SET embedding = %s WHERE lemma_id = %s"
        cursor.execute(update_query, (serialized_embedding, lemma_id))

    connection.commit()

# Close the cursor and connection
cursor.close()
connection.close()