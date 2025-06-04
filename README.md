# FRoot – French Lemma & Ethymology Search

FRoot is a compact web app that lets you look up a **French lemma** together with the **meaning you have in mind** and returns the closest matches from a linguistically curated database. It combines classic Levenshtein edit‑distance lookup (for the lemma) with CamemBERT semantic similarity (for the meaning) so you can find the right word even when your recollection is fuzzy.

---

## Why we built it

This project was created for the University of Zurich course *Language Technologies and Web Applications* (HS 2023). Our goal was to make a slice of the **LEGaMe** French etymology dataset (https://gallrom.linguistik.uzh.ch/pdfs/further-information.pdf#/legame) searchable in a user‑friendly way and to showcase how dual‑input search plus lightweight NLP can turn a highly structured academic corpus into an interactive learning tool.

> **Data disclaimer**
> Everything in **`backend/database/data/`** is a *toy sample* with just a few rows. The full LEGaMe dataset is not redistributable here. The data was lent to us **for educational purposes only** by the *LEGaMe* project.
0
---

## Demo 
Responsive landing screen design for the interface:
![Quick demo](assets/froot_vid_1.mov)

User interface design and search query output:
![Quick demo](assets/froot_vid_2.mov)


## Quick start

```bash
# Clone & enter
$ git clone <your-fork-url> froot && cd froot

# Python env
$ python -m venv .venv && source .venv/bin/activate
$ pip install -r requirements.txt

# Launch the backend (Flask)
$ export FLASK_APP=flask_app.py
$ flask run   # ➜ http://127.0.0.1:5000
```

---

## Repo layout

```
backend/database/
    db_scripts/            # SQL DDL & population helpers
    data/                  # sample CSV/JSON slices (see note above)
frontend/                  # JS + HTML/CSS assets
flask_app.py               # API endpoints and routing
requirements.txt           # Python deps
```

---

## Credits

* **Sarah Baur**
* **Mara Baccaro**

---

## License

Released under the **MIT License** – see `LICENSE`.
