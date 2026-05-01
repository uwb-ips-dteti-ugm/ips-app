package portsdrivinghttp

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type Role interface {
	// Roles
	AddRole(ctx context.Context, name string, description string) (role domainmodels.Role, err error)
	GetRole(ctx context.Context, roleId int64) (role domainmodels.Role, err error)
	GetRoles(ctx context.Context, page int, limit int, cursorId *int64, search *string) (roles []domainmodels.Role, total int, err error)
	SetRole(ctx context.Context, roleId int64, name *string, description *string) (role domainmodels.Role, err error)
	SetRolePreferences(ctx context.Context, roleId int64, preferences []byte) (role domainmodels.Role, err error)
	RemoveRole(ctx context.Context, roleId int64) (message string, err error)

	// Permissions
	AddPermission(ctx context.Context, name string, description string) (permission domainmodels.Permission, err error)
	GetPermission(ctx context.Context, permissionId int64) (permission domainmodels.Permission, err error)
	GetPermissions(ctx context.Context, page int, limit int, cursorId *int64, search *string) (permissions []domainmodels.Permission, total int, err error)
	SetPermission(ctx context.Context, permissionId int64, name *string, description *string) (permission domainmodels.Permission, err error)
	SetPermissionPreferences(ctx context.Context, permissionId int64, preferences []byte) (permission domainmodels.Permission, err error)
	RemovePermission(ctx context.Context, permissionId int64) (message string, err error)

	// Role-Permission bindings
	AddPermissionsToRole(ctx context.Context, roleId int64, permissionIds []int64) (role domainmodels.Role, err error)
	RemovePermissionsFromRole(ctx context.Context, roleId int64, permissionIds []int64) (role domainmodels.Role, err error)
	GetRolePermissions(ctx context.Context, roleId int64) (permissions []domainmodels.Permission, err error)
}
