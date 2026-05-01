package domainmodels

type Environment string

const (
	EnvironmentDevelopment Environment = "development"
	EnvironmentStaging     Environment = "staging"
	EnvironmentProduction  Environment = "production"
)

func (e Environment) IsValid() bool {
	switch e {
	case
		EnvironmentDevelopment,
		EnvironmentStaging,
		EnvironmentProduction:
		return true
	}
	return false
}
