#include "infrastructure/wifi/connection/esp32_impl.h"

#include <cstdio>

#include <Arduino.h>
#include <WiFi.h>
#include <esp_mac.h>

namespace infrastructure::wifi::connection
{
    constexpr const char *connectTag = "wifi::connection::ESP32Impl::isConnected";

    // Adapter implementations

    ESP32Impl::ESP32Impl(contracts::logger::Leveled *logger)
        : logger(logger), connection_logged(false)
    {
        // The ESP32 Arduino WiFi library defaults to WiFi.persistent(true), so esp_wifi
        // auto-reconnects at boot using whatever SSID/password was last saved to NVS by a
        // previous flash/test, independent of the compiled-in config::wifiSsid/wifiPassword.
        // If that stale network is reachable, isConnected() reports true before the WiFi task
        // ever calls connect() with the correct credentials, so the device silently stays on
        // the old network. Disable persistence and clear any stale auto-join here, before
        // App::initControllers() starts the WiFi task's connectivity checks, so the compiled
        // .env SSID always wins.
        WiFi.mode(WIFI_STA);
        WiFi.persistent(false);
        WiFi.disconnect(true);
    }

    void ESP32Impl::connect(const char *ssid, const char *password)
    {
        WiFi.mode(WIFI_STA);
        WiFi.begin(ssid, password);
    }

    void ESP32Impl::disconnect()
    {
        WiFi.disconnect(true);
        connection_logged = false;
    }

    bool ESP32Impl::isConnected() const
    {
        const bool connected = WiFi.status() == WL_CONNECTED;

        if (connected && !connection_logged)
        {
            logger->info(
                connectTag,
                "WiFi link up (ip=%s gateway=%s subnet=%s rssi=%d dBm)",
                WiFi.localIP().toString().c_str(),
                WiFi.gatewayIP().toString().c_str(),
                WiFi.subnetMask().toString().c_str(),
                static_cast<int>(WiFi.RSSI()));
            configTime(0, 0, "pool.ntp.org");
            connection_logged = true;
        }
        else if (!connected)
        {
            connection_logged = false;
        }

        return connected;
    }

    bool ESP32Impl::getDeviceId(char *device_id, std::size_t length) const
    {
        if (device_id == nullptr || length < 13)
            return false;

        uint8_t mac[6] = {};
        if (esp_efuse_mac_get_default(mac) != ESP_OK)
            return false;

        const int written = snprintf(
            device_id,
            length,
            "%02X%02X%02X%02X%02X%02X",
            static_cast<unsigned int>(mac[0]),
            static_cast<unsigned int>(mac[1]),
            static_cast<unsigned int>(mac[2]),
            static_cast<unsigned int>(mac[3]),
            static_cast<unsigned int>(mac[4]),
            static_cast<unsigned int>(mac[5]));

        return written == 12;
    }
}
