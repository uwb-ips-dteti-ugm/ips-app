#pragma once

#include "domain/models/error.h"
#include "domain/models/ota.h"
#include "domain/models/ranging.h"

namespace contracts::client
{
    class UWBServer
    {
    public:
        virtual ~UWBServer() = default;
        virtual models::Error sendConnectRequest(const char *device_id) = 0;
        virtual models::Error sendRangingResult(
            const char *device_id,
            const models::RangingResult &result) = 0;
        virtual models::Error sendError(
            const char *device_id,
            const models::RangingFailure &failure) = 0;
        virtual models::Error sendOtaResult(
            const char *device_id,
            const models::OtaResult &result) = 0;
        virtual models::Error sendOtaError(
            const char *device_id,
            const models::OtaFailure &failure) = 0;
    };
}
