package adaptersdrivenrepositoryauth

import (
	"context"
	"database/sql"
	"errors"
	"strings"

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
) portsdrivenrepository.Auth {
	return &postgresImpl{
		dt:          dt,
		sqrQuestion: sqrQuestion,
		log:         log,
	}
}

func (s *postgresImpl) CreateAuth(ctx context.Context, userId int64, username string, passwordHash string, email *string, phone *string, createdBy *int64) (id int64, err error) {
	const tag = path + "/CreateAuth"

	query, args, err := s.queryCreateAuth(userId, username, passwordHash, email, phone, createdBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return 0, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var lastInsertId int64
	err = row.Scan(&lastInsertId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to create auth", domainmodels.LogMeta{"error": err.Error()})
		return 0, s.mapError(err)
	}

	return lastInsertId, nil
}

func (s *postgresImpl) ReadAuthById(ctx context.Context, id int64) (item *domainmodels.Auth, err error) {
	const tag = path + "/ReadAuthById"

	query, args, err := s.queryReadAuthById(id)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var auth domainmodels.Auth
	err = row.Scan(&auth.Id, &auth.UserId, &auth.Username, &auth.Email, &auth.Phone, &auth.PasswordHash, &auth.CreatedAt, &auth.CreatedBy, &auth.UpdatedAt, &auth.UpdatedBy, &auth.Version)
	if err != nil {
		mapped := s.mapError(err)
		if errors.Is(mapped, domainmodels.ErrNotFound) {
			return nil, mapped
		}
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return nil, mapped
	}

	return &auth, nil
}

func (s *postgresImpl) ReadAuthByUserId(ctx context.Context, userId int64) (item *domainmodels.Auth, err error) {
	const tag = path + "/ReadAuthByUserId"

	query, args, err := s.queryReadAuthByUserId(userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var auth domainmodels.Auth
	err = row.Scan(&auth.Id, &auth.UserId, &auth.Username, &auth.Email, &auth.Phone, &auth.PasswordHash, &auth.CreatedAt, &auth.CreatedBy, &auth.UpdatedAt, &auth.UpdatedBy, &auth.Version)
	if err != nil {
		mapped := s.mapError(err)
		if errors.Is(mapped, domainmodels.ErrNotFound) {
			return nil, mapped
		}
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return nil, mapped
	}

	return &auth, nil
}

func (s *postgresImpl) ReadAuthBySignInIdentifier(ctx context.Context, signInIdentifier string) (item *domainmodels.Auth, err error) {
	const tag = path + "/ReadAuthBySignInIdentifier"

	query, args, err := s.queryReadAuthBySignInIdentifier(signInIdentifier)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, domainmodels.ErrQueryBuilder
	}

	row := s.dt.QueryRow(ctx, query, args...)
	var auth domainmodels.Auth
	err = row.Scan(&auth.Id, &auth.UserId, &auth.Username, &auth.Email, &auth.Phone, &auth.PasswordHash, &auth.CreatedAt, &auth.CreatedBy, &auth.UpdatedAt, &auth.UpdatedBy, &auth.Version)
	if err != nil {
		mapped := s.mapError(err)
		if errors.Is(mapped, domainmodels.ErrNotFound) {
			return nil, mapped
		}
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return nil, mapped
	}

	return &auth, nil
}

func (s *postgresImpl) ReadAuthsByPagination(ctx context.Context, page int, limit int, cursorId *int64, search *string) (items []domainmodels.Auth, total int, err error) {
	const tag = path + "/ReadAuthsByPagination"

	countQuery, countArgs, query, args, err := s.queryReadAuthsByPagination(page, limit, cursorId, search)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, domainmodels.ErrQueryBuilder
	}

	countRow := s.dt.QueryRow(ctx, countQuery, countArgs...)
	if err := countRow.Scan(&total); err != nil {
		s.log.Error(ctx, tag, "Failed to count auths", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	if total == 0 {
		return []domainmodels.Auth{}, 0, nil
	}

	rows, err := s.dt.Query(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read auths", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}
	defer rows.Close()

	items = make([]domainmodels.Auth, 0, total)
	for rows.Next() {
		var auth domainmodels.Auth
		if err := rows.Scan(&auth.Id, &auth.UserId, &auth.Username, &auth.Email, &auth.Phone, &auth.PasswordHash, &auth.CreatedAt, &auth.CreatedBy, &auth.UpdatedAt, &auth.UpdatedBy, &auth.Version); err != nil {
			s.log.Error(ctx, tag, "Failed to scan auth", domainmodels.LogMeta{"error": err.Error()})
			return nil, 0, err
		}
		items = append(items, auth)
	}

	if err := rows.Err(); err != nil {
		s.log.Error(ctx, tag, "Failed to iterate auths", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return items, total, nil
}

func (s *postgresImpl) UpdateAuthInfoById(ctx context.Context, id int64, username *string, email *string, phone *string, updatedBy *int64) (err error) {
	const tag = path + "/UpdateAuthInfoById"

	query, args, err := s.queryUpdateAuthInfoById(id, username, email, phone, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update auth", domainmodels.LogMeta{"error": err.Error()})
		return s.mapError(err)
	}

	return nil
}

func (s *postgresImpl) UpdateAuthPasswordById(ctx context.Context, id int64, passwordHash string, updatedBy *int64) (err error) {
	const tag = path + "/UpdateAuthPasswordById"

	query, args, err := s.queryUpdateAuthPasswordById(id, passwordHash, updatedBy)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to update auth password", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) DeleteAuthByUserId(ctx context.Context, userId int64) (err error) {
	const tag = path + "/DeleteAuthByUserId"

	query, args, err := s.queryDeleteAuthByUserId(userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to build query", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.ErrQueryBuilder
	}

	_, err = s.dt.Exec(ctx, query, args...)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to delete auth", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *postgresImpl) mapError(err error) error {
	if err == nil {
		return nil
	}
	if errors.Is(err, sql.ErrNoRows) {
		return domainmodels.ErrNotFound
	}
	switch {
	case strings.Contains(err.Error(), "auths_username_key"):
		return domainmodels.ErrUsernameTaken
	case strings.Contains(err.Error(), "auths_email_key"):
		return domainmodels.ErrEmailTaken
	case strings.Contains(err.Error(), "auths_phone_key"):
		return domainmodels.ErrPhoneTaken
	}
	return err
}
