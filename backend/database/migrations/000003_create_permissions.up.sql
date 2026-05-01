CREATE TABLE IF NOT EXISTS permissions (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000) NOT NULL DEFAULT '',
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by BIGINT,
    updated_at TIMESTAMPTZ,
    updated_by BIGINT,
    version INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT uq_permissions_name_lower UNIQUE (LOWER(name))
);

CREATE INDEX IF NOT EXISTS idx_permissions_name_lower ON permissions USING gin (LOWER(name) gin_trgm_ops);
