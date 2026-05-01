package domainserviceshttpauth

import (
	"context"
	"errors"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
	portsdrivenlogging "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/logging"
	portsdrivenrepository "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/repository"
	portsdrivinghttp "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driving/http"
	"github.com/uwb-ips-dteti-ugm/ips-app/backend/pkg/pgxdt"
	"github.com/uwb-ips-dteti-ugm/ips-app/backend/pkg/pwd"
	"github.com/uwb-ips-dteti-ugm/ips-app/backend/pkg/token"
)

type baseImpl struct {
	tx              pgxdt.Transactor
	log             portsdrivenlogging.Generic
	repoAuth        portsdrivenrepository.Auth
	repoGoogleOAuth portsdrivenrepository.GoogleOAuth
	repoRole        portsdrivenrepository.Role
	repoUser        portsdrivenrepository.User
}

func NewBaseImpl(
	tx pgxdt.Transactor,
	log portsdrivenlogging.Generic,
	repoAuth portsdrivenrepository.Auth,
	repoGoogleOAuth portsdrivenrepository.GoogleOAuth,
	repoRole portsdrivenrepository.Role,
	repoUser portsdrivenrepository.User,
) portsdrivinghttp.Auth {
	return &baseImpl{
		tx:              tx,
		log:             log,
		repoAuth:        repoAuth,
		repoGoogleOAuth: repoGoogleOAuth,
		repoRole:        repoRole,
		repoUser:        repoUser,
	}
}

func (s *baseImpl) SignUp(ctx context.Context, name string, username string, email *string, phone *string, password string) (accessToken string, refreshToken string, err error) {
	const tag = path + "/SignUp"

	defaultRole, err := s.repoRole.ReadRoleDefault(ctx)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read default role", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	passwordHash, err := pwd.Hash(password)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to hash password", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	var userId int64
	err = s.tx.WithTx(ctx, func(ctx context.Context) error {
		var err error
		userId, err = s.repoUser.CreateUser(ctx, defaultRole.Id, name, nil)
		if err != nil {
			return err
		}

		_, err = s.repoAuth.CreateAuth(ctx, userId, username, passwordHash, email, phone, nil)
		if err != nil {
			return err
		}

		return nil
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to sign up", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	user := domainmodels.User{Id: userId, RoleId: defaultRole.Id, Name: name}
	return s.generateTokens(ctx, tag, user)
}

func (s *baseImpl) SignIn(ctx context.Context, signInIdentifier string, passwordInput string) (accessToken string, refreshToken string, err error) {
	const tag = path + "/SignIn"

	auth, err := s.repoAuth.ReadAuthBySignInIdentifier(ctx, signInIdentifier)
	if err != nil {
		if errors.Is(err, domainmodels.ErrNotFound) {
			return "", "", domainmodels.ErrInvalidCredentials
		}
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	if err := pwd.Compare(auth.PasswordHash, passwordInput); err != nil {
		return "", "", domainmodels.ErrInvalidCredentials
	}

	user, err := s.repoUser.ReadUserById(ctx, auth.UserId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read user", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	if err := s.repoUser.UpdateUserLastSignedInAtById(ctx, user.Id, &user.Id); err != nil {
		s.log.Error(ctx, tag, "Failed to update user last signed in", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	return s.generateTokens(ctx, tag, *user)
}

func (s *baseImpl) SignInWithGoogle(ctx context.Context, sub string, email string, name string, googleRefreshToken string) (accessToken string, refreshToken string, err error) {
	const tag = path + "/SignInWithGoogle"

	googleOAuth, err := s.repoGoogleOAuth.ReadGoogleOAuthBySub(ctx, sub)
	if err == nil {
		if err := s.repoGoogleOAuth.UpdateGoogleOAuthBySub(ctx, sub, &email, &name, &googleRefreshToken, &googleOAuth.UserId); err != nil {
			s.log.Error(ctx, tag, "Failed to update google oauth", domainmodels.LogMeta{"error": err.Error()})
			return "", "", err
		}

		user, err := s.repoUser.ReadUserById(ctx, googleOAuth.UserId)
		if err != nil {
			s.log.Error(ctx, tag, "Failed to read user", domainmodels.LogMeta{"error": err.Error()})
			return "", "", err
		}

		if err := s.repoUser.UpdateUserLastSignedInAtById(ctx, user.Id, &user.Id); err != nil {
			s.log.Error(ctx, tag, "Failed to update user last signed in", domainmodels.LogMeta{"error": err.Error()})
			return "", "", err
		}

		return s.generateTokens(ctx, tag, *user)
	}
	if !errors.Is(err, domainmodels.ErrNotFound) {
		s.log.Error(ctx, tag, "Failed to read google oauth", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	defaultRole, err := s.repoRole.ReadRoleDefault(ctx)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read default role", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	var userId int64
	err = s.tx.WithTx(ctx, func(ctx context.Context) error {
		var err error
		userId, err = s.repoUser.CreateUser(ctx, defaultRole.Id, name, nil)
		if err != nil {
			return err
		}

		_, err = s.repoGoogleOAuth.CreateGoogleOAuth(ctx, userId, sub, email, name, googleRefreshToken, nil)
		if err != nil {
			return err
		}

		return nil
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to sign in with google", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	user := domainmodels.User{Id: userId, RoleId: defaultRole.Id, Name: name}
	return s.generateTokens(ctx, tag, user)
}

func (s *baseImpl) ConnectToGoogle(ctx context.Context, userId int64, sub string, email string, name string, googleRefreshToken string) (accessToken string, refreshToken string, err error) {
	const tag = path + "/ConnectToGoogle"

	user, err := s.repoUser.ReadUserById(ctx, userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read user", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	googleOAuth, err := s.repoGoogleOAuth.ReadGoogleOAuthBySub(ctx, sub)
	if err == nil {
		if googleOAuth.UserId != userId {
			return "", "", domainmodels.ErrDuplicate
		}

		if err := s.repoGoogleOAuth.UpdateGoogleOAuthBySub(ctx, sub, &email, &name, &googleRefreshToken, &userId); err != nil {
			s.log.Error(ctx, tag, "Failed to update google oauth", domainmodels.LogMeta{"error": err.Error()})
			return "", "", err
		}

		return s.generateTokens(ctx, tag, *user)
	}
	if !errors.Is(err, domainmodels.ErrNotFound) {
		s.log.Error(ctx, tag, "Failed to read google oauth", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	_, err = s.repoGoogleOAuth.CreateGoogleOAuth(ctx, userId, sub, email, name, googleRefreshToken, &userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to connect google oauth", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	return s.generateTokens(ctx, tag, *user)
}

func (s *baseImpl) RefreshToken(ctx context.Context, refreshTokenInput string) (accessToken string, newRefreshToken string, err error) {
	const tag = path + "/RefreshToken"

	claims := &domainmodels.UserRefreshTokenClaims{}
	if err := token.ValidateRefresh(refreshTokenInput, claims); err != nil {
		return "", "", domainmodels.ErrInvalidCredentials
	}

	user, err := s.repoUser.ReadUserById(ctx, claims.UserId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read user", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	if err := s.repoUser.UpdateUserLastRefreshedAtById(ctx, user.Id, &user.Id); err != nil {
		s.log.Error(ctx, tag, "Failed to update user last refreshed", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	return s.generateTokens(ctx, tag, *user)
}

func (s *baseImpl) SignOut(ctx context.Context, userId int64) (err error) {
	const tag = path + "/SignOut"

	err = s.repoUser.UpdateUserStateById(ctx, userId, domainmodels.UserStateOffline, &userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to sign out", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *baseImpl) ForgotPassword(ctx context.Context, emailOrPhone string) (err error) {
	const tag = path + "/ForgotPassword"

	_, err = s.repoAuth.ReadAuthBySignInIdentifier(ctx, emailOrPhone)
	if err != nil {
		if errors.Is(err, domainmodels.ErrNotFound) {
			return nil
		}
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *baseImpl) SetNewPassword(ctx context.Context, newPassword string) (err error) {
	const tag = path + "/SetNewPassword"

	s.log.Warn(ctx, tag, "Failed to set new password without auth context", domainmodels.LogMeta{})
	return domainmodels.ErrInvalidCredentials
}

func (s *baseImpl) SetNewPasswordWithOldPassword(ctx context.Context, authId int64, oldPassword string, newPassword string) (err error) {
	const tag = path + "/SetNewPasswordWithOldPassword"

	auth, err := s.repoAuth.ReadAuthById(ctx, authId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	if err := pwd.Compare(auth.PasswordHash, oldPassword); err != nil {
		return domainmodels.ErrInvalidCredentials
	}

	passwordHash, err := pwd.Hash(newPassword)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to hash password", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	err = s.repoAuth.UpdateAuthPasswordById(ctx, authId, passwordHash, &auth.UserId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set new password", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *baseImpl) SetNewPasswordWithResetToken(ctx context.Context, authId int64, resetToken string, newPassword string) (err error) {
	const tag = path + "/SetNewPasswordWithResetToken"

	claims := &domainmodels.UserRefreshTokenClaims{}
	if err := token.ValidateRefresh(resetToken, claims); err != nil {
		return domainmodels.ErrInvalidCredentials
	}

	auth, err := s.repoAuth.ReadAuthById(ctx, authId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return err
	}
	if auth.UserId != claims.UserId {
		return domainmodels.ErrInvalidCredentials
	}

	passwordHash, err := pwd.Hash(newPassword)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to hash password", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	err = s.repoAuth.UpdateAuthPasswordById(ctx, authId, passwordHash, &auth.UserId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set new password", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *baseImpl) SetAuthInfo(ctx context.Context, authId int64, username *string, email *string, phone *string) (err error) {
	const tag = path + "/SetAuthInfo"

	auth, err := s.repoAuth.ReadAuthById(ctx, authId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to read auth", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	err = s.repoAuth.UpdateAuthInfoById(ctx, authId, username, email, phone, &auth.UserId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set auth info", domainmodels.LogMeta{"error": err.Error()})
		return err
	}

	return nil
}

func (s *baseImpl) generateTokens(ctx context.Context, tag string, user domainmodels.User) (accessToken string, refreshToken string, err error) {
	accessToken, err = token.GenerateAccess(&domainmodels.UserAccessTokenClaims{
		UserId: user.Id,
		Name:   user.Name,
		RoleId: user.RoleId,
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to generate access token", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	refreshToken, err = token.GenerateRefresh(&domainmodels.UserRefreshTokenClaims{
		UserId: user.Id,
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to generate refresh token", domainmodels.LogMeta{"error": err.Error()})
		return "", "", err
	}

	return accessToken, refreshToken, nil
}
