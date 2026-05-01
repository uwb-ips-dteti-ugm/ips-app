CREATE TABLE IF NOT EXISTS auths (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    password_hash TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by BIGINT,
    updated_at TIMESTAMPTZ,
    updated_by BIGINT,
    version INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_auths_user_id ON auths(user_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_auths_username_lower ON auths USING gin (LOWER(username) gin_trgm_ops);

CREATE UNIQUE INDEX IF NOT EXISTS idx_auths_email_lower ON auths USING gin (LOWER(COALESCE(email, md5(random()::text))) gin_trgm_ops);

CREATE UNIQUE INDEX IF NOT EXISTS idx_auths_phone_lower ON auths USING gin (LOWER(COALESCE(phone, md5(random()::text))) gin_trgm_ops);

