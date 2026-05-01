package domainmodels

import (
	"encoding/json"
	"time"
)

type Feature struct {
	Id          int64
	Name        string
	Description string
	Preferences json.RawMessage

	CreatedAt time.Time
	CreatedBy *int64
	UpdatedAt *time.Time
	UpdatedBy *int64
	Version   int64
}
