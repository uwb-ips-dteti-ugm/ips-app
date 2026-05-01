package domainserviceshttpuser

import (
	"context"
	"encoding/json"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
	portsdrivenlogging "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/logging"
	portsdrivenrepository "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/repository"
	portsdrivinghttp "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driving/http"
	"github.com/uwb-ips-dteti-ugm/ips-app/backend/pkg/pgxdt"
)

type baseImpl struct {
	tx       pgxdt.Transactor
	log      portsdrivenlogging.Generic
	repoUser portsdrivenrepository.User
}

func NewBaseImpl(
	tx pgxdt.Transactor,
	log portsdrivenlogging.Generic,
	repoUser portsdrivenrepository.User,
) portsdrivinghttp.User {
	return &baseImpl{
		tx:       tx,
		log:      log,
		repoUser: repoUser,
	}
}

func (s *baseImpl) GetUser(ctx context.Context, userId int64) (user domainmodels.User, err error) {
	const tag = path + "/GetUser"

	item, err := s.repoUser.ReadUserById(ctx, userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get user", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.User{}, err
	}

	return *item, nil
}

func (s *baseImpl) GetUsers(ctx context.Context, page int, limit int, cursorId *int64, search *string, roleId *int64) (users []domainmodels.User, total int, err error) {
	const tag = path + "/GetUsers"

	users, total, err = s.repoUser.ReadUsersByPagination(ctx, page, limit, cursorId, search, roleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get users", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return users, total, nil
}

func (s *baseImpl) SetUserInfo(ctx context.Context, userId int64, name *string, bio *string) (user domainmodels.User, err error) {
	const tag = path + "/SetUserInfo"

	err = s.repoUser.UpdateUserInfoById(ctx, userId, name, bio, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set user info", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.User{}, err
	}

	return s.GetUser(ctx, userId)
}

func (s *baseImpl) SetUserPreferences(ctx context.Context, userId int64, preferences []byte) (user domainmodels.User, err error) {
	const tag = path + "/SetUserPreferences"

	err = s.repoUser.UpdateUserPreferencesById(ctx, userId, json.RawMessage(preferences), nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set user preferences", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.User{}, err
	}

	return s.GetUser(ctx, userId)
}

func (s *baseImpl) SetUserRole(ctx context.Context, userId int64, roleId int64) (user domainmodels.User, err error) {
	const tag = path + "/SetUserRole"

	err = s.repoUser.UpdateUserRoleById(ctx, userId, roleId, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set user role", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.User{}, err
	}

	return s.GetUser(ctx, userId)
}

func (s *baseImpl) SetUserState(ctx context.Context, userId int64, state domainmodels.UserState) (user domainmodels.User, err error) {
	const tag = path + "/SetUserState"

	err = s.repoUser.UpdateUserStateById(ctx, userId, state, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set user state", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.User{}, err
	}

	return s.GetUser(ctx, userId)
}

func (s *baseImpl) SetUserStatus(ctx context.Context, userId int64, status domainmodels.UserStatus) (user domainmodels.User, err error) {
	const tag = path + "/SetUserStatus"

	err = s.repoUser.UpdateUserStatusById(ctx, userId, status, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set user status", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.User{}, err
	}

	return s.GetUser(ctx, userId)
}

func (s *baseImpl) RemoveUser(ctx context.Context, userId int64) (message string, err error) {
	const tag = path + "/RemoveUser"

	err = s.repoUser.DeleteUserById(ctx, userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to remove user", domainmodels.LogMeta{"error": err.Error()})
		return "", err
	}

	return "User removed successfully", nil
}
