package tracer

import (
	"context"

	"github.com/google/uuid"
)

func Inject(ctx context.Context, issuer string) context.Context {
	return context.WithValue(ctx, "trace_id", issuer+"-"+uuid.NewString())
}

func Extract(ctx context.Context) string {
	traceID := ctx.Value("trace_id")
	if traceIDStr, ok := traceID.(string); ok {
		return traceIDStr
	}
	return "None"
}
