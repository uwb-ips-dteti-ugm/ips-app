package domainmodels

import (
	"encoding/json"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type UserState string

const (
	UserStateOnline  UserState = "online"
	UserStateOffline UserState = "offline"
	UserStateAway    UserState = "away"
	UserStateDnd     UserState = "dnd"
)

type UserStatus string

const (
	UserStatusActive    UserStatus = "active"
	UserStatusSuspended UserStatus = "suspended"
	UserStatusBanned    UserStatus = "banned"
)

type User struct {
	Id              int64
	RoleId          int64
	Name            string
	Bio             string
	State           UserState
	Status          UserStatus
	Preferences     json.RawMessage
	LastSignedInAt  *time.Time
	LastRefreshedAt *time.Time
	LastActivityAt  *time.Time

	CreatedAt time.Time
	CreatedBy *int64
	UpdatedAt *time.Time
	UpdatedBy *int64
	Version   int64
}

type UserAccessTokenClaims struct {
	UserId int64  `json:"user_id"`
	Name   string `json:"name"`
	RoleId int64  `json:"role_id"`
	jwt.RegisteredClaims
}

type UserRefreshTokenClaims struct {
	UserId int64 `json:"user_id"`
	jwt.RegisteredClaims
}
