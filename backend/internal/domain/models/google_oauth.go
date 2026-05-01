package domainmodels

import (
	"time"
)

type GoogleOAuth struct {
	Id           int64
	UserId       int64
	Sub          string
	Email        string
	Name         string
	RefreshToken *string

	CreatedAt time.Time
	CreatedBy *int64
	UpdatedAt *time.Time
	UpdatedBy *int64
	Version   int64
}
