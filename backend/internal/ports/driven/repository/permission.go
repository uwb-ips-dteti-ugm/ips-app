package portsdrivenrepository

import (
	"context"
	"encoding/json"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type Permission interface {
	CreatePermission(ctx context.Context, name string, description string, createdBy *int64) (id int64, err error)
	ReadPermissionById(ctx context.Context, id int64) (permission *domainmodels.Permission, err error)
	ReadPermissionsByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (permissions []domainmodels.Permission, total int, err error)
	UpdatePermissionById(ctx context.Context, id int64, name *string, description *string, updatedBy *int64) (err error)
	UpdatePermissionPreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error)
	DeletePermissionById(ctx context.Context, id int64) (err error)
}
