#include "infrastructure/device/ota/esp32_impl.h"

#include <cstdio>
#include <cstring>

#include <HTTPClient.h>
#include <Update.h>
#include <WiFiClient.h>
#include <WiFiClientSecure.h>
#include <mbedtls/sha256.h>

#include "config/config.h"

namespace infrastructure::device::ota
{
    constexpr const char *updateTag = "device::ota::ESP32Impl::update";

    // Helpers

    bool isEmpty(const char *value)
    {
        return value == nullptr || value[0] == '\0';
    }

    bool isHttpsUrl(const char *url)
    {
        return strncmp(url, "https://", 8) == 0;
    }

    void hexEncode(const uint8_t *digest, std::size_t length, char *out)
    {
        static const char hex[] = "0123456789abcdef";
        for (std::size_t i = 0; i < length; ++i)
        {
            out[i * 2] = hex[(digest[i] >> 4) & 0x0F];
            out[i * 2 + 1] = hex[digest[i] & 0x0F];
        }
        out[length * 2] = '\0';
    }

    bool equalsIgnoreCase(const char *a, const char *b)
    {
        while (*a != '\0' && *b != '\0')
        {
            if (tolower(static_cast<unsigned char>(*a)) != tolower(static_cast<unsigned char>(*b)))
                return false;
            ++a;
            ++b;
        }
        return *a == '\0' && *b == '\0';
    }

    // Adapter implementations

    ESP32Impl::ESP32Impl(contracts::logger::Leveled *logger)
        : logger(logger)
    {
    }

    models::Error ESP32Impl::update(const models::OtaCommand &command)
    {
        if (isEmpty(command.url) || isEmpty(command.version) || isEmpty(command.checksum) || command.size == 0)
        {
            logger->error(updateTag, "Invalid argument: malformed OTA command");
            return models::Error::InvalidArgument;
        }

        WiFiClientSecure secure_client;
        WiFiClient plain_client;
        HTTPClient http;
        http.setTimeout(config::otaHttpTimeoutMs);

        bool began = false;
        if (isHttpsUrl(command.url))
        {
            secure_client.setInsecure();
            began = http.begin(secure_client, command.url);
        }
        else
        {
            began = http.begin(plain_client, command.url);
        }

        if (!began)
        {
            logger->error(updateTag, "Failed to initialize HTTP request (url=%s)", command.url);
            return models::Error::OtaDownloadFailed;
        }

        const int status_code = http.GET();
        if (status_code != HTTP_CODE_OK)
        {
            logger->error(updateTag, "Unexpected HTTP status (status=%d url=%s)", status_code, command.url);
            http.end();
            return models::Error::OtaDownloadFailed;
        }

        const int content_length = http.getSize();
        if (content_length > 0 && static_cast<uint32_t>(content_length) != command.size)
        {
            logger->error(
                updateTag,
                "Content length mismatch (expected=%lu actual=%d)",
                static_cast<unsigned long>(command.size),
                content_length);
            http.end();
            return models::Error::OtaSizeMismatch;
        }

        if (!Update.begin(command.size))
        {
            logger->error(updateTag, "Insufficient space for OTA image (size=%lu)", static_cast<unsigned long>(command.size));
            http.end();
            return models::Error::OtaInsufficientSpace;
        }

        mbedtls_sha256_context sha_ctx;
        mbedtls_sha256_init(&sha_ctx);
        mbedtls_sha256_starts(&sha_ctx, 0);

        WiFiClient *stream = http.getStreamPtr();
        uint8_t buffer[config::otaDownloadBufferSize];
        uint32_t written = 0;
        models::Error result = models::Error::Ok;

        while (written < command.size)
        {
            if (!http.connected() && stream->available() == 0)
            {
                logger->error(updateTag, "Connection dropped mid-download (written=%lu/%lu)", static_cast<unsigned long>(written), static_cast<unsigned long>(command.size));
                result = models::Error::OtaDownloadFailed;
                break;
            }

            const std::size_t available = stream->available();
            if (available == 0)
            {
                delay(1);
                continue;
            }

            const std::size_t to_read = available > sizeof(buffer) ? sizeof(buffer) : available;
            const std::size_t read = stream->readBytes(buffer, to_read);
            if (read == 0)
                continue;

            if (Update.write(buffer, read) != read)
            {
                logger->error(updateTag, "Flash write failed at offset %lu", static_cast<unsigned long>(written));
                result = models::Error::OtaFlashFailed;
                break;
            }

            mbedtls_sha256_update(&sha_ctx, buffer, read);
            written += static_cast<uint32_t>(read);
        }

        http.end();

        if (result != models::Error::Ok)
        {
            mbedtls_sha256_free(&sha_ctx);
            Update.abort();
            return result;
        }

        if (written != command.size)
        {
            logger->error(updateTag, "Size mismatch after download (expected=%lu actual=%lu)", static_cast<unsigned long>(command.size), static_cast<unsigned long>(written));
            mbedtls_sha256_free(&sha_ctx);
            Update.abort();
            return models::Error::OtaSizeMismatch;
        }

        uint8_t digest[32];
        mbedtls_sha256_finish(&sha_ctx, digest);
        mbedtls_sha256_free(&sha_ctx);

        char digest_hex[65];
        hexEncode(digest, sizeof(digest), digest_hex);

        if (!equalsIgnoreCase(digest_hex, command.checksum))
        {
            logger->error(updateTag, "Checksum mismatch (expected=%s actual=%s)", command.checksum, digest_hex);
            Update.abort();
            return models::Error::OtaChecksumMismatch;
        }

        if (!Update.end(true))
        {
            logger->error(updateTag, "Failed to finalize OTA update (error=%s)", Update.errorString());
            return models::Error::OtaFlashFailed;
        }

        return models::Error::Ok;
    }
}
