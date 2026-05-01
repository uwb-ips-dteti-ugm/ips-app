package portsdrivenrepository

import (
	"context"
	"encoding/json"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
)

type User interface {
	CreateUser(ctx context.Context, roleId int64, name string, createdBy *int64) (id int64, err error)
	ReadUserById(ctx context.Context, id int64) (user *domainmodels.User, err error)
	ReadUsersByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string, roleId *int64) (users []domainmodels.User, total int, err error)
	UpdateUserInfoById(ctx context.Context, id int64, name *string, bio *string, updatedBy *int64) (err error)
	UpdateUserStateById(ctx context.Context, id int64, state domainmodels.UserState, updatedBy *int64) (err error)
	UpdateUserStatusById(ctx context.Context, id int64, status domainmodels.UserStatus, updatedBy *int64) (err error)
	UpdateUserRoleById(ctx context.Context, id int64, roleId int64, updatedBy *int64) (err error)
	UpdateUserPreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error)
	UpdateUserLastSignedInAtById(ctx context.Context, id int64, updatedBy *int64) (err error)
	UpdateUserLastRefreshedAtById(ctx context.Context, id int64, updatedBy *int64) (err error)
	UpdateUserLastActivityAtById(ctx context.Context, id int64, updatedBy *int64) (err error)
	DeleteUserById(ctx context.Context, id int64) (err error)
}
