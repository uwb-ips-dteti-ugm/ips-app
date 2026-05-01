package adaptersdrivenrepositoryfeature

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
) portsdrivenrepository.Feature {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreateFeature(ctx context.Context, name string, description string, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreateFeature"

	query, args, err := s.queryCreateFeature(name, description, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create feature", domainmodels.LogMeta{"error": err.Error()})
		return 0, err
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadFeatureById(ctx context.Context, id int64) (item *domainmodels.Feature, err error) {
	const tag = path + "/ReadFeatureById"

	query, args, err := s.queryReadFeatureById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var feature domainmodels.Feature
	err = row.Scan(&feature.Id, &feature.Name, &feature.Description, &feature.Preferences, &feature.CreatedAt, &feature.CreatedBy, &feature.UpdatedAt, &feature.UpdatedBy, &feature.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read feature", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &feature, nil
}

func (s *postgresImpl) ReadFeaturesByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (items []domainmodels.Feature, total int, err error) {
	const tag = path + "/ReadFeaturesByPagination"

	countQuery, countArgs, query, args, err := s.queryReadFeaturesByPagination(page, limit, cursorId, search)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, domainmodels.ErrQueryBuilder
	}

	countRow := s.dt.QueryRow(ctx, countQuery, countArgs...)
	if err := countRow.Scan(&total); err != nil {
		s.log.Error(ctx, tag, "Failed to count features", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	if total == 0 {
		return []domainmodels.Feature{}, 0, nil
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read features", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}
	defer rows.Close()

	items = make([]domainmodels.Feature, 0, total)
	for rows.Next() {
		var item domainmodels.Feature
		if err := rows.Scan(&item.Id, &item.Name, &item.Description, &item.Preferences, &item.CreatedAt, &item.CreatedBy, &item.UpdatedAt, &item.UpdatedBy, &item.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan feature", domainmodels.LogMeta{"error": err.Error()})
			return nil, 0, err
		}
		items = append(items, item)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate features", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return items, total, nil
}

func (s *postgresImpl) UpdateFeatureById(ctx context.Context, id int64, name *string, description *string, updatedBy *int64) (err error) {
	const tag = path + "/UpdateFeatureById"

	query, args, err := s.queryUpdateFeatureById(id, name, description, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update feature", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) UpdateFeaturePreferencesById(ctx context.Context, id int64, preferences json.RawMessage, updatedBy *int64) (err error) {
	const tag = path + "/UpdateFeaturePreferencesById"

	query, args, err := s.queryUpdateFeaturePreferencesById(id, preferences, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update feature preferences", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteFeatureById(ctx context.Context, id int64) (err error) {
	const tag = path + "/DeleteFeatureById"

	query, args, err := s.queryDeleteFeatureById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete feature", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}
