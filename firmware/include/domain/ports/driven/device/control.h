#pragma once

namespace ports::driven::device
{
    class Control
    {
    public:
        virtual ~Control() = default;
        virtual void restart() = 0;
    };
}
