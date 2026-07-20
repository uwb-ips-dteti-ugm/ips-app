#pragma once

#include <cstdint>

namespace models
{
    struct OtaCommand
    {
        char url[256];
        char version[32];
        uint32_t size;
        char checksum[65]; // lowercase hex sha256 digest + null terminator
    };

    struct OtaResult
    {
        bool success;
        char version[32];
    };

    struct OtaFailure
    {
        char version[32];
        const char *message;
    };
}
