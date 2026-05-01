package portsdrivenlogging

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type Generic interface {
	Error(ctx context.Context, tag string, message string, meta domainmodels.LogMeta)
	Warn(ctx context.Context, tag string, message string, meta domainmodels.LogMeta)
	Info(ctx context.Context, tag string, message string, meta domainmodels.LogMeta)
	Debug(ctx context.Context, tag string, message string, meta domainmodels.LogMeta)
}
