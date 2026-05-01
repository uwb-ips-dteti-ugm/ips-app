CREATE TABLE IF NOT EXISTS feature_permission (
    feature_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by BIGINT,

    PRIMARY KEY (feature_id, permission_id),

    FOREIGN KEY (feature_id)
        REFERENCES features(id)
        ON DELETE CASCADE,

    FOREIGN KEY (permission_id)
        REFERENCES permissions(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_feature_permission_feature_id ON feature_permission(feature_id);

CREATE INDEX IF NOT EXISTS idx_feature_permission_permission_id ON feature_permission(permission_id);
