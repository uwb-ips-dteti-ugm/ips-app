#pragma once

#include "domain/contracts/device/control.h"

namespace infrastructure::device::control
{
    class ESP32Impl : public contracts::device::Control
    {
    public:
        ESP32Impl();
        ~ESP32Impl() override = default;
        ESP32Impl(const ESP32Impl &) = delete;
        ESP32Impl &operator=(const ESP32Impl &) = delete;

        void restart() override;
    };
}
