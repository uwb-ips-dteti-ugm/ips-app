#pragma once

#include <cstdint>
#include <Arduino.h>
#include "domain/contracts/logger/leveled.h"

namespace infrastructure::logger::leveled
{
    enum LogLevel : uint8_t
    {
        LOG_LEVEL_NONE,
        LOG_LEVEL_ERROR,
        LOG_LEVEL_WARN,
        LOG_LEVEL_INFO,
        LOG_LEVEL_DEBUG
    };

    class SerialImpl : public contracts::logger::Leveled
    {
    public:
        SerialImpl(HardwareSerial *serial, LogLevel level);
        ~SerialImpl() override = default;
        SerialImpl(const SerialImpl &) = delete;
        SerialImpl &operator=(const SerialImpl &) = delete;

        void error(const char *tag, const char *message, ...) override;
        void warn(const char *tag, const char *message, ...) override;
        void info(const char *tag, const char *message, ...) override;
        void debug(const char *tag, const char *message, ...) override;

    private:
        static void log(HardwareSerial *serial, const char *level, const char *tag, const char *message, va_list args);

        HardwareSerial *serial;
        LogLevel level;
    };
}
