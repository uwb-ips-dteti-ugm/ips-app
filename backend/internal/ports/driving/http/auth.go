package portsdrivinghttp

import "context"

type Auth interface {
	SignUp(ctx context.Context, name string, username string, email *string, phone *string, password string) (accessToken string, refreshToken string, err error)
	SignIn(ctx context.Context, signInIdentifier string, password string) (accessToken string, refreshToken string, err error)
	SignInWithGoogle(ctx context.Context, sub string, email string, name string, googleRefreshToken string) (accessToken string, refreshToken string, err error)
	ConnectToGoogle(ctx context.Context, userId int64, sub string, email string, name string, googleRefreshToken string) (accessToken string, refreshToken string, err error)
	RefreshToken(ctx context.Context, refreshToken string) (accessToken string, newRefreshToken string, err error)
	SignOut(ctx context.Context, userId int64) (err error)
	ForgotPassword(ctx context.Context, emailOrPhone string) (err error)
	SetNewPassword(ctx context.Context, newPassword string) (err error)
	SetNewPasswordWithOldPassword(ctx context.Context, authId int64, oldPassword string, newPassword string) (err error)
	SetNewPasswordWithResetToken(ctx context.Context, authId int64, resetToken string, newPassword string) (err error)
	SetAuthInfo(ctx context.Context, authId int64, username *string, email *string, phone *string) (err error)
}
