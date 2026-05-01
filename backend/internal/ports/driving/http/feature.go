package portsdrivinghttp

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type Feature interface {
	// Features
	AddFeature(ctx context.Context, name string, description string) (feature domainmodels.Feature, err error)
	GetFeature(ctx context.Context, featureId int64) (feature domainmodels.Feature, err error)
	GetFeatures(ctx context.Context, page int, limit int, cursorId *int64, search *string) (features []domainmodels.Feature, total int, err error)
	SetFeature(ctx context.Context, featureId int64, name *string, description *string) (feature domainmodels.Feature, err error)
	SetFeaturePreferences(ctx context.Context, featureId int64, preferences []byte) (feature domainmodels.Feature, err error)
	RemoveFeature(ctx context.Context, featureId int64) (message string, err error)

	// Feature-Permission bindings
	AddPermissionsToFeature(ctx context.Context, featureId int64, permissionIds []int64) (feature domainmodels.Feature, err error)
	RemovePermissionsFromFeature(ctx context.Context, featureId int64, permissionIds []int64) (feature domainmodels.Feature, err error)
	GetFeaturePermissions(ctx context.Context, featureId int64) (permissions []domainmodels.Permission, err error)

	// Feature access
	GetAccessibleFeatures(ctx context.Context, userId int64) (features []domainmodels.Feature, err error)
	CanAccessFeature(ctx context.Context, userId int64, featureId int64) (canAccess bool, err error)
}
