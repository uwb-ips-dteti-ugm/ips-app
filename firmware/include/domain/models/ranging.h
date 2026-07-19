#pragma once

#include <cstddef>
#include <cstdint>

namespace models
{
    struct RangingCommand
    {
        uint16_t pan_id;
        uint16_t listener_address;
        uint16_t initiator_address;
        uint32_t timeout_uus;
    };

    struct RangingResult
    {
        uint16_t pan_id;
        uint16_t source_address;
        uint16_t destination_address;
        float distance;
    };

    struct RangingFailure
    {
        uint16_t pan_id;
        uint16_t source_address;
        uint16_t destination_address;
        const char *message;
    };

    namespace RangingFrameControl
    {
        constexpr uint16_t ShortAddress = 0x8841;
    };

    namespace RangingFunctionCode
    {
        constexpr uint8_t Poll = 0xE0;
        constexpr uint8_t Resp = 0xE1;
    }

    namespace RangingFrameLength
    {
        constexpr std::size_t Poll = 12U;
        constexpr std::size_t Resp = 20U;
    }

    namespace RangingFrameIndex
    {
        constexpr uint8_t FrameControlLow = 0;
        constexpr uint8_t FrameControlHigh = 1;
        constexpr uint8_t SequenceNumber = 2;
        constexpr uint8_t PanIdLow = 3;
        constexpr uint8_t PanIdHigh = 4;
        constexpr uint8_t DestinationAddressLow = 5;
        constexpr uint8_t DestinationAddressHigh = 6;
        constexpr uint8_t SourceAddressLow = 7;
        constexpr uint8_t SourceAddressHigh = 8;
        constexpr uint8_t FunctionCode = 9;
        constexpr uint8_t RespPollRxTime = 10;
        constexpr uint8_t RespRespTxTime = 14;
    }
}
