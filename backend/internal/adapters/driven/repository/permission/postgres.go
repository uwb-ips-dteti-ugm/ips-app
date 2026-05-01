package adaptersdrivenrepositorypermission

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
) portsdrivenrepository.Permission {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreatePermission(ctx context.Context, name string, description string, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreatePermission"

	query, args, err := s.queryCreatePermission(name, description, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create permission", domainmodels.LogMeta{"error": err.Error()})
		return 0, err
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadPermissionById(ctx context.Context, id int64) (item *domainmodels.Permission, err error) {
	const tag = path + "/ReadPermissionById"

	query, args, err := s.queryReadPermissionById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var perm domainmodels.Permission
	err = row.Scan(&perm.Id, &perm.Name, &perm.Description, &perm.Preferences, &perm.CreatedAt, &perm.CreatedBy, &perm.UpdatedAt, &perm.UpdatedBy, &perm.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read permission", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &perm, nil
}

func (s *postgresImpl) ReadPermissionsByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (items []domainmodels.Permission, total int, err error) {
	const tag = path + "/ReadPermissionsByPagination"

	countQuery, countArgs, query, args, err := s.queryReadPermissionsByPagination(page, limit, cursorId, search)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, domainmodels.ErrQueryBuilder
	}

	countRow := s.dt.QueryRow(ctx, countQuery, countArgs...)
	if err := countRow.Scan(&total); err != nil {
		s.log.Error(ctx, tag, "Failed to count permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	if total == 0 {
		return []domainmodels.Permission{}, 0, nil
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}
	defer rows.Close()

	items = make([]domainmodels.Permission, 0, total)
	for rows.Next() {
		var item domainmodels.Permission
		if err := rows.Scan(&item.Id, &item.Name, &item.Description, &item.Preferences, &item.CreatedAt, &item.CreatedBy, &item.UpdatedAt, &item.UpdatedBy, &item.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan permission", domainmodels.LogMeta{"error": err.Error()})
			return nil, 0, err
		}
		items = append(items, item)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return items, total, nil
}

func (s *postgresImpl) UpdatePermissionById(ctx context.Context, id int64, name *string, description *string, updatedBy *int64) (err error) {
	const tag = path + "/UpdatePermissionById"

	query, args, err := s.queryUpdatePermissionById(id, name, description, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update permission", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdatePermissionPreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error) {
	const tag = path + "/UpdatePermissionPreferencesById"

	query, args, err := s.queryUpdatePermissionPreferencesById(id, preferences, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update permission preferences", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeletePermissionById(ctx context.Context, id int64) (err error) {
	const tag = path + "/DeletePermissionById"

	query, args, err := s.queryDeletePermissionById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete permission", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}
