package portsdrivinghttp

import (
	"context"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type User interface {
	GetUser(ctx context.Context, userId int64) (user domainmodels.User, err error)
	GetUsers(ctx context.Context, page int, limit int, cursorId *int64, search *string, roleId *int64) (users []domainmodels.User, total int, err error)
	SetUserInfo(ctx context.Context, userId int64, name *string, bio *string) (user domainmodels.User, err error)
	SetUserPreferences(ctx context.Context, userId int64, preferences []byte) (user domainmodels.User, err error)
	SetUserRole(ctx context.Context, userId int64, roleId int64) (user domainmodels.User, err error)
	SetUserState(ctx context.Context, userId int64, state domainmodels.UserState) (user domainmodels.User, err error)
	SetUserStatus(ctx context.Context, userId int64, status domainmodels.UserStatus) (user domainmodels.User, err error)
	RemoveUser(ctx context.Context, userId int64) (message string, err error)
}
