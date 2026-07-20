#pragma once

#include <cstdint>

#include <Arduino.h>
#include <WebSocketsClient.h>

#include "domain/contracts/client/uwb_server.h"
#include "domain/contracts/logger/leveled.h"

namespace infrastructure::client::uwb_server
{
    class WSClientImpl : public contracts::client::UWBServer
    {
    public:
        WSClientImpl(
            contracts::logger::Leveled *logger,
            WebSocketsClient *client,
            const char *scheme,
            const char *host,
            uint16_t port,
            const char *path,
            uint32_t connect_timeout_ms = 5000);
        ~WSClientImpl() override = default;
        WSClientImpl(const WSClientImpl &) = delete;
        WSClientImpl &operator=(const WSClientImpl &) = delete;

        models::Error sendConnectRequest(const char *device_id) override;
        models::Error sendRangingResult(
            const char *device_id,
            const models::RangingResult &result) override;
        models::Error sendError(
            const char *device_id,
            const models::RangingFailure &failure) override;
        models::Error sendOtaResult(
            const char *device_id,
            const models::OtaResult &result) override;
        models::Error sendOtaError(
            const char *device_id,
            const models::OtaFailure &failure) override;

    private:
        WebSocketsClient *client;
        String scheme;
        String host;
        uint16_t port;
        String path;
        uint32_t connect_timeout_ms;
        contracts::logger::Leveled *logger;
    };
}
