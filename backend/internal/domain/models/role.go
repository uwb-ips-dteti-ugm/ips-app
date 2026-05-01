package domainmodels

import (
	"encoding/json"
	"time"
)

type Role struct {
	Id          int64
	Name        string
	Description string
	Preferences json.RawMessage
	IsDefault   bool

	CreatedAt time.Time
	CreatedBy *int64
	UpdatedAt *time.Time
	UpdatedBy *int64
	Version   int64
}
