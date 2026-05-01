package portsdrivenrepository

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type GoogleOAuth interface {
	CreateGoogleOAuth(ctx context.Context, userId int64, sub string, email string, name string, refreshToken string, createdBy *int64) (id int64, err error)
	ReadGoogleOAuthById(ctx context.Context, id int64) (googleOAuth *domainmodels.GoogleOAuth, err error)
	ReadGoogleOAuthByUserId(ctx context.Context, userId int64) (googleOAuth *domainmodels.GoogleOAuth, err error)
	ReadGoogleOAuthBySub(ctx context.Context, sub string) (googleOAuth *domainmodels.GoogleOAuth, err error)
	ReadGoogleOAuthByEmail(ctx context.Context, email string) (googleOAuth *domainmodels.GoogleOAuth, err error)
	UpdateGoogleOAuthBySub(ctx context.Context, sub string, email *string, name *string, refreshToken *string, updatedBy *int64) (err error)
	DeleteGoogleOAuthByUserId(ctx context.Context, userId int64) (err error)
}
