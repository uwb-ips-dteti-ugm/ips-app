CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    role_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    bio VARCHAR(2048) NOT NULL DEFAULT '',
    state VARCHAR(32) NOT NULL DEFAULT 'offline',
    status VARCHAR(32) NOT NULL DEFAULT 'active',
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_signed_in_at TIMESTAMPTZ,
    last_refreshed_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by BIGINT,
    updated_at TIMESTAMPTZ,
    updated_by BIGINT,
    version INTEGER NOT NULL DEFAULT 0,

    FOREIGN KEY (role_id)
        REFERENCES roles(id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_users_role_id ON users(role_id);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_name_lower ON users USING gin (LOWER(name) gin_trgm_ops);
