# example usage: python3 prettyJSON.py lemma_senses.json

import json
import sys

with open(sys.argv[1], "r") as f:
    input = json.dumps(json.loads(f.read()), indent=4)

#Saving the pretty pring JSON data to a file
output_file_path = ('./articles')
with open(output_file_path, 'w') as file:
    file.write(input)