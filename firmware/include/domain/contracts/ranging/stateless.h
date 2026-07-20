#pragma once

#include "domain/models/error.h"
#include "domain/models/ranging.h"

namespace contracts::ranging
{
    class Stateless
    {
    public:
        virtual ~Stateless() = default;
        virtual models::Error initiate(const models::RangingCommand &command, float *distance) = 0;
        virtual models::Error listen(const models::RangingCommand &command) = 0;
    };
}
