package adaptersdrivenrepositoryuser

import (
	"context"
	"database/sql"
	"encoding/json"
	"errors"

	"github.com/Masterminds/squirrel"
	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
	portsdrivenlogging "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/logging"
	portsdrivenrepository "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/repository"
	"github.com/uwb-ips-dteti-ugm/ips-app/backend/pkg/pgxdt"
)

type postgresImpl struct {
	dt          pgxdt.Pgxdt
	sqrQuestion squirrel.StatementBuilderType
	log         portsdrivenlogging.Generic
}

func NewPostgresImpl(
	dt pgxdt.Pgxdt,
	sqrQuestion squirrel.StatementBuilderType,
	log portsdrivenlogging.Generic,
) portsdrivenrepository.User {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreateUser(ctx context.Context, roleId int64, name string, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreateUser"

	query, args, err := s.queryCreateUser(roleId, name, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create user", domainmodels.LogMeta{"error": err.Error()})
		return 0, err
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadUserById(ctx context.Context, id int64) (item *domainmodels.User, err error) {
	const tag = path + "/ReadUserById"

	query, args, err := s.queryReadUserById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var usr domainmodels.User
	err = row.Scan(&usr.Id, &usr.RoleId, &usr.Name, &usr.Bio, &usr.State, &usr.Status, &usr.Preferences, &usr.LastSignedInAt, &usr.LastRefreshedAt, &usr.LastActivityAt, &usr.CreatedAt, &usr.CreatedBy, &usr.UpdatedAt, &usr.UpdatedBy, &usr.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read user", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &usr, nil
}

func (s *postgresImpl) ReadUsersByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string, roleId *int64) (items []domainmodels.User, total int, err error) {
	const tag = path + "/ReadUsersByPagination"

	countQuery, countArgs, query, args, err := s.queryReadUsersByPagination(page, limit, cursorId, search, roleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, domainmodels.ErrQueryBuilder
	}

	countRow := s.dt.QueryRow(ctx, countQuery, countArgs...)
	if err := countRow.Scan(&total); err != nil {
		s.log.Error(ctx, tag, "Failed to count users", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	if total == 0 {
		return []domainmodels.User{}, 0, nil
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read users", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}
	defer rows.Close()

	items = make([]domainmodels.User, 0, total)
	for rows.Next() {
		var item domainmodels.User
		if err := rows.Scan(&item.Id, &item.RoleId, &item.Name, &item.Bio, &item.State, &item.Status, &item.Preferences, &item.LastSignedInAt, &item.LastRefreshedAt, &item.LastActivityAt, &item.CreatedAt, &item.CreatedBy, &item.UpdatedAt, &item.UpdatedBy, &item.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan user", domainmodels.LogMeta{"error": err.Error()})
			return nil, 0, err
		}
		items = append(items, item)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate users", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return items, total, nil
}

func (s *postgresImpl) UpdateUserInfoById(ctx context.Context, id int64, name *string, bio *string, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserInfoById"

	query, args, err := s.queryUpdateUserInfoById(id, name, bio, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateUserStateById(ctx context.Context, id int64, state domainmodels.UserState, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserStateById"

	query, args, err := s.queryUpdateUserStateById(id, string(state), updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user state", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateUserStatusById(ctx context.Context, id int64, status domainmodels.UserStatus, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserStatusById"

	query, args, err := s.queryUpdateUserStatusById(id, string(status), updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user status", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateUserRoleById(ctx context.Context, id int64, roleId int64, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserRoleById"

	query, args, err := s.queryUpdateUserRoleById(id, roleId, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user role", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateUserPreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserPreferencesById"

	prefsStr := string(preferences)
	query, args, err := s.queryUpdateUserPreferencesById(id, &prefsStr, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user preferences", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateUserLastSignedInAtById(ctx context.Context, id int64, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserLastSignedInAtById"

	query, args, err := s.queryUpdateUserLastSignedInAtById(id, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user last signed in", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateUserLastRefreshedAtById(ctx context.Context, id int64, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserLastRefreshedAtById"

	query, args, err := s.queryUpdateUserLastRefreshedAtById(id, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user last refreshed at", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateUserLastActivityAtById(ctx context.Context, id int64, updatedBy *int64) (err error) {
	const tag = path + "/UpdateUserLastActivityAtById"

	query, args, err := s.queryUpdateUserLastActivityAtById(id, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update user last activity at", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteUserById(ctx context.Context, id int64) (err error) {
	const tag = path + "/DeleteUserById"

	query, args, err := s.queryDeleteUserById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete user", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}
