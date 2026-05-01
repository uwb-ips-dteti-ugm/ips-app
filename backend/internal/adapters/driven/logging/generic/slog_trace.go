package adaptersdrivelogginggcontext

import (
	"context"
	"log/slog"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
	portsdrivenlogging "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/logging"
	"github.com/uwb-ips-dteti-ugm/ips-app/backend/pkg/tracer"
)

type slogTraceImpl struct {
	logger *slog.Logger
}

func NewSlogTraceImpl(logger *slog.Logger) portsdrivenlogging.Generic {
	return &slogTraceImpl{
		logger: logger,
	}
}

func (s *slogTraceImpl) Error(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.ErrorContext(
		ctx, message,
		slog.String("trace_id", tracer.Extract(ctx)),
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}

func (s *slogTraceImpl) Warn(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.WarnContext(
		ctx, message,
		slog.String("trace_id", tracer.Extract(ctx)),
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}

func (s *slogTraceImpl) Info(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.InfoContext(
		ctx, message,
		slog.String("trace_id", tracer.Extract(ctx)),
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}

func (s *slogTraceImpl) Debug(ctx context.Context, tag string, message string, meta domainmodels.LogMeta) {
	s.logger.DebugContext(
		ctx, message,
		slog.String("trace_id", tracer.Extract(ctx)),
		slog.String("tag", tag),
		slog.Any("meta", meta),
	)
}
