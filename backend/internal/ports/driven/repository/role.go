package portsdrivenrepository

import (
	"context"
	"encoding/json"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type Role interface {
	CreateRole(ctx context.Context, name string, description string, isDefault bool, createdBy *int64) (id int64, err error)
	ReadRoleById(ctx context.Context, id int64) (role *domainmodels.Role, err error)
	ReadRolesByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (roles []domainmodels.Role, total int, err error)
	ReadRoleDefault(ctx context.Context) (role *domainmodels.Role, err error)
	UpdateRoleById(ctx context.Context, id int64, name *string, description *string, updatedBy *int64) (err error)
	UpdateRoleIsDefaultById(ctx context.Context, id int64, updatedBy *int64) (err error)
	UpdateRolePreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error)
	DeleteRoleById(ctx context.Context, id int64) (err error)
}
