#pragma once

#include <cstddef>
#include <cstdint>

#include "domain/models/error.h"
#include "domain/models/ranging.h"

namespace usecases::task
{
    class UWBStateless
    {
    public:
        virtual ~UWBStateless() = default;
        virtual bool getDeviceId(char *device_id, std::size_t length) const = 0;
        virtual bool isWiFiConnected() const = 0;
        virtual models::Error sendConnectRequest(const char *device_id) = 0;
        virtual models::Error initiate(const models::RangingCommand &command, float *distance) = 0;
        virtual models::Error listen(const models::RangingCommand &command) = 0;
        virtual void restart() = 0;
        virtual models::Error sendRangingResult(
            const char *device_id,
            const models::RangingResult &result) = 0;
        virtual models::Error sendError(
            const char *device_id,
            const models::RangingFailure &failure) = 0;
    };
}
