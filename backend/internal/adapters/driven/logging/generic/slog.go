package adaptersdrivelogginggcontext

import (
	"context"
	"log/slog"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
	portsdrivenlogging "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/logging"
)

type slogImpl struct {
	logger *slog.Logger
}

func NewSlogImpl(logger *slog.Logger) portsdrivenlogging.Generic {
	return &slogImpl{
		logger: logger,
	}
}

func (s *slogImpl) Error(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.ErrorContext(
		ctx, message,
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}

func (s *slogImpl) Warn(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.WarnContext(
		ctx, message,
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}

func (s *slogImpl) Info(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.InfoContext(
		ctx, message,
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}

func (s *slogImpl) Debug(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.DebugContext(
		ctx, message,
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}
