#pragma once

#include <cstddef>
#include <cstdint>

#include "domain/contracts/ranging/stateless.h"
#include "domain/contracts/logger/leveled.h"

namespace infrastructure::ranging::stateless
{
    class DW3000Impl : public contracts::ranging::Stateless
    {
    public:
        DW3000Impl(
            contracts::logger::Leveled *logger,
            uint16_t tx_antenna_delay,
            uint32_t poll_tx_to_resp_rx_delay_uus,
            uint32_t poll_rx_to_resp_tx_delay_uus);
        ~DW3000Impl() override = default;
        DW3000Impl(const DW3000Impl &) = delete;
        DW3000Impl &operator=(const DW3000Impl &) = delete;

        models::Error initiate(const models::RangingCommand &command, float *distance) override;
        models::Error listen(const models::RangingCommand &command) override;

    private:
        uint8_t sequence_number;
        uint16_t tx_antenna_delay;
        uint32_t poll_tx_to_resp_rx_delay_uus;
        uint32_t poll_rx_to_resp_tx_delay_uus;
        contracts::logger::Leveled *logger;
    };
}
