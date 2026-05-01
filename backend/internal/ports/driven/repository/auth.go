package portsdrivenrepository

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type Auth interface {
	CreateAuth(ctx context.Context, userId int64, username string, passwordHash string, email *string, phone *string, createdBy *int64) (id int64, err error)
	ReadAuthsByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (auths []domainmodels.Auth, total int, err error)
	ReadAuthById(ctx context.Context, id int64) (auth *domainmodels.Auth, err error)
	ReadAuthByUserId(ctx context.Context, userId int64) (auth *domainmodels.Auth, err error)
	ReadAuthBySignInIdentifier(ctx context.Context, signInIdentifier string) (auth *domainmodels.Auth, err error)
	UpdateAuthInfoById(ctx context.Context, id int64, username *string, email *string, phone *string, updatedBy *int64) (err error)
	UpdateAuthPasswordById(ctx context.Context, id int64, passwordHash string, updatedBy *int64) (err error)
	DeleteAuthByUserId(ctx context.Context, userId int64) (err error)
}
