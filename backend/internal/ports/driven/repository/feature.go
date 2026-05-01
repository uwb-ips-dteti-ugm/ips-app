package portsdrivenrepository

import (
	"context"
	"encoding/json"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type Feature interface {
	CreateFeature(ctx context.Context, name string, description string, createdBy *int64) (id int64, err error)
	ReadFeatureById(ctx context.Context, id int64) (feature *domainmodels.Feature, err error)
	ReadFeaturesByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (features []domainmodels.Feature, total int, err error)
	UpdateFeatureById(ctx context.Context, id int64, name *string, description *string, updatedBy *int64) (err error)
	UpdateFeaturePreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error)
	DeleteFeatureById(ctx context.Context, id int64) (err error)
}
