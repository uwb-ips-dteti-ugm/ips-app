package domainserviceshttpfeature

import (
	"context"
	"encoding/json"

	domainmodels "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/domain/models"
	portsdrivenlogging "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/logging"
	portsdrivenrepository "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driven/repository"
	portsdrivinghttp "github.com/uwb-ips-dteti-ugm/ips-app/backend/internal/ports/driving/http"
	"github.com/uwb-ips-dteti-ugm/ips-app/backend/pkg/pgxdt"
)

type baseImpl struct {
	tx                    pgxdt.Transactor
	log                   portsdrivenlogging.Generic
	repoFeature           portsdrivenrepository.Feature
	repoPermission        portsdrivenrepository.Permission
	repoFeaturePermission portsdrivenrepository.FeaturePermission
	repoRolePermission    portsdrivenrepository.RolePermission
	repoUser              portsdrivenrepository.User
}

func NewBaseImpl(
	tx pgxdt.Transactor,
	log portsdrivenlogging.Generic,
	repoFeature portsdrivenrepository.Feature,
	repoPermission portsdrivenrepository.Permission,
	repoFeaturePermission portsdrivenrepository.FeaturePermission,
	repoRolePermission portsdrivenrepository.RolePermission,
	repoUser portsdrivenrepository.User,
) portsdrivinghttp.Feature {
	return &baseImpl{
		tx:                    tx,
		log:                   log,
		repoFeature:           repoFeature,
		repoPermission:        repoPermission,
		repoFeaturePermission: repoFeaturePermission,
		repoRolePermission:    repoRolePermission,
		repoUser:              repoUser,
	}
}

func (s *baseImpl) AddFeature(ctx context.Context, name string, description string) (feature domainmodels.Feature, err error) {
	const tag = path + "/AddFeature"

	id, err := s.repoFeature.CreateFeature(ctx, name, description, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to add feature", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Feature{}, err
	}

	return s.GetFeature(ctx, id)
}

func (s *baseImpl) GetFeature(ctx context.Context, featureId int64) (feature domainmodels.Feature, err error) {
	const tag = path + "/GetFeature"

	item, err := s.repoFeature.ReadFeatureById(ctx, featureId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get feature", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Feature{}, err
	}

	return *item, nil
}

func (s *baseImpl) GetFeatures(ctx context.Context, page int, limit int, cursorId *int64, search *string) (features []domainmodels.Feature, total int, err error) {
	const tag = path + "/GetFeatures"

	features, total, err = s.repoFeature.ReadFeaturesByPagination(ctx, page, limit, cursorId, search)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get features", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return features, total, nil
}

func (s *baseImpl) SetFeature(ctx context.Context, featureId int64, name *string, description *string) (feature domainmodels.Feature, err error) {
	const tag = path + "/SetFeature"

	err = s.repoFeature.UpdateFeatureById(ctx, featureId, name, description, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set feature", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Feature{}, err
	}

	return s.GetFeature(ctx, featureId)
}

func (s *baseImpl) SetFeaturePreferences(ctx context.Context, featureId int64, preferences []byte) (feature domainmodels.Feature, err error) {
	const tag = path + "/SetFeaturePreferences"

	err = s.repoFeature.UpdateFeaturePreferencesById(ctx, featureId, json.RawMessage(preferences), nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set feature preferences", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Feature{}, err
	}

	return s.GetFeature(ctx, featureId)
}

func (s *baseImpl) RemoveFeature(ctx context.Context, featureId int64) (message string, err error) {
	const tag = path + "/RemoveFeature"

	err = s.repoFeature.DeleteFeatureById(ctx, featureId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to remove feature", domainmodels.LogMeta{"error": err.Error()})
		return "", err
	}

	return "Feature removed successfully", nil
}

func (s *baseImpl) AddPermissionsToFeature(ctx context.Context, featureId int64, permissionIds []int64) (feature domainmodels.Feature, err error) {
	const tag = path + "/AddPermissionsToFeature"

	err = s.tx.WithTx(ctx, func(ctx context.Context) error {
		for _, permissionId := range permissionIds {
			if _, err := s.repoFeaturePermission.CreateFeaturePermission(ctx, featureId, permissionId, nil); err != nil {
				return err
			}
		}
		return nil
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to add permissions to feature", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Feature{}, err
	}

	return s.GetFeature(ctx, featureId)
}

func (s *baseImpl) RemovePermissionsFromFeature(ctx context.Context, featureId int64, permissionIds []int64) (feature domainmodels.Feature, err error) {
	const tag = path + "/RemovePermissionsFromFeature"

	err = s.tx.WithTx(ctx, func(ctx context.Context) error {
		for _, permissionId := range permissionIds {
			if err := s.repoFeaturePermission.DeleteFeaturePermissionByFeatureIdAndPermissionId(ctx, featureId, permissionId); err != nil {
				return err
			}
		}
		return nil
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to remove permissions from feature", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Feature{}, err
	}

	return s.GetFeature(ctx, featureId)
}

func (s *baseImpl) GetFeaturePermissions(ctx context.Context, featureId int64) (permissions []domainmodels.Permission, err error) {
	const tag = path + "/GetFeaturePermissions"

	permissions, err = s.repoFeaturePermission.ReadPermissionsByFeatureId(ctx, featureId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get feature permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return permissions, nil
}

func (s *baseImpl) GetAccessibleFeatures(ctx context.Context, userId int64) (features []domainmodels.Feature, err error) {
	const tag = path + "/GetAccessibleFeatures"

	user, err := s.repoUser.ReadUserById(ctx, userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get user", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	rolePermissions, err := s.repoRolePermission.ReadPermissionsByRoleId(ctx, user.RoleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get role permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	rolePermissionIds := make(map[int64]struct{}, len(rolePermissions))
	for _, permission := range rolePermissions {
		rolePermissionIds[permission.Id] = struct{}{}
	}

	_, total, err := s.repoFeature.ReadFeaturesByPagination(ctx, 0, 1, nil, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to count features", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}
	if total == 0 {
		return []domainmodels.Feature{}, nil
	}

	allFeatures, _, err := s.repoFeature.ReadFeaturesByPagination(ctx, 0, total, nil, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get features", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	features = make([]domainmodels.Feature, 0, len(allFeatures))
	for _, feature := range allFeatures {
		canAccess, err := s.canRoleAccessFeature(ctx, rolePermissionIds, feature.Id)
		if err != nil {
			s.log.Error(ctx, tag, "Failed to check feature access", domainmodels.LogMeta{"error": err.Error()})
			return nil, err
		}
		if canAccess {
			features = append(features, feature)
		}
	}

	return features, nil
}

func (s *baseImpl) CanAccessFeature(ctx context.Context, userId int64, featureId int64) (canAccess bool, err error) {
	const tag = path + "/CanAccessFeature"

	if _, err := s.repoFeature.ReadFeatureById(ctx, featureId); err != nil {
		s.log.Error(ctx, tag, "Failed to get feature", domainmodels.LogMeta{"error": err.Error()})
		return false, err
	}

	user, err := s.repoUser.ReadUserById(ctx, userId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get user", domainmodels.LogMeta{"error": err.Error()})
		return false, err
	}

	rolePermissions, err := s.repoRolePermission.ReadPermissionsByRoleId(ctx, user.RoleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get role permissions", domainmodels.LogMeta{"error": err.Error()})
		return false, err
	}

	rolePermissionIds := make(map[int64]struct{}, len(rolePermissions))
	for _, permission := range rolePermissions {
		rolePermissionIds[permission.Id] = struct{}{}
	}

	return s.canRoleAccessFeature(ctx, rolePermissionIds, featureId)
}

func (s *baseImpl) canRoleAccessFeature(ctx context.Context, rolePermissionIds map[int64]struct{}, featureId int64) (bool, error) {
	requiredPermissions, err := s.repoFeaturePermission.ReadPermissionsByFeatureId(ctx, featureId)
	if err != nil {
		return false, err
	}

	for _, permission := range requiredPermissions {
		if _, ok := rolePermissionIds[permission.Id]; !ok {
			return false, nil
		}
	}

	return true, nil
}
