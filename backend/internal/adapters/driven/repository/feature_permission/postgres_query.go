package adaptersdrivenrepositoryfeaturepermission

import (
	"github.com/Masterminds/squirrel"
)

func (s *postgresImpl) queryCreateFeaturePermission(
	featureId int64,
	permissionId int64,
	createdBy *int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Insert("feature_permission").
		Columns(
			"feature_id",
			"permission_id",
			"created_by",
		).
		Values(
			featureId,
			permissionId,
			createdBy,
		).
		Suffix("RETURNING feature_id").
		ToSql()
}

func (s *postgresImpl) queryReadPermissionsByFeatureId(
	featureId int64,
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
		From("feature_permission fp JOIN permissions p ON fp.permission_id = p.id").
		Where(squirrel.Eq{"fp.feature_id": featureId}).
		ToSql()
}

func (s *postgresImpl) queryReadFeaturesByPermissionId(
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
		From("feature_permission fp JOIN features f ON fp.feature_id = f.id").
		Where(squirrel.Eq{"fp.permission_id": permissionId}).
		ToSql()
}

func (s *postgresImpl) queryDeleteFeaturePermissionByFeatureIdAndPermissionId(
	featureId int64,
	permissionId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("feature_permission").
		Where(squirrel.Eq{
			"feature_id":    featureId,
			"permission_id": permissionId,
		}).
		ToSql()
}

func (s *postgresImpl) queryDeleteFeaturePermissionsByFeatureId(
	featureId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("feature_permission").
		Where(squirrel.Eq{"feature_id": featureId}).
		ToSql()
}

func (s *postgresImpl) queryDeleteFeaturePermissionsByPermissionId(
	permissionId int64,
) (query string, args []any, err error) {
	return s.sqrQuestion.
		Delete("feature_permission").
		Where(squirrel.Eq{"permission_id": permissionId}).
		ToSql()
}
