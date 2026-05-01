package adaptersdrivenrepositoryrolepermission

import (
	"context"

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
) portsdrivenrepository.RolePermission {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreateRolePermission(ctx context.Context, roleId int64, permissionId int64, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreateRolePermission"

	query, args, err := s.queryCreateRolePermission(roleId, permissionId, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create role_permission", domainmodels.LogMeta{"error": err.Error()})
		return 0, err
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadPermissionsByRoleId(ctx context.Context, roleId int64) (items []domainmodels.Permission, err error) {
	const tag = path + "/ReadPermissionsByRoleId"

	query, args, err := s.queryReadPermissionsByRoleId(roleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}
	defer rows.Close()

	items = make([]domainmodels.Permission, 0)
	for rows.Next() {
		var item domainmodels.Permission
		if err := rows.Scan(&item.Id, &item.Name, &item.Description, &item.Preferences, &item.CreatedAt, &item.CreatedBy, &item.UpdatedAt, &item.UpdatedBy, &item.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan permission", domainmodels.LogMeta{"error": err.Error()})
			return nil, err
		}
		items = append(items, item)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return items, nil
}

func (s *postgresImpl) ReadRolesByPermissionId(ctx context.Context, permissionId int64) (items []domainmodels.Role, err error) {
	const tag = path + "/ReadRolesByPermissionId"

	query, args, err := s.queryReadRolesByPermissionId(permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read roles", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}
	defer rows.Close()

	items = make([]domainmodels.Role, 0)
	for rows.Next() {
		var item domainmodels.Role
		if err := rows.Scan(&item.Id, &item.Name, &item.Description, &item.Preferences, &item.CreatedAt, &item.CreatedBy, &item.UpdatedAt, &item.UpdatedBy, &item.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan role", domainmodels.LogMeta{"error": err.Error()})
			return nil, err
		}
		items = append(items, item)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate roles", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return items, nil
}

func (s *postgresImpl) DeleteRolePermissionByRoleIdAndPermissionId(ctx context.Context, roleId int64, permissionId int64) (err error) {
	const tag = path + "/DeleteRolePermissionByRoleIdAndPermissionId"

	query, args, err := s.queryDeleteRolePermissionByRoleIdAndPermissionId(roleId, permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete role_permission", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteRolePermissionsByRoleId(ctx context.Context, roleId int64) (err error) {
	const tag = path + "/DeleteRolePermissionsByRoleId"

	query, args, err := s.queryDeleteRolePermissionsByRoleId(roleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete role_permissions", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteRolePermissionsByPermissionId(ctx context.Context, permissionId int64) (err error) {
	const tag = path + "/DeleteRolePermissionsByPermissionId"

	query, args, err := s.queryDeleteRolePermissionsByPermissionId(permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete role_permissions", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}
