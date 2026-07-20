#pragma once

#include "domain/contracts/logger/leveled.h"
#include "domain/contracts/wifi/connection.h"
#include "domain/usecases/task/wifi_connection.h"

namespace application::task::wifi_connection
{
    class BaseImpl : public usecases::task::WiFiConnection
    {
    public:
        BaseImpl(
            contracts::wifi::Connection *connection,
            contracts::logger::Leveled *logger);
        ~BaseImpl() override = default;
        BaseImpl(const BaseImpl &) = delete;
        BaseImpl &operator=(const BaseImpl &) = delete;

        void connect(const char *ssid, const char *password) override;
        void disconnect() override;
        bool isConnected() const override;

    private:
        contracts::wifi::Connection *connection;
        contracts::logger::Leveled *logger;
    };
}
