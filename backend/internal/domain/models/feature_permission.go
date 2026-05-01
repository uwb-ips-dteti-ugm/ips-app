package domainmodels

import (
	"time"
)

type FeaturePermission struct {
	FeatureId    int64
	PermissionId int64

	CreatedAt time.Time
	CreatedBy *int64
}
