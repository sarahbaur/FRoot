import os
import re
import Levenshtein
import psycopg2
import torch
import numpy as np
import traceback
import pickle
import uuid

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import CamembertTokenizer, CamembertModel
from scipy.spatial.distance import cosine
from tqdm import tqdm

# Initialize Flask app and CORS
app = Flask(__name__, static_folder='frontend')
CORS(app)

# Configure the app with environment variables
app.config['DB_HOST'] = os.environ.get('DB_HOST')
app.config['DB_PORT'] = os.environ.get('DB_PORT')
app.config['DB_NAME'] = os.environ.get('DB_NAME')
app.config['DB_USER'] = os.environ.get('DB_USER')
app.config['DB_PASSWORD'] = os.environ.get('DB_PASSWORD')

# Establish database connection
connection = psycopg2.connect(
    host=app.config['DB_HOST'],
    port=app.config['DB_PORT'],
    dbname=app.config['DB_NAME'],
    user=app.config['DB_USER'],
    password=app.config['DB_PASSWORD']
)

##########################################################################################
# Function to normalize lemma names by removing numerical suffixes
def normalize_lemma_name(lemma_name):
    return re.sub(r'\d+$', '', lemma_name).strip()

# Function to process and filter lemmas
def process_lemmas(lemma_scores):
    seen = set()
    processed_scores = []
    for lemma, score in lemma_scores:
        normalized_lemma = normalize_lemma_name(lemma)
        if normalized_lemma not in seen:
            seen.add(normalized_lemma)
            processed_scores.append((normalized_lemma, score))
    return processed_scores

# Function to load words and their senses from the database
def load_data_from_database():
    with connection.cursor() as cursor:
        cursor.execute("SELECT lemma_id, lemma_form, senses, embedding FROM lemma_senses")
        rows = cursor.fetchall()
        elements_list = []
        for row in rows:
            lemma_id, lemma_form, senses, embedding = row
            if senses is not None and embedding is not None and lemma_id is not None and lemma_form is not None:
                try:
                    embedding = pickle.loads(embedding)
                    # Normalize the lemma_form by removing numerical suffixes
                    normalized_lemma_form = normalize_lemma_name(lemma_form)
                    elements_list.append((lemma_id, normalized_lemma_form, senses, embedding))
                except (pickle.UnpicklingError, TypeError, EOFError) as e:
                    print(f"Error deserializing embedding for {lemma_form}: {e}")
    return elements_list

# Load the CamemBERT model
model_name = "camembert-base"
tokenizer = CamembertTokenizer.from_pretrained(model_name)
model = CamembertModel.from_pretrained(model_name)

def get_embedding(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).squeeze().detach().numpy()

def calculate_bert_similarity_scores(input_text, elements_list):
    input_embedding = get_embedding(input_text)
    scores = {}
    for lemma_id, lemma_form, sense, precalc_emb in elements_list:
        similarity = 1 - cosine(input_embedding, np.array(precalc_emb))
        scores[sense] = similarity
    return scores

def calculate_levenshtein_scores(input_word, elements_list):
    scores = {}
    for lemma_id, lemma_form, sense, precalc_emb in elements_list:
        if lemma_form is not None:
            distance = Levenshtein.distance(input_word, lemma_form)
            max_length = max(len(input_word), len(lemma_form))
            similarity = 1 - (distance / max_length)
            scores[lemma_form] = similarity  # Use lemma_form or another unique identifier as the key
    return scores

def get_top_matches(similarity_scores, top_n=5):
    sorted_words = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    # Adjust the return to include lemma names and scores
    return [(lemma, score) for lemma, score in sorted_words[:top_n]]

# Function to retrieve article information by lemma ID
def get_article_info_by_id(id):
    try:
        # The SQL query now joins the lemma_senses table as well to get the lemma_form and senses.
        query = """
        SELECT ls.lemma_form, ls.senses, a.etymology
        FROM lemma_senses ls
        LEFT JOIN article_lemma al ON ls.lemma_id = al.lemma_id
        LEFT JOIN article a ON al.article_id = a.article_id
        WHERE ls.lemma_id = %s
        """
        lemma_id_str = str(id)  # Convert UUID to a string if necessary
        with connection.cursor() as cursor:
            cursor.execute(query, (lemma_id_str,))
            result = cursor.fetchone()
            if result:
                lemma_form, senses, etymology = result
                return {
                    'lemma_form': lemma_form,
                    'senses': senses,
                    'etymology': etymology
                }
            else:
                return None
    except Exception as e:
        traceback.print_exc()
        return None



##########################################################################################

@app.route('/process-query', methods=['POST'])
def process_query():
    try:
        data = request.json
        user_lemma = data.get('lemma', '')
        user_meaning = data.get('meaning', '')

        elements_list = load_data_from_database()

        # Processing Lemmas
        lemma_results = []
        if user_lemma:
            lemma_scores_levenshtein = calculate_levenshtein_scores(user_lemma, elements_list)
            lemma_results_raw = get_top_matches(lemma_scores_levenshtein)

            for lemma_name, score in lemma_results_raw:
                for lemma_id, form, sense, emb in elements_list:
                    if form == lemma_name:
                        lemma_results.append({'id': lemma_id, 'lemma': lemma_name, 'score': score})
                        break

        # Processing Meanings
        meaning_results = []
        seen_senses = set()  # Use this set to track unique senses
        if user_meaning:
            meaning_scores_bert = calculate_bert_similarity_scores(user_meaning, elements_list)
            meaning_results_raw = get_top_matches(meaning_scores_bert)
            for sense, score in meaning_results_raw:
                if sense not in seen_senses:
                    seen_senses.add(sense)
                    for lemma_id, form, sense_list, emb in elements_list:
                        if sense in sense_list:
                            meaning_results.append({'id': lemma_id, 'sense': sense, 'score': score})
                            break  # Break after adding the first occurrence

        response = jsonify({
            'lemma_results': lemma_results,
            'meaning_results': meaning_results
        })
        print(response.get_data(as_text=True))  # This will print the JSON response
        return response


    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/details/<uuid:id>', methods=['GET'])
def details(id):
    print(f"Received ID: {id}")
    article_info = get_article_info_by_id(id)

    if article_info:
        # Extract the lemma_form, senses, and etymology from the article_info dictionary
        lemma_form_raw = article_info.get('lemma_form')
        lemma_form = normalize_lemma_name(lemma_form_raw)
        senses = article_info.get('senses')
        etymology = article_info.get('etymology')

        # Replace 'Null', 'Undefined', or None with the default message for each field
        default_msg = 'No information stored in the Database'
        lemma_form = default_msg if lemma_form in [None, 'Null', 'Undefined'] else lemma_form
        senses = default_msg if senses in [None, 'Null', 'Undefined'] else senses
        etymology = default_msg if etymology in [None, 'Null', 'Undefined'] else etymology

        return jsonify({
            'lemma': lemma_form,
            'meaning': senses,
            'etymology': etymology
        })
    else:
        return jsonify({'error': 'Article not found for the given ID.'}), 404

# Serve the frontend static files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'base.html')

@app.route('/home.html')
def home():
    return app.send_static_file('base.html')

@app.route('/about.html')
def about():
    return app.send_static_file('about.html')

# Main entry point for the Flask application
if __name__ == '__main__':
    # Use the environment variable PORT if available, otherwise default to 63342
    port = int(os.environ.get('PORT', 5000))
    # Use the environment variable HOST if available, otherwise default to 127.0.0.1
    host = os.environ.get('HOST', '127.0.0.1')
    # Run the Flask app with debug mode turned off for production
    app.run(host=host, port=port, debug=False)