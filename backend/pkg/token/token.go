package token

import (
	"errors"
	"fmt"
	"reflect"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

var (
	ErrExpired = errors.New("token is expired")
	ErrInvalid = errors.New("token is invalid")
)

var cfg struct {
	issuer     string
	accessKey  []byte
	accessExp  time.Duration
	refreshKey []byte
	refreshExp time.Duration
}

func Config(issuer, accessKey, refreshKey string, accessExp, refreshExp time.Duration) {
	cfg.issuer = issuer
	cfg.accessKey = []byte(accessKey)
	cfg.accessExp = accessExp
	cfg.refreshKey = []byte(refreshKey)
	cfg.refreshExp = refreshExp
}

func GenerateAccess(claims jwt.Claims) (string, error) {
	return generate(claims, cfg.accessKey, cfg.accessExp)
}

func ValidateAccess(tokenString string, claims jwt.Claims) error {
	return validate(tokenString, claims, cfg.accessKey)
}

func GenerateRefresh(claims jwt.Claims) (string, error) {
	return generate(claims, cfg.refreshKey, cfg.refreshExp)
}

func ValidateRefresh(tokenString string, claims jwt.Claims) error {
	return validate(tokenString, claims, cfg.refreshKey)
}

func generate(claims jwt.Claims, key []byte, expiration time.Duration) (string, error) {
	now := time.Now()
	exp := jwt.NewNumericDate(now.Add(expiration))
	iat := jwt.NewNumericDate(now)

	switch c := claims.(type) {
	case jwt.MapClaims:
		c["iss"] = cfg.issuer
		c["exp"] = exp
		c["iat"] = iat
	case *jwt.RegisteredClaims:
		c.Issuer = cfg.issuer
		c.ExpiresAt = exp
		c.IssuedAt = iat
	default:
		v := reflect.ValueOf(claims)
		if v.Kind() == reflect.Ptr {
			v = v.Elem()
		}

		if v.Kind() != reflect.Struct {
			return "", fmt.Errorf("unsupported claims type: must be jwt.MapClaims, *jwt.RegisteredClaims, or a struct embedding jwt.RegisteredClaims")
		}

		regClaimsField := v.FieldByName("RegisteredClaims")
		if !regClaimsField.IsValid() || !regClaimsField.CanSet() {
			return "", fmt.Errorf("invalid claims struct: must embed jwt.RegisteredClaims and be a pointer")
		}

		newRegClaims := jwt.RegisteredClaims{
			Issuer:    cfg.issuer,
			ExpiresAt: exp,
			IssuedAt:  iat,
		}
		regClaimsField.Set(reflect.ValueOf(newRegClaims))
	}

	t := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)

	tokenString, err := t.SignedString(key)
	if err != nil {
		return "", fmt.Errorf("failed to sign token: %w", err)
	}

	return tokenString, nil
}

func validate(tokenString string, claims jwt.Claims, key []byte) error {
	if claims == nil {
		return fmt.Errorf("claims parameter cannot be nil: pass a non-nil pointer to your claims struct (e.g., &MyClaims{} or jwt.MapClaims{})")
	}

	t, err := jwt.ParseWithClaims(
		tokenString,
		claims,
		func(t *jwt.Token) (any, error) {
			if _, ok := t.Method.(*jwt.SigningMethodHMAC); !ok {
				return nil, fmt.Errorf("unexpected signing method: %v", t.Header["alg"])
			}
			return key, nil
		})
	if err != nil {
		if errors.Is(err, jwt.ErrTokenExpired) {
			return ErrExpired
		}
		return fmt.Errorf("failed to parse token: %w", err)
	}
	if !t.Valid {
		return ErrInvalid
	}

	return nil
}
