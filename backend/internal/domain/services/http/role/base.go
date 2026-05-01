package domainserviceshttprole

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
	tx                 pgxdt.Transactor
	log                portsdrivenlogging.Generic
	repoRole           portsdrivenrepository.Role
	repoPermission     portsdrivenrepository.Permission
	repoRolePermission portsdrivenrepository.RolePermission
}

func NewBaseImpl(
	tx pgxdt.Transactor,
	log portsdrivenlogging.Generic,
	repoRole portsdrivenrepository.Role,
	repoPermission portsdrivenrepository.Permission,
	repoRolePermission portsdrivenrepository.RolePermission,
) portsdrivinghttp.Role {
	return &baseImpl{
		tx:                 tx,
		log:                log,
		repoRole:           repoRole,
		repoPermission:     repoPermission,
		repoRolePermission: repoRolePermission,
	}
}

func (s *baseImpl) AddRole(ctx context.Context, name string, description string) (role domainmodels.Role, err error) {
	const tag = path + "/AddRole"

	id, err := s.repoRole.CreateRole(ctx, name, description, false, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to add role", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Role{}, err
	}

	return s.GetRole(ctx, id)
}

func (s *baseImpl) GetRole(ctx context.Context, roleId int64) (role domainmodels.Role, err error) {
	const tag = path + "/GetRole"

	item, err := s.repoRole.ReadRoleById(ctx, roleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get role", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Role{}, err
	}

	return *item, nil
}

func (s *baseImpl) GetRoles(ctx context.Context, page int, limit int, cursorId *int64, search *string) (roles []domainmodels.Role, total int, err error) {
	const tag = path + "/GetRoles"

	roles, total, err = s.repoRole.ReadRolesByPagination(ctx, page, limit, cursorId, search)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get roles", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return roles, total, nil
}

func (s *baseImpl) SetRole(ctx context.Context, roleId int64, name *string, description *string) (role domainmodels.Role, err error) {
	const tag = path + "/SetRole"

	err = s.repoRole.UpdateRoleById(ctx, roleId, name, description, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set role", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Role{}, err
	}

	return s.GetRole(ctx, roleId)
}

func (s *baseImpl) SetRolePreferences(ctx context.Context, roleId int64, preferences []byte) (role domainmodels.Role, err error) {
	const tag = path + "/SetRolePreferences"

	err = s.repoRole.UpdateRolePreferencesById(ctx, roleId, json.RawMessage(preferences), nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set role preferences", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Role{}, err
	}

	return s.GetRole(ctx, roleId)
}

func (s *baseImpl) RemoveRole(ctx context.Context, roleId int64) (message string, err error) {
	const tag = path + "/RemoveRole"

	err = s.repoRole.DeleteRoleById(ctx, roleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to remove role", domainmodels.LogMeta{"error": err.Error()})
		return "", err
	}

	return "Role removed successfully", nil
}

func (s *baseImpl) AddPermission(ctx context.Context, name string, description string) (permission domainmodels.Permission, err error) {
	const tag = path + "/AddPermission"

	id, err := s.repoPermission.CreatePermission(ctx, name, description, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to add permission", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Permission{}, err
	}

	return s.GetPermission(ctx, id)
}

func (s *baseImpl) GetPermission(ctx context.Context, permissionId int64) (permission domainmodels.Permission, err error) {
	const tag = path + "/GetPermission"

	item, err := s.repoPermission.ReadPermissionById(ctx, permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get permission", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Permission{}, err
	}

	return *item, nil
}

func (s *baseImpl) GetPermissions(ctx context.Context, page int, limit int, cursorId *int64, search *string) (permissions []domainmodels.Permission, total int, err error) {
	const tag = path + "/GetPermissions"

	permissions, total, err = s.repoPermission.ReadPermissionsByPagination(ctx, page, limit, cursorId, search)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, 0, err
	}

	return permissions, total, nil
}

func (s *baseImpl) SetPermission(ctx context.Context, permissionId int64, name *string, description *string) (permission domainmodels.Permission, err error) {
	const tag = path + "/SetPermission"

	err = s.repoPermission.UpdatePermissionById(ctx, permissionId, name, description, nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set permission", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Permission{}, err
	}

	return s.GetPermission(ctx, permissionId)
}

func (s *baseImpl) SetPermissionPreferences(ctx context.Context, permissionId int64, preferences []byte) (permission domainmodels.Permission, err error) {
	const tag = path + "/SetPermissionPreferences"

	err = s.repoPermission.UpdatePermissionPreferencesById(ctx, permissionId, json.RawMessage(preferences), nil)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to set permission preferences", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Permission{}, err
	}

	return s.GetPermission(ctx, permissionId)
}

func (s *baseImpl) RemovePermission(ctx context.Context, permissionId int64) (message string, err error) {
	const tag = path + "/RemovePermission"

	err = s.repoPermission.DeletePermissionById(ctx, permissionId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to remove permission", domainmodels.LogMeta{"error": err.Error()})
		return "", err
	}

	return "Permission removed successfully", nil
}

func (s *baseImpl) AddPermissionsToRole(ctx context.Context, roleId int64, permissionIds []int64) (role domainmodels.Role, err error) {
	const tag = path + "/AddPermissionsToRole"

	err = s.tx.WithTx(ctx, func(ctx context.Context) error {
		for _, permissionId := range permissionIds {
			if _, err := s.repoRolePermission.CreateRolePermission(ctx, roleId, permissionId, nil); err != nil {
				return err
			}
		}
		return nil
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to add permissions to role", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Role{}, err
	}

	return s.GetRole(ctx, roleId)
}

func (s *baseImpl) RemovePermissionsFromRole(ctx context.Context, roleId int64, permissionIds []int64) (role domainmodels.Role, err error) {
	const tag = path + "/RemovePermissionsFromRole"

	err = s.tx.WithTx(ctx, func(ctx context.Context) error {
		for _, permissionId := range permissionIds {
			if err := s.repoRolePermission.DeleteRolePermissionByRoleIdAndPermissionId(ctx, roleId, permissionId); err != nil {
				return err
			}
		}
		return nil
	})
	if err != nil {
		s.log.Error(ctx, tag, "Failed to remove permissions from role", domainmodels.LogMeta{"error": err.Error()})
		return domainmodels.Role{}, err
	}

	return s.GetRole(ctx, roleId)
}

func (s *baseImpl) GetRolePermissions(ctx context.Context, roleId int64) (permissions []domainmodels.Permission, err error) {
	const tag = path + "/GetRolePermissions"

	permissions, err = s.repoRolePermission.ReadPermissionsByRoleId(ctx, roleId)
	if err != nil {
		s.log.Error(ctx, tag, "Failed to get role permissions", domainmodels.LogMeta{"error": err.Error()})
		return nil, err
	}

	return permissions, nil
}
