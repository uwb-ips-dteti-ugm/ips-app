package domainmodels

import "time"

type Auth struct {
	Id           int64
	UserId       int64
	Username     string
	Email        *string
	Phone        *string
	PasswordHash string

	CreatedAt time.Time
	CreatedBy *int64
	UpdatedAt *time.Time
	UpdatedBy *int64
	Version   int64
}
