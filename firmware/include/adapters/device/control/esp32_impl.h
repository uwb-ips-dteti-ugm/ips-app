#pragma once

#include "domain/ports/driven/device/control.h"

namespace adapters::device::control
{
    class ESP32Impl : public ports::driven::device::Control
    {
    public:
        ESP32Impl();
        ~ESP32Impl() override = default;
        ESP32Impl(const ESP32Impl &) = delete;
        ESP32Impl &operator=(const ESP32Impl &) = delete;

        void restart() override;
    };
}
