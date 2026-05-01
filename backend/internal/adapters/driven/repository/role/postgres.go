package adaptersdrivenrepositoryrole

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
) portsdrivenrepository.Role {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreateRole(ctx context.Context, name string, description string, isDefault bool, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreateRole"

	query, args, err := s.queryCreateRole(name, description, isDefault, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create role", domainmodels.LogMeta{"error": err.Error()})
		return 0, err
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadRoleById(ctx context.Context, id int64) (item *domainmodels.Role, err error) {
	const tag = path + "/ReadRoleById"

	query, args, err := s.queryReadRoleById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var r domainmodels.Role
	err = row.Scan(&r.Id, &r.Name, &r.Description, &r.Preferences, &r.IsDefault, &r.CreatedAt, &r.CreatedBy, &r.UpdatedAt, &r.UpdatedBy, &r.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read role", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &r, nil
}

func (s *postgresImpl) ReadRolesByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (items []domainmodels.Role, total int, err error) {
	const tag = path + "/ReadRolesByPagination"

	countQuery, countArgs, query, args, err := s.queryReadRolesByPagination(page, limit, cursorId, search)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, domainmodels.ErrQueryBuilder
	}

	countRow := s.dt.QueryRow(ctx, countQuery, countArgs...)
	if err := countRow.Scan(&total); err != nil {
		s.log.Error(ctx, tag, "Failed to count roles", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	if total == 0 {
		return []domainmodels.Role{}, 0, nil
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read roles", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}
	defer rows.Close()

	items = make([]domainmodels.Role, 0, total)
	for rows.Next() {
		var r domainmodels.Role
		if err := rows.Scan(&r.Id, &r.Name, &r.Description, &r.Preferences, &r.IsDefault, &r.CreatedAt, &r.CreatedBy, &r.UpdatedAt, &r.UpdatedBy, &r.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan role", domainmodels.LogMeta{"error": err.Error()})
			return nil, 0, err
		}
		items = append(items, r)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate roles", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return items, total, nil
}

func (s *postgresImpl) ReadRoleDefault(ctx context.Context) (item *domainmodels.Role, err error) {
	const tag = path + "/ReadRoleDefault"

	query, args, err := s.queryReadRoleDefault()
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var r domainmodels.Role
	err = row.Scan(&r.Id, &r.Name, &r.Description, &r.Preferences, &r.IsDefault, &r.CreatedAt, &r.CreatedBy, &r.UpdatedAt, &r.UpdatedBy, &r.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read default role", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &r, nil
}

func (s *postgresImpl) UpdateRoleById(ctx context.Context, id int64, name *string, description *string, updatedBy *int64) (err error) {
	const tag = path + "/UpdateRoleById"

	query, args, err := s.queryUpdateRoleById(id, name, description, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update role", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateRoleIsDefaultById(ctx context.Context, id int64, updatedBy *int64) (err error) {
	const tag = path + "/UpdateRoleIsDefaultById"

	unsetQuery, unsetArgs, setQuery, setArgs, err := s.queryUpdateRoleIsDefaultById(id, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	err = s.dt.WithTx(ctx, func(ctx context.Context) error {
		if _, err := s.dt.Exec(ctx, unsetQuery, unsetArgs...); err != nil {
			return err
		}

		if _, err := s.dt.Exec(ctx, setQuery, setArgs...); err != nil {
			return err
		}

		return nil
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set default role", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateRolePreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error) {
	const tag = path + "/UpdateRolePreferencesById"

	query, args, err := s.queryUpdateRolePreferencesById(id, preferences, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update role preferences", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteRoleById(ctx context.Context, id int64) (err error) {
	const tag = path + "/DeleteRoleById"

	query, args, err := s.queryDeleteRoleById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete role", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}
