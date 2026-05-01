package domainmodels

type LogLevel string

const (
	LogLevelError LogLevel = "error"
	LogLevelWarn  LogLevel = "warn"
	LogLevelInfo  LogLevel = "info"
	LogLevelDebug LogLevel = "debug"
)

func (l LogLevel) IsValid() bool {
	switch l {
	case
		LogLevelError,
		LogLevelWarn,
		LogLevelInfo,
		LogLevelDebug:
		return true
	}
	return false
}

func (l LogLevel) Order() int {
	switch l {
	case LogLevelError:
		return 0
	case LogLevelWarn:
		return 1
	case LogLevelInfo:
		return 2
	case LogLevelDebug:
		return 3
	}
	return -1
}

type LogMeta map[string]any
