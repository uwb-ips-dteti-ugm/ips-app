package portsdrivenrepository

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type RolePermission interface {
	CreateRolePermission(ctx context.Context, roleId int64, permissionId int64, createdBy *int64) (id int64, err error)
	ReadPermissionsByRoleId(ctx context.Context, roleId int64) (permissions []domainmodels.Permission, err error)
	ReadRolesByPermissionId(ctx context.Context, permissionId int64) (roles []domainmodels.Role, err error)
	DeleteRolePermissionByRoleIdAndPermissionId(ctx context.Context, roleId int64, permissionId int64) (err error)
	DeleteRolePermissionsByRoleId(ctx context.Context, roleId int64) (err error)
	DeleteRolePermissionsByPermissionId(ctx context.Context, permissionId int64) (err error)
}
