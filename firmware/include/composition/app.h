#pragma once

#include <WebSocketsClient.h>

#include "application/task/uwb_stateless/base_impl.h"
#include "application/task/wifi_connection/base_impl.h"
#include "config/config.h"
#include "infrastructure/client/uwb_server/wsclient_impl.h"
#include "infrastructure/device/control/esp32_impl.h"
#include "infrastructure/device/ota/esp32_impl.h"
#include "infrastructure/logger/leveled/serial_impl.h"
#include "infrastructure/ranging/stateless/dw3000_impl.h"
#include "infrastructure/wifi/connection/esp32_impl.h"
#include "presentation/task/uwb_stateless.h"
#include "presentation/task/wifi_connection.h"

namespace composition
{
    class App
    {
    public:
        App();
        ~App() = default;
        App(const App &) = delete;
        App &operator=(const App &) = delete;

        void setup();
        void initControllers();
        void run();

    private:
        infrastructure::logger::leveled::SerialImpl logger;
        WebSocketsClient websocket_client;
        infrastructure::device::control::ESP32Impl device_control;
        infrastructure::device::ota::ESP32Impl ota;
        infrastructure::wifi::connection::ESP32Impl wifi_connection;
        infrastructure::ranging::stateless::DW3000Impl ranging;
        infrastructure::client::uwb_server::WSClientImpl uwb_server;
        application::task::wifi_connection::BaseImpl wifi_service;
        application::task::uwb_stateless::BaseImpl uwb_service;
        presentation::task::WiFiConnection wifi_controller;
        presentation::task::UWBStateless uwb_controller;
    };
}
