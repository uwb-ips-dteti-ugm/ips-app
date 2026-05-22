#include "adapters/device/control/esp32_impl.h"

#include <Arduino.h>

namespace adapters::device::control
{

    // Adapter implementations

    ESP32Impl::ESP32Impl() = default;

    void ESP32Impl::restart()
    {
        ESP.restart();
    }
}
