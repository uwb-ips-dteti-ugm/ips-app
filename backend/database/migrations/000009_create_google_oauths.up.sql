CREATE TABLE IF NOT EXISTS google_oauths (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    sub VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    refresh_token TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by BIGINT,
    updated_at TIMESTAMPTZ,
    updated_by BIGINT,
    version INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_google_oauths_user_id ON google_oauths(user_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_google_oauths_sub_lower ON google_oauths USING gin (LOWER(sub) gin_trgm_ops);

CREATE UNIQUE INDEX IF NOT EXISTS idx_google_oauths_email_lower ON google_oauths USING gin (LOWER(email) gin_trgm_ops);

CREATE UNIQUE INDEX IF NOT EXISTS idx_google_oauths_name_lower ON google_oauths USING gin (LOWER(name) gin_trgm_ops);
