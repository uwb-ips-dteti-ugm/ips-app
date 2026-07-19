#include "application/task/wifi_connection/base_impl.h"

namespace application::task::wifi_connection
{
    constexpr const char *connectTag = "task::wifi_connection::BaseImpl::connect";
    constexpr const char *disconnectTag = "task::wifi_connection::BaseImpl::disconnect";
    constexpr const char *isConnectedTag = "task::wifi_connection::BaseImpl::isConnected";

    // Application implementations

    BaseImpl::BaseImpl(
        contracts::wifi::Connection *connection,
        contracts::logger::Leveled *logger)
        : connection(connection),
          logger(logger)
    {
    }

    void BaseImpl::connect(const char *ssid, const char *password)
    {
        logger->info(connectTag, "Connecting to WiFi (ssid=%s)", ssid ? ssid : "");
        connection->connect(ssid, password);
    }

    void BaseImpl::disconnect()
    {
        logger->info(disconnectTag, "Disconnecting WiFi");
        connection->disconnect();
    }

    bool BaseImpl::isConnected() const
    {
        if (connection->isConnected())
        {
            logger->info(isConnectedTag, "WiFi is connected");
            return true;
        }
        logger->warn(isConnectedTag, "WiFi is not connected");
        return false;
    }
}
