#pragma once

namespace contracts::device
{
    class Control
    {
    public:
        virtual ~Control() = default;
        virtual void restart() = 0;
    };
}
