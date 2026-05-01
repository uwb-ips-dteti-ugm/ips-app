package adaptersdrivenrepositoryauth

import (
	"github.com/Masterminds/squirrel"
)

func (s *postgresImpl) queryCreateAuth(
	userId int64,
	username string,
	passwordHash string,
	email *string,
	phone *string,
	createdBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Insert("auths").
		Columns(
			"user_id",
			"username",
			"password_hash",
			"email",
			"phone",
			"created_by",
		).
		Values(
			userId,
			username,
			passwordHash,
			email,
			phone,
			createdBy,
		).
		Suffix("RETURNING id").
		ToSql()
}

func (s *postgresImpl) queryReadAuthById(
	id int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"user_id",
			"username",
			"email",
			"phone",
			"password_hash",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("auths").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}

func (s *postgresImpl) queryReadAuthByUserId(
	userId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"user_id",
			"username",
			"email",
			"phone",
			"password_hash",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("auths").
		Where(squirrel.Eq{"user_id": userId}).
		ToSql()
}

func (s *postgresImpl) queryReadAuthBySignInIdentifier(
	signInIdentifier string,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"user_id",
			"username",
			"email",
			"phone",
			"password_hash",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("auths").
		Where(squirrel.Or{
			squirrel.Eq{"username": signInIdentifier},
			squirrel.Eq{"email": signInIdentifier},
			squirrel.Eq{"phone": signInIdentifier},
		}).
		ToSql()
}

func (s *postgresImpl) queryReadAuthsByPagination(
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
	baseQ := s.sqrQuestion.Select("*").From("auths")
	countQ := s.sqrQuestion.Select("COUNT(*)").From("auths")

	if search != nil && *search != "" {
		searchPattern := "%" + *search + "%"
		baseQ = baseQ.Where(squirrel.Or{
			squirrel.Expr("username ILIKE ?", searchPattern),
			squirrel.Expr("email ILIKE ?", searchPattern),
			squirrel.Expr("phone ILIKE ?", searchPattern),
		})
		countQ = countQ.Where(squirrel.Or{
			squirrel.Expr("username ILIKE ?", searchPattern),
			squirrel.Expr("email ILIKE ?", searchPattern),
			squirrel.Expr("phone ILIKE ?", searchPattern),
		})
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

func (s *postgresImpl) queryUpdateAuthInfoById(
	id int64,
	username *string,
	email *string,
	phone *string,
	updatedBy *int64,
) (query string, args []any, err error) {
	q := s.sqrQuestion.
		Update("auths").
		Where(squirrel.Eq{"id": id})

	if username != nil {
		q = q.Set("username", *username)
	}

	if email != nil {
		q = q.Set("email", *email)
	}

	if phone != nil {
		q = q.Set("phone", *phone)
	}

	return q.
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryUpdateAuthPasswordById(
	id int64,
	passwordHash string,
	updatedBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Update("auths").
		Where(squirrel.Eq{"id": id}).
		Set("password_hash", passwordHash).
		Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryDeleteAuthByUserId(
	userId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("auths").
		Where(squirrel.Eq{"user_id": userId}).
		ToSql()
}
