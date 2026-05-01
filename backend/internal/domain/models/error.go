package domainmodels

import "errors"

var (
	ErrQueryBuilder       = errors.New("Query building failed")
	ErrNotFound           = errors.New("Data not found")
	ErrDuplicate          = errors.New("Duplicate entry")
	ErrInvalidCredentials = errors.New("Invalid credentials")
	ErrUsernameTaken      = errors.New("Username is already taken")
	ErrEmailTaken         = errors.New("Email is already taken")
	ErrPhoneTaken         = errors.New("Phone number is already taken")
)
