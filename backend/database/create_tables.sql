-- NO ONE MESS WITH THIS FILE OR IMMA STRANGLE YOU

-- Drop existing tables if they exist and create new tables with necessary constraints
-- DROP TABLE IF EXISTS article_lemma;
-- DROP TABLE IF EXISTS article;
-- DROP TABLE IF EXISTS lemma_senses;

CREATE TABLE IF NOT EXISTS lemma_senses (
    lemma_id VARCHAR(36) PRIMARY KEY,
    lemma_form VARCHAR(255),
    senses TEXT,
    language_code VARCHAR(10),
    embedding BYTEA  -- Add this line for the embeddings
);


CREATE TABLE IF NOT EXISTS article (
    article_id VARCHAR(36) PRIMARY KEY,
    main_lemma_id VARCHAR(36),
    etymology TEXT,
    CONSTRAINT fk_article_main_lemma_id FOREIGN KEY (main_lemma_id) REFERENCES lemma_senses(lemma_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS article_lemma (
    article_id VARCHAR(36),
    lemma_id VARCHAR(36),
    PRIMARY KEY (article_id, lemma_id),
    CONSTRAINT fk_article_lemma_article_id FOREIGN KEY (article_id) REFERENCES article(article_id) ON DELETE CASCADE,
    CONSTRAINT fk_article_lemma_lemma_id FOREIGN KEY (lemma_id) REFERENCES lemma_senses(lemma_id) ON DELETE CASCADE
);

-- Grant Permissions to user 'webapp_user' on the table 'lemma_senses'
GRANT SELECT, INSERT, UPDATE, DELETE ON lemma_senses, article_lemma, article TO webapp_user;
