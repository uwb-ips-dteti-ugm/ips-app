#include "presentation/task/uwb_stateless.h"

#include <cctype>
#include <cstring>

#include <ArduinoJson.h>

#include "domain/models/error.h"
#include "domain/models/ota.h"
#include "domain/models/ranging.h"

namespace presentation::task
{
    constexpr int restartCommandCode = 1;
    constexpr int listenCommandCode = 2;
    constexpr int initiateCommandCode = 3;
    constexpr int otaUpdateCommandCode = 4;

    constexpr const char *commandTag = "task::UWBStateless::handleCommand";

    // Helpers

    bool readUint16(JsonObjectConst args, const char *key, uint16_t *value)
    {
        JsonVariantConst field = args[key];
        if (field.isNull() || !field.is<long>())
            return false;

        const long parsed = field.as<long>();
        if (parsed < 0 || parsed > 0xFFFF)
            return false;

        *value = static_cast<uint16_t>(parsed);
        return true;
    }

    bool readUint32(JsonObjectConst args, const char *key, uint32_t *value)
    {
        JsonVariantConst field = args[key];
        if (field.isNull() || !field.is<long>())
            return false;

        const long parsed = field.as<long>();
        if (parsed < 0)
            return false;

        *value = static_cast<uint32_t>(parsed);
        return true;
    }

    bool readRangingCommand(JsonObjectConst payload, models::RangingCommand *command)
    {
        return readUint16(payload, "pan_id", &command->pan_id) &&
               readUint16(payload, "listener_address", &command->listener_address) &&
               readUint16(payload, "initiator_address", &command->initiator_address) &&
               readUint32(payload, "timeout_uus", &command->timeout_uus);
    }

    bool readString(JsonObjectConst args, const char *key, char *out, std::size_t capacity)
    {
        JsonVariantConst field = args[key];
        if (field.isNull() || !field.is<const char *>())
            return false;

        const char *value = field.as<const char *>();
        const std::size_t value_length = strlen(value);
        if (value_length == 0 || value_length >= capacity)
            return false;

        strncpy(out, value, capacity - 1);
        out[capacity - 1] = '\0';
        return true;
    }

    bool isHexChecksum(const char *value)
    {
        const std::size_t value_length = strlen(value);
        if (value_length != 64)
            return false;

        for (std::size_t i = 0; i < value_length; ++i)
        {
            if (!isxdigit(static_cast<unsigned char>(value[i])))
                return false;
        }
        return true;
    }

    bool readOtaCommand(JsonObjectConst payload, models::OtaCommand *command)
    {
        if (!readString(payload, "url", command->url, sizeof(command->url)))
            return false;
        if (!readString(payload, "version", command->version, sizeof(command->version)))
            return false;
        if (!readUint32(payload, "size", &command->size) || command->size == 0)
            return false;
        if (!readString(payload, "checksum", command->checksum, sizeof(command->checksum)))
            return false;
        if (!isHexChecksum(command->checksum))
            return false;

        return true;
    }

    // Controller implementations

    UWBStateless::UWBStateless(
        usecases::task::UWBStateless *service,
        WebSocketsClient *client,
        contracts::logger::Leveled *logger,
        uint32_t check_interval_ms,
        const char *task_name,
        uint32_t stack_depth,
        UBaseType_t priority)
        : service(service),
          client(client),
          logger(logger),
          check_interval_ms(check_interval_ms == 0 ? 100 : check_interval_ms),
          task_name(task_name ? task_name : "uwb_stateless"),
          stack_depth(stack_depth),
          priority(priority),
          task_handle(nullptr),
          running(false),
          device_id{}
    {
    }

    UWBStateless::~UWBStateless()
    {
        stop();
    }

    bool UWBStateless::start()
    {
        if (task_handle != nullptr)
            return true;

        if (service == nullptr || client == nullptr || task_name.length() == 0 || stack_depth == 0)
            return false;

        if (!service->getDeviceId(device_id, sizeof(device_id)))
            return false;

        client->onEvent([this](WStype_t type, uint8_t *payload, std::size_t length)
                        { handleEvent(type, payload, length); });

        running = true;
        const BaseType_t result = xTaskCreate(
            UWBStateless::task,
            task_name.c_str(),
            stack_depth,
            this,
            priority,
            &task_handle);

        if (result != pdPASS)
        {
            client->onEvent([](WStype_t, uint8_t *, std::size_t) {});
            running = false;
            task_handle = nullptr;
            return false;
        }

        return true;
    }

    void UWBStateless::stop()
    {
        if (task_handle == nullptr)
            return;

        running = false;

        if (task_handle == xTaskGetCurrentTaskHandle())
            return;

        while (task_handle != nullptr)
            vTaskDelay(pdMS_TO_TICKS(check_interval_ms));

        if (client != nullptr)
            client->onEvent([](WStype_t, uint8_t *, std::size_t) {});
    }

    void UWBStateless::task(void *argument)
    {
        UWBStateless *self = static_cast<UWBStateless *>(argument);

        while (self->running)
        {
            if (!self->service->isWiFiConnected())
            {
                vTaskDelay(pdMS_TO_TICKS(self->check_interval_ms));
                continue;
            }

            if (!self->client->isConnected())
            {
                self->service->sendConnectRequest(self->device_id);
                vTaskDelay(pdMS_TO_TICKS(self->check_interval_ms));
                continue;
            }

            self->client->loop();
            vTaskDelay(pdMS_TO_TICKS(self->check_interval_ms));
        }

        self->client->disconnect();
        self->task_handle = nullptr;
        self->running = false;
        vTaskDelete(nullptr);
    }

    void UWBStateless::handleEvent(WStype_t type, uint8_t *payload, std::size_t length)
    {
        if (!running || type != WStype_TEXT || payload == nullptr || length == 0)
            return;

        handleCommand(payload, length);
    }

    void UWBStateless::handleCommand(const uint8_t *payload, std::size_t length)
    {
        JsonDocument document;
        DeserializationError parse_error = deserializeJson(document, payload, length);
        if (parse_error)
        {
            logger->warn(commandTag, "Rejected malformed command: invalid JSON (%s)", parse_error.c_str());
            return;
        }

        JsonVariantConst command_field = document["command"];
        JsonObjectConst payload_object = document["payload"].as<JsonObjectConst>();
        if (command_field.isNull() || !command_field.is<long>() || payload_object.isNull())
        {
            logger->warn(commandTag, "Rejected command: missing or invalid 'command'/'payload'");
            return;
        }

        const long command = command_field.as<long>();
        if (command == restartCommandCode)
        {
            service->restart();
            return;
        }

        if (command == otaUpdateCommandCode)
        {
            models::OtaCommand ota_command = {};
            if (!readOtaCommand(payload_object, &ota_command))
            {
                logger->warn(commandTag, "Rejected command %ld: invalid OTA payload fields", command);
                return;
            }

            const models::Error error = service->ota(ota_command);
            if (error == models::Error::Ok)
            {
                models::OtaResult result = {};
                result.success = true;
                strncpy(result.version, ota_command.version, sizeof(result.version) - 1);
                service->sendOtaResult(device_id, result);
                service->restart();
            }
            else
            {
                models::OtaFailure failure = {};
                strncpy(failure.version, ota_command.version, sizeof(failure.version) - 1);
                failure.message = models::errorToString(error);
                service->sendOtaError(device_id, failure);
            }
            return;
        }

        models::RangingCommand ranging_command = {};
        if (!readRangingCommand(payload_object, &ranging_command))
        {
            logger->warn(commandTag, "Rejected command %ld: invalid ranging payload fields", command);
            return;
        }

        if (command == listenCommandCode)
        {
            const models::Error error = service->listen(ranging_command);
            if (error != models::Error::Ok)
            {
                const models::RangingFailure failure = {
                    ranging_command.pan_id,
                    ranging_command.initiator_address,
                    ranging_command.listener_address,
                    models::errorToString(error)};
                service->sendError(device_id, failure);
            }
            return;
        }

        if (command == initiateCommandCode)
        {
            float distance = 0.0F;
            const models::Error error = service->initiate(ranging_command, &distance);
            if (error == models::Error::Ok)
            {
                const models::RangingResult result = {
                    ranging_command.pan_id,
                    ranging_command.initiator_address,
                    ranging_command.listener_address,
                    distance};
                service->sendRangingResult(device_id, result);
            }
            else
            {
                const models::RangingFailure failure = {
                    ranging_command.pan_id,
                    ranging_command.initiator_address,
                    ranging_command.listener_address,
                    models::errorToString(error)};
                service->sendError(device_id, failure);
            }
            return;
        }

        logger->warn(commandTag, "Rejected unknown command code %ld", command);
    }
}
