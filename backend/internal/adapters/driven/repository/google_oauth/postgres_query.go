package adaptersdrivenrepositorygoogleoauth

import (
	"github.com/Masterminds/squirrel"
)

func (s *postgresImpl) queryCreateGoogleOAuth(userId int64, sub string, email string, name string, refreshToken *string, createdBy *int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Insert("google_oauths").
		Columns("user_id", "sub", "email", "name", "refresh_token", "created_by").
		Values(userId, sub, email, name, refreshToken, createdBy).
		Suffix("RETURNING id").
		ToSql()
}

func (s *postgresImpl) queryReadGoogleOAuthById(id int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select("id", "user_id", "sub", "email", "name", "refresh_token", "created_at", "created_by", "updated_at", "updated_by", "version").
		From("google_oauths").
		Where(squirrel.Eq{"id": id}).
		ToSql()
}

func (s *postgresImpl) queryReadGoogleOAuthByUserId(userId int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select("id", "user_id", "sub", "email", "name", "refresh_token", "created_at", "created_by", "updated_at", "updated_by", "version").
		From("google_oauths").
		Where(squirrel.Eq{"user_id": userId}).
		ToSql()
}

func (s *postgresImpl) queryReadGoogleOAuthBySub(sub string) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select("id", "user_id", "sub", "email", "name", "refresh_token", "created_at", "created_by", "updated_at", "updated_by", "version").
		From("google_oauths").
		Where(squirrel.Eq{"sub": sub}).
		ToSql()
}

func (s *postgresImpl) queryReadGoogleOAuthByEmail(email string) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select("id", "user_id", "sub", "email", "name", "refresh_token", "created_at", "created_by", "updated_at", "updated_by", "version").
		From("google_oauths").
		Where(squirrel.Eq{"email": email}).
		ToSql()
}

func (s *postgresImpl) queryUpdateGoogleOAuthBySub(sub string, email *string, name *string, refreshToken *string, updatedBy *int64) (query string, args []any, err error) {
	q := s.sqrQuestion.
		Update("google_oauths").
		Where(squirrel.Eq{"sub": sub})

	if email != nil {
		q = q.Set("email", *email)
	}
	if name != nil {
		q = q.Set("name", *name)
	}
	if refreshToken != nil {
		q = q.Set("refresh_token", *refreshToken)
	}

	return q.Set("updated_at", "CURRENT_TIMESTAMP").
		Set("updated_by", updatedBy).
		Set("version", squirrel.Expr("version + 1")).
		ToSql()
}

func (s *postgresImpl) queryDeleteGoogleOAuthByUserId(userId int64) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("google_oauths").
		Where(squirrel.Eq{"user_id": userId}).
		ToSql()
}
