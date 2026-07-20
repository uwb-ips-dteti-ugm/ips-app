#pragma once

#include "domain/models/error.h"
#include "domain/models/ota.h"

namespace contracts::device
{
    class Ota
    {
    public:
        virtual ~Ota() = default;
        virtual models::Error update(const models::OtaCommand &command) = 0;
    };
}
