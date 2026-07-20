#pragma once

#include "domain/contracts/device/ota.h"
#include "domain/contracts/logger/leveled.h"

namespace infrastructure::device::ota
{
    class ESP32Impl : public contracts::device::Ota
    {
    public:
        explicit ESP32Impl(contracts::logger::Leveled *logger);
        ~ESP32Impl() override = default;
        ESP32Impl(const ESP32Impl &) = delete;
        ESP32Impl &operator=(const ESP32Impl &) = delete;

        models::Error update(const models::OtaCommand &command) override;

    private:
        contracts::logger::Leveled *logger;
    };
}
