package adaptersdrivenrepositorypermission

import (
	"encoding/json"

	"github.com/Masterminds/squirrel"
)

func (s *postgresImpl) queryCreatePermission(
	name string,
	description string,
	createdBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Insert("permissions").
		Columns(
			"name",
			"description",
			"created_by",
		).
		Values(
			name,
			description,
			createdBy,
		).
		Suffix("RETURNING id").
		ToSql()
}

func (s *postgresImpl) queryReadPermissionById(
	id int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"name",
			"description",
			"preferences",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("permissions").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}

func (s *postgresImpl) queryReadPermissionsByPagination(
	page int,
	limit int,
	cursorId *int64,
	search *string,
) (
	countQuery string,
	countArgs []any,
	query string,
	args []any,
	err error,
) {
	baseQ := s.sqrQuestion.Select("*").From("permissions")
	countQ := s.sqrQuestion.Select("COUNT(*)").From("permissions")

	if search != nil && *search != "" {
		searchPattern := "%" + *search + "%"
		baseQ = baseQ.Where("name ILIKE ?", searchPattern)
		countQ = countQ.Where("name ILIKE ?", searchPattern)
	}

	if cursorId != nil {
		baseQ = baseQ.Where("id > ?", *cursorId)
		countQ = countQ.Where("id > ?", *cursorId)
	}

	countQuery, countArgs, err = countQ.ToSql()
	if err != nil {
		return
	}

	query, args, err = baseQ.
		OrderBy("id ASC").
		Limit(uint64(limit)).
		Offset(uint64(page * limit)).
		ToSql()

	return
}

func (s *postgresImpl) queryUpdatePermissionById(
	id int64,
	name *string,
	description *string,
	updatedBy *int64,
) (query string, args []any, err error) {
	q := s.sqrQuestion.
		Update("permissions").
		Where(squirrel.Eq{"id": id})

	if name != nil {
		q = q.Set("name", *name)
	}

	if description != nil {
		q = q.Set("description", *description)
	}

	return q.
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdatePermissionPreferencesById(
	id int64,
	preferences json.RawMessage,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("permissions").
		Where(squirrel.Eq{"id": id}).
		Set("preferences", preferences).
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryDeletePermissionById(
	id int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("permissions").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}
