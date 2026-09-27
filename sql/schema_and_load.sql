DROP TABLE IF EXISTS ott_titles;

CREATE TABLE ott_titles (
    title_id VARCHAR(32) PRIMARY KEY,
    title VARCHAR(512) NOT NULL,
    type VARCHAR(32) NOT NULL,
    release_year INTEGER NOT NULL,
    genre VARCHAR(128) NOT NULL,
    language VARCHAR(64) NOT NULL,
    country VARCHAR(128) NOT NULL,
    rating VARCHAR(32) NOT NULL,
    runtime NUMERIC(8, 2),
    popularity NUMERIC(6, 2),
    rating_score NUMERIC(4, 2),
    content_segment VARCHAR(128) NOT NULL,
    is_niche SMALLINT NOT NULL DEFAULT 0,
    is_recent_release SMALLINT NOT NULL DEFAULT 0
);

CREATE INDEX idx_ott_type ON ott_titles (type);
CREATE INDEX idx_ott_release_year ON ott_titles (release_year);
CREATE INDEX idx_ott_genre ON ott_titles (genre);
CREATE INDEX idx_ott_language ON ott_titles (language);
CREATE INDEX idx_ott_country ON ott_titles (country);
CREATE INDEX idx_ott_rating ON ott_titles (rating);
CREATE INDEX idx_ott_content_segment ON ott_titles (content_segment);
