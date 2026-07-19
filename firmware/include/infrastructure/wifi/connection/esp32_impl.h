#pragma once

#include <cstddef>

#include "domain/contracts/wifi/connection.h"

namespace infrastructure::wifi::connection
{
    class ESP32Impl : public contracts::wifi::Connection
    {
    public:
        ESP32Impl();
        ~ESP32Impl() override = default;
        ESP32Impl(const ESP32Impl &) = delete;
        ESP32Impl &operator=(const ESP32Impl &) = delete;

        void connect(const char *ssid, const char *password) override;
        void disconnect() override;
        bool isConnected() const override;
        bool getDeviceId(char *device_id, std::size_t length) const override;

    private:
        mutable bool ntp_synced;
    };
}
