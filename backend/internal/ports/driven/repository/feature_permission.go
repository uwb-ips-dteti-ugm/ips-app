package portsdrivenrepository

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type FeaturePermission interface {
	CreateFeaturePermission(ctx context.Context, featureId int64, permissionId int64, createdBy *int64) (id int64, err error)
	ReadPermissionsByFeatureId(ctx context.Context, featureId int64) (permissions []domainmodels.Permission, err error)
	ReadFeaturesByPermissionId(ctx context.Context, permissionId int64) (features []domainmodels.Feature, err error)
	DeleteFeaturePermissionByFeatureIdAndPermissionId(ctx context.Context, featureId int64, permissionId int64) (err error)
	DeleteFeaturePermissionsByFeatureId(ctx context.Context, featureId int64) (err error)
	DeleteFeaturePermissionsByPermissionId(ctx context.Context, permissionId int64) (err error)
}
