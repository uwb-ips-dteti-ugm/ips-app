#pragma once

#include <cstddef>
#include <cstdint>

#include "domain/contracts/client/uwb_server.h"
#include "domain/contracts/device/control.h"
#include "domain/contracts/logger/leveled.h"
#include "domain/contracts/ranging/stateless.h"
#include "domain/contracts/wifi/connection.h"
#include "domain/usecases/task/uwb_stateless.h"

namespace application::task::uwb_stateless
{
    class BaseImpl : public usecases::task::UWBStateless
    {
    public:
        BaseImpl(
            contracts::logger::Leveled *logger,
            contracts::client::UWBServer *client,
            contracts::device::Control *device,
            contracts::ranging::Stateless *ranging,
            contracts::wifi::Connection *wifi);
        ~BaseImpl() override = default;
        BaseImpl(const BaseImpl &) = delete;
        BaseImpl &operator=(const BaseImpl &) = delete;

        bool getDeviceId(char *device_id, std::size_t length) const override;
        bool isWiFiConnected() const override;
        models::Error sendConnectRequest(const char *device_id) override;
        models::Error initiate(const models::RangingCommand &command, float *distance) override;
        models::Error listen(const models::RangingCommand &command) override;
        void restart() override;
        models::Error sendRangingResult(
            const char *device_id,
            const models::RangingResult &result) override;
        models::Error sendError(
            const char *device_id,
            const models::RangingFailure &failure) override;

    private:
        contracts::logger::Leveled *logger;
        contracts::client::UWBServer *client;
        contracts::device::Control *device;
        contracts::ranging::Stateless *ranging;
        contracts::wifi::Connection *wifi;
    };
}
