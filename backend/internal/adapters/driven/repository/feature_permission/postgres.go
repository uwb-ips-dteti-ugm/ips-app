package adaptersdrivenrepositoryfeaturepermission

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
) portsdrivenrepository.FeaturePermission {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreateFeaturePermission(ctx context.Context, featureId int64, permissionId int64, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreateFeaturePermission"

	query, args, err := s.queryCreateFeaturePermission(featureId, permissionId, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create feature_permission", domainmodels.LogMeta{"error": err.Error()})
		return 0, err
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadPermissionsByFeatureId(ctx context.Context, featureId int64) (items []domainmodels.Permission, err error) {
	const tag = path + "/ReadPermissionsByFeatureId"

	query, args, err := s.queryReadPermissionsByFeatureId(featureId)
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

func (s *postgresImpl) ReadFeaturesByPermissionId(ctx context.Context, permissionId int64) (items []domainmodels.Feature, err error) {
	const tag = path + "/ReadFeaturesByPermissionId"

	query, args, err := s.queryReadFeaturesByPermissionId(permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read features", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}
	defer rows.Close()

	items = make([]domainmodels.Feature, 0)
	for rows.Next() {
		var item domainmodels.Feature
		if err := rows.Scan(&item.Id, &item.Name, &item.Description, &item.Preferences, &item.CreatedAt, &item.CreatedBy, &item.UpdatedAt, &item.UpdatedBy, &item.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan feature", domainmodels.LogMeta{"error": err.Error()})
			return nil, err
		}
		items = append(items, item)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate features", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return items, nil
}

func (s *postgresImpl) DeleteFeaturePermissionByFeatureIdAndPermissionId(ctx context.Context, featureId int64, permissionId int64) (err error) {
	const tag = path + "/DeleteFeaturePermissionByFeatureIdAndPermissionId"

	query, args, err := s.queryDeleteFeaturePermissionByFeatureIdAndPermissionId(featureId, permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete feature_permission", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteFeaturePermissionsByFeatureId(ctx context.Context, featureId int64) (err error) {
	const tag = path + "/DeleteFeaturePermissionsByFeatureId"

	query, args, err := s.queryDeleteFeaturePermissionsByFeatureId(featureId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete feature_permissions", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteFeaturePermissionsByPermissionId(ctx context.Context, permissionId int64) (err error) {
	const tag = path + "/DeleteFeaturePermissionsByPermissionId"

	query, args, err := s.queryDeleteFeaturePermissionsByPermissionId(permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete feature_permissions", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}
