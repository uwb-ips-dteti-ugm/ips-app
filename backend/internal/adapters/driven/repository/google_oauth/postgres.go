package adaptersdrivenrepositorygoogleoauth

import (
	"context"
	"database/sql"
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
) portsdrivenrepository.GoogleOAuth {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreateGoogleOAuth(ctx context.Context, userId int64, sub string, email string, name string, refreshToken string, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreateGoogleOAuth"

	query, args, err := s.queryCreateGoogleOAuth(userId, sub, email, name, &refreshToken, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create google_oauth", domainmodels.LogMeta{"error": err.Error()})
		return 0, err
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadGoogleOAuthById(ctx context.Context, id int64) (item *domainmodels.GoogleOAuth, err error) {
	const tag = path + "/ReadGoogleOAuthById"

	query, args, err := s.queryReadGoogleOAuthById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var oauth domainmodels.GoogleOAuth
	err = row.Scan(&oauth.Id, &oauth.UserId, &oauth.Sub, &oauth.Email, &oauth.Name, &oauth.RefreshToken, &oauth.CreatedAt, &oauth.CreatedBy, &oauth.UpdatedAt, &oauth.UpdatedBy, &oauth.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read google_oauth", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &oauth, nil
}

func (s *postgresImpl) ReadGoogleOAuthByUserId(ctx context.Context, userId int64) (item *domainmodels.GoogleOAuth, err error) {
	const tag = path + "/ReadGoogleOAuthByUserId"

	query, args, err := s.queryReadGoogleOAuthByUserId(userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var oauth domainmodels.GoogleOAuth
	err = row.Scan(&oauth.Id, &oauth.UserId, &oauth.Sub, &oauth.Email, &oauth.Name, &oauth.RefreshToken, &oauth.CreatedAt, &oauth.CreatedBy, &oauth.UpdatedAt, &oauth.UpdatedBy, &oauth.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read google_oauth", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &oauth, nil
}

func (s *postgresImpl) ReadGoogleOAuthBySub(ctx context.Context, sub string) (item *domainmodels.GoogleOAuth, err error) {
	const tag = path + "/ReadGoogleOAuthBySub"

	query, args, err := s.queryReadGoogleOAuthBySub(sub)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var oauth domainmodels.GoogleOAuth
	err = row.Scan(&oauth.Id, &oauth.UserId, &oauth.Sub, &oauth.Email, &oauth.Name, &oauth.RefreshToken, &oauth.CreatedAt, &oauth.CreatedBy, &oauth.UpdatedAt, &oauth.UpdatedBy, &oauth.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read google_oauth", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &oauth, nil
}

func (s *postgresImpl) ReadGoogleOAuthByEmail(ctx context.Context, email string) (item *domainmodels.GoogleOAuth, err error) {
	const tag = path + "/ReadGoogleOAuthByEmail"

	query, args, err := s.queryReadGoogleOAuthByEmail(email)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var oauth domainmodels.GoogleOAuth
	err = row.Scan(&oauth.Id, &oauth.UserId, &oauth.Sub, &oauth.Email, &oauth.Name, &oauth.RefreshToken, &oauth.CreatedAt, &oauth.CreatedBy, &oauth.UpdatedAt, &oauth.UpdatedBy, &oauth.Version)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return nil, domainmodels.ErrNotFound
		}
		s.log.Error(ctx, tag, "Failed to read google_oauth", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return &oauth, nil
}

func (s *postgresImpl) UpdateGoogleOAuthBySub(ctx context.Context, sub string, email *string, name *string, refreshToken *string, updatedBy *int64) (err error) {
	const tag = path + "/UpdateGoogleOAuthBySub"

	query, args, err := s.queryUpdateGoogleOAuthBySub(sub, email, name, refreshToken, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update google_oauth", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteGoogleOAuthByUserId(ctx context.Context, userId int64) (err error) {
	const tag = path + "/DeleteGoogleOAuthByUserId"

	query, args, err := s.queryDeleteGoogleOAuthByUserId(userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete google_oauth", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}
