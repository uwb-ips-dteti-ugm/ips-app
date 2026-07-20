#include "application/task/uwb_stateless/base_impl.h"

namespace application::task::uwb_stateless
{
    constexpr const char *deviceIdTag = "task::uwb_stateless::BaseImpl::getDeviceId";
    constexpr const char *connectTag = "task::uwb_stateless::BaseImpl::sendConnectRequest";
    constexpr const char *initiateTag = "task::uwb_stateless::BaseImpl::initiate";
    constexpr const char *listenTag = "task::uwb_stateless::BaseImpl::listen";
    constexpr const char *restartTag = "task::uwb_stateless::BaseImpl::restart";
    constexpr const char *rangingResultTag = "task::uwb_stateless::BaseImpl::sendRangingResult";
    constexpr const char *errorTag = "task::uwb_stateless::BaseImpl::sendError";
    constexpr const char *otaTag = "task::uwb_stateless::BaseImpl::ota";
    constexpr const char *otaResultTag = "task::uwb_stateless::BaseImpl::sendOtaResult";
    constexpr const char *otaErrorTag = "task::uwb_stateless::BaseImpl::sendOtaError";

    // Helpers

    bool isEmpty(const char *value)
    {
        return value == nullptr || value[0] == '\0';
    }

    models::Error requireWiFi(
        contracts::logger::Leveled *logger,
        contracts::wifi::Connection *wifi,
        const char *tag)
    {
        if (!wifi->isConnected())
        {
            logger->error(tag, "WiFi is not connected");
            return models::Error::BadState;
        }

        return models::Error::Ok;
    }

    void logOperationError(
        contracts::logger::Leveled *logger,
        const char *tag,
        const char *operation,
        models::Error error)
    {
        logger->error(tag, "%s failed: %s", operation, models::errorToString(error));
    }

    // Application implementations

    BaseImpl::BaseImpl(
        contracts::logger::Leveled *logger,
        contracts::client::UWBServer *client,
        contracts::device::Control *device,
        contracts::ranging::Stateless *ranging,
        contracts::wifi::Connection *wifi,
        contracts::device::Ota *ota)
        : logger(logger),
          client(client),
          device(device),
          ranging(ranging),
          wifi(wifi),
          ota_device(ota)
    {
    }

    bool BaseImpl::getDeviceId(char *device_id, std::size_t length) const
    {
        const bool result = wifi->getDeviceId(device_id, length);
        if (!result)
        {
            logger->error(deviceIdTag, "Failed to get device ID");
            return false;
        }

        logger->info(deviceIdTag, "Device ID: %s", device_id);
        return true;
    }

    bool BaseImpl::isWiFiConnected() const
    {
        return wifi->isConnected();
    }

    models::Error BaseImpl::sendConnectRequest(const char *device_id)
    {
        if (isEmpty(device_id))
        {
            logger->error(connectTag, "Invalid argument: device_id is empty");
            return models::Error::InvalidArgument;
        }

        const models::Error wifi_error = requireWiFi(logger, wifi, connectTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        logger->info(connectTag, "Sending connect request (device_id=%s)", device_id);
        const models::Error error = client->sendConnectRequest(device_id);
        if (error != models::Error::Ok)
        {
            logOperationError(logger, connectTag, "Connect request", error);
            return error;
        }

        logger->info(connectTag, "Connect request accepted (device_id=%s)", device_id);
        return models::Error::Ok;
    }

    models::Error BaseImpl::initiate(const models::RangingCommand &command, float *distance)
    {
        if (distance == nullptr)
        {
            logger->error(initiateTag, "Invalid argument: distance is null");
            return models::Error::InvalidArgument;
        }

        const models::Error wifi_error = requireWiFi(logger, wifi, initiateTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        logger->info(
            initiateTag,
            "Initiating ranging (pan_id=0x%04X initiator=0x%04X listener=0x%04X timeout_uus=%lu)",
            static_cast<unsigned int>(command.pan_id),
            static_cast<unsigned int>(command.initiator_address),
            static_cast<unsigned int>(command.listener_address),
            static_cast<unsigned long>(command.timeout_uus));

        const models::Error error = ranging->initiate(command, distance);
        if (error != models::Error::Ok)
        {
            logOperationError(logger, initiateTag, "Ranging initiate", error);
            return error;
        }

        logger->info(
            initiateTag,
            "Ranging initiated (pan_id=0x%04X initiator=0x%04X listener=0x%04X distance=%.3f)",
            static_cast<unsigned int>(command.pan_id),
            static_cast<unsigned int>(command.initiator_address),
            static_cast<unsigned int>(command.listener_address),
            static_cast<double>(*distance));
        return models::Error::Ok;
    }

    models::Error BaseImpl::listen(const models::RangingCommand &command)
    {
        const models::Error wifi_error = requireWiFi(logger, wifi, listenTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        logger->info(
            listenTag,
            "Listening for ranging (pan_id=0x%04X listener=0x%04X initiator=0x%04X timeout_uus=%lu)",
            static_cast<unsigned int>(command.pan_id),
            static_cast<unsigned int>(command.listener_address),
            static_cast<unsigned int>(command.initiator_address),
            static_cast<unsigned long>(command.timeout_uus));

        const models::Error error = ranging->listen(command);
        if (error != models::Error::Ok)
        {
            logOperationError(logger, listenTag, "Ranging listen", error);
            return error;
        }

        logger->info(
            listenTag,
            "Ranging response sent (pan_id=0x%04X listener=0x%04X initiator=0x%04X)",
            static_cast<unsigned int>(command.pan_id),
            static_cast<unsigned int>(command.listener_address),
            static_cast<unsigned int>(command.initiator_address));
        return models::Error::Ok;
    }

    void BaseImpl::restart()
    {
        logger->info(restartTag, "Restarting device");
        device->restart();
    }

    models::Error BaseImpl::sendRangingResult(
        const char *device_id,
        const models::RangingResult &result)
    {
        if (isEmpty(device_id))
        {
            logger->error(rangingResultTag, "Invalid argument: device_id is empty");
            return models::Error::InvalidArgument;
        }

        const models::Error wifi_error = requireWiFi(logger, wifi, rangingResultTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        logger->info(
            rangingResultTag,
            "Sending ranging result (device_id=%s pan_id=0x%04X source=0x%04X destination=0x%04X distance=%.3f)",
            device_id,
            static_cast<unsigned int>(result.pan_id),
            static_cast<unsigned int>(result.source_address),
            static_cast<unsigned int>(result.destination_address),
            static_cast<double>(result.distance));

        const models::Error error = client->sendRangingResult(device_id, result);
        if (error != models::Error::Ok)
        {
            logOperationError(logger, rangingResultTag, "Send ranging result", error);
            return error;
        }

        logger->info(rangingResultTag, "Ranging result sent (device_id=%s)", device_id);
        return models::Error::Ok;
    }

    models::Error BaseImpl::sendError(
        const char *device_id,
        const models::RangingFailure &failure)
    {
        if (isEmpty(device_id))
        {
            logger->error(errorTag, "Invalid argument: device_id is empty");
            return models::Error::InvalidArgument;
        }

        if (isEmpty(failure.message))
        {
            logger->error(errorTag, "Invalid argument: message is empty");
            return models::Error::InvalidArgument;
        }

        const models::Error wifi_error = requireWiFi(logger, wifi, errorTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        logger->info(
            errorTag,
            "Sending error (device_id=%s pan_id=0x%04X source=0x%04X destination=0x%04X message=%s)",
            device_id,
            static_cast<unsigned int>(failure.pan_id),
            static_cast<unsigned int>(failure.source_address),
            static_cast<unsigned int>(failure.destination_address),
            failure.message);

        const models::Error error = client->sendError(device_id, failure);
        if (error != models::Error::Ok)
        {
            logOperationError(logger, errorTag, "Send error", error);
            return error;
        }

        logger->info(errorTag, "Error sent (device_id=%s)", device_id);
        return models::Error::Ok;
    }

    models::Error BaseImpl::ota(const models::OtaCommand &command)
    {
        const models::Error wifi_error = requireWiFi(logger, wifi, otaTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        logger->info(otaTag, "Starting OTA update (version=%s size=%lu)", command.version, static_cast<unsigned long>(command.size));

        const models::Error error = ota_device->update(command);
        if (error != models::Error::Ok)
        {
            logOperationError(logger, otaTag, "OTA update", error);
            return error;
        }

        logger->info(otaTag, "OTA update flashed successfully (version=%s)", command.version);
        return models::Error::Ok;
    }

    models::Error BaseImpl::sendOtaResult(
        const char *device_id,
        const models::OtaResult &result)
    {
        if (isEmpty(device_id))
        {
            logger->error(otaResultTag, "Invalid argument: device_id is empty");
            return models::Error::InvalidArgument;
        }

        const models::Error wifi_error = requireWiFi(logger, wifi, otaResultTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        const models::Error error = client->sendOtaResult(device_id, result);
        if (error != models::Error::Ok)
            logOperationError(logger, otaResultTag, "Send OTA result", error);

        return error;
    }

    models::Error BaseImpl::sendOtaError(
        const char *device_id,
        const models::OtaFailure &failure)
    {
        if (isEmpty(device_id))
        {
            logger->error(otaErrorTag, "Invalid argument: device_id is empty");
            return models::Error::InvalidArgument;
        }

        const models::Error wifi_error = requireWiFi(logger, wifi, otaErrorTag);
        if (wifi_error != models::Error::Ok)
            return wifi_error;

        const models::Error error = client->sendOtaError(device_id, failure);
        if (error != models::Error::Ok)
            logOperationError(logger, otaErrorTag, "Send OTA error", error);

        return error;
    }
}
