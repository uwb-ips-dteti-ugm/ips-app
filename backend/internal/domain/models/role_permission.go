package domainmodels

import (
	"time"
)

type RolePermission struct {
	RoleId       int64
	PermissionId int64

	CreatedAt time.Time
	CreatedBy *int64
}
