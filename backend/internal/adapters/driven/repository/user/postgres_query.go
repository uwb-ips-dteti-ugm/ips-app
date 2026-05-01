package adaptersdrivenrepositoryuser

import (
	"github.com/Masterminds/squirrel"
)

func (s *postgresImpl) queryCreateUser(
	roleId int64,
	name string,
	createdBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Insert("users").
		Columns(
			"role_id",
			"name",
			"created_by",
		).
		Values(
			roleId,
			name,
			createdBy,
		).
		Suffix("RETURNING id").
		ToSql()
}

func (s *postgresImpl) queryReadUserById(
	id int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"role_id",
			"name",
			"bio",
			"state",
			"status",
			"preferences",
			"last_signed_in_at",
			"last_refreshed_at",
			"last_activity_at",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("users").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}

func (s *postgresImpl) queryReadUsersByPagination(
	page int,
	limit int,
	cursorId *int64,
	search *string,
	roleId *int64,
) (
	countQuery string,
	countArgs []any,
	query string,
	args []any,
	err error,
) {
	baseQ := s.sqrQuestion.Select("*").From("users")
	countQ := s.sqrQuestion.Select("COUNT(*)").From("users")

	if search != nil && *search != "" {
		searchPattern := "%" + *search + "%"
		baseQ = baseQ.Where("name ILIKE ?", searchPattern)
		countQ = countQ.Where("name ILIKE ?", searchPattern)
	}

	if cursorId != nil {
		baseQ = baseQ.Where("id > ?", *cursorId)
		countQ = countQ.Where("id > ?", *cursorId)
	}

	if roleId != nil {
		baseQ = baseQ.Where("role_id = ?", *roleId)
		countQ = countQ.Where("role_id = ?", *roleId)
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

func (s *postgresImpl) queryUpdateUserInfoById(
	id int64,
	name *string,
	bio *string,
	updatedBy *int64,
) (query string, args []any, err error) {
	q := s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id})

	if name != nil {
		q = q.Set("name", *name)
	}

	if bio != nil {
		q = q.Set("bio", *bio)
	}

	return q.
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateUserStatusById(
	id int64,
	status string,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id}).
		Set("status", status).
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateUserStateById(
	id int64,
	state string,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id}).
		Set("state", state).
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateUserRoleById(
	id int64,
	roleId int64,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id}).
		Set("role_id", roleId).
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateUserPreferencesById(
	id int64,
	preferences *string,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id}).
		Set("preferences", *preferences).
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateUserLastSignedInAtById(
	id int64,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id}).
		Set("last_signed_in_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateUserLastRefreshedAtById(
	id int64,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id}).
		Set("last_refreshed_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateUserLastActivityAtById(
	id int64,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("users").
		Where(squirrel.Eq{"id": id}).
		Set("last_activity_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryDeleteUserById(
	id int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("users").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}
