CREATE TABLE IF NOT EXISTS roles (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000) NOT NULL DEFAULT '',
    preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by BIGINT,
    updated_at TIMESTAMPTZ,
    updated_by BIGINT,
    version INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT uq_roles_name_lower UNIQUE (LOWER(name))
);

CREATE INDEX IF NOT EXISTS idx_roles_name_lower ON roles USING gin (LOWER(name) gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_roles_is_default ON roles(is_default) WHERE is_default = TRUE;
