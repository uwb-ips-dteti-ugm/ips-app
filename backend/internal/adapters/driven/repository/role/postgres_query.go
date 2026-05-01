package adaptersdrivenrepositoryrole

import (
	"encoding/json"

	"github.com/Masterminds/squirrel"
)

func (s *postgresImpl) queryCreateRole(name string, description string, isDefault bool, createdBy *int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Insert("roles").
		Columns(
			"name",
			"description",
			"is_default",
			"created_by",
		).
		Values(
			name,
			description,
			isDefault,
			createdBy,
		).
		Suffix("RETURNING id").
		ToSql()
}

func (s *postgresImpl) queryReadRoleById(id int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"name",
			"description",
			"preferences",
			"is_default",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("roles").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}

func (s *postgresImpl) queryReadRolesByPagination(page int, limit int, cursorId *int64, search *string) (countQuery string, countArgs []any, query string, args []any, err error) {
	baseQ := s.sqrQuestion.Select("*").From("roles")
	countQ := s.sqrQuestion.Select("COUNT(*)").From("roles")

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

func (s *postgresImpl) queryReadRoleDefault() (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"name",
			"description",
			"preferences",
			"is_default",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("roles").
		Where(squirrel.Eq{"is_default": true}).
		Limit(1).
		ToSql()
}

func (s *postgresImpl) queryUpdateRoleById(id int64, name *string, description *string, updatedBy *int64) (query string, args []any, err error) {
	q := s.sqrQuestion.
		Update("roles").
		Where(squirrel.Eq{"id": id})

	if name != nil {
		q = q.Set("name", *name)
	}
	if description != nil {
		q = q.Set("description", *description)
	}

	return q.Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateRoleIsDefaultById(id int64, updatedBy *int64) (
	unsetQuery string,
	unsetArgs []any,
	setQuery string,
	setArgs []any,
	err error,
) {
	unsetQuery, unsetArgs, err = s.sqrQuestion.
		Update("roles").
		Where(squirrel.Eq{"is_default": true}).
		Where(squirrel.NotEq{"id": id}).
		Set("is_default", false).
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
	if err != nil {
		return
	}

	setQuery, setArgs, err = s.sqrQuestion.
		Update("roles").
		Where(squirrel.Eq{"id": id}).
		Set("is_default", true).
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()

	return
}

func (s *postgresImpl) queryUpdateRolePreferencesById(id int64, preferences json.RawMessage, updatedBy *int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("roles").
		Where(squirrel.Eq{"id": id}).
		Set("preferences", preferences).
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryDeleteRoleById(id int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("roles").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}
