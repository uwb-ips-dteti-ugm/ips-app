package adaptersdrivenrepositoryrolepermission

import (
	"github.com/Masterminds/squirrel"
)

func (s *postgresImpl) queryCreateRolePermission(
	roleId int64,
	permissionId int64,
	createdBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Insert("role_permission").
		Columns(
			"role_id",
			"permission_id",
			"created_by",
		).
		Values(
			roleId,
			permissionId,
			createdBy,
		).
		Suffix("RETURNING role_id").
		ToSql()
}

func (s *postgresImpl) queryReadPermissionsByRoleId(
	roleId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"name",
			"description",
			"preferences",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("role_permission rp JOIN permissions p ON rp.permission_id = p.id").
		Where(squirrel.Eq{"rp.role_id": roleId}).
		ToSql()
}

func (s *postgresImpl) queryReadRolesByPermissionId(
	permissionId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Select(
			"id",
			"name",
			"description",
			"preferences",
			"created_at",
			"created_by",
			"updated_at",
			"updated_by",
			"version",
		).
		From("role_permission rp JOIN roles r ON rp.role_id = r.id").
		Where(squirrel.Eq{"rp.permission_id": permissionId}).
		ToSql()
}

func (s *postgresImpl) queryDeleteRolePermissionByRoleIdAndPermissionId(
	roleId int64,
	permissionId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("role_permission").
		Where(squirrel.Eq{
			"role_id":       roleId,
			"permission_id": permissionId,
		}).
		ToSql()
}

func (s *postgresImpl) queryDeleteRolePermissionsByRoleId(
	roleId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("role_permission").
		Where(squirrel.Eq{"role_id": roleId}).
		ToSql()
}

func (s *postgresImpl) queryDeleteRolePermissionsByPermissionId(
	permissionId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("role_permission").
		Where(squirrel.Eq{"permission_id": permissionId}).
		ToSql()
}
