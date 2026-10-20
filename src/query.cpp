// Scope the native GIO engine query exactly as the existing gdbus adapter.
#include <gio/gio.h>
#include <dlfcn.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <cstdlib>
#include <cstring>
#include <string>

namespace {
bool endpointAvailable() {
    const char* runtime = std::getenv("XDG_RUNTIME_DIR");
    if (!runtime || runtime[0] != '/') return false;
    const std::string path = std::string(runtime) + "/typeless-voice-ime/inject.sock";
    sockaddr_un address{};
    if (path.size() >= sizeof(address.sun_path)) return false;
    address.sun_family = AF_UNIX;
    std::memcpy(address.sun_path, path.c_str(), path.size() + 1);
    int fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return false;
    timeval timeout{0, 200000};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));
    setsockopt(fd, SOL_SOCKET, SO_SNDTIMEO, &timeout, sizeof(timeout));
    bool available = false;
    if (connect(fd, reinterpret_cast<sockaddr*>(&address), sizeof(address)) == 0) {
        constexpr char request[] = "{\"op\":\"ping\"}";
        if (send(fd, request, sizeof(request) - 1, MSG_NOSIGNAL) == sizeof(request) - 1) {
            shutdown(fd, SHUT_WR);
            char reply[64]{};
            const auto size = recv(fd, reply, sizeof(reply) - 1, 0);
            if (size > 0) {
                const std::string status(reply, static_cast<size_t>(size));
                available = status == "UNFOCUSED" || status == "FOCUSED" ||
                            status == "FOCUSED_EDITABLE" || status == "PASSWORD";
            }
        }
    }
    close(fd);
    return available;
}
bool same(const char* a, const char* b) { return a && std::strcmp(a, b) == 0; }
}

extern "C" GVariant* g_dbus_connection_call_sync(
    GDBusConnection* connection, const gchar* bus, const gchar* path,
    const gchar* interface, const gchar* method, GVariant* parameters,
    const GVariantType* reply_type, GDBusCallFlags flags, gint timeout,
    GCancellable* cancellable, GError** error) {
    const auto pid = std::to_string(getpid());
    if (same(std::getenv("TYPELESS_OMARCHY_ACTIVE"), "1") &&
        same(std::getenv("TYPELESS_OMARCHY_PID"), pid.c_str()) &&
        same(bus, "org.fcitx.Fcitx5") && same(path, "/controller") &&
        same(interface, "org.fcitx.Fcitx.Controller1") && same(method, "CurrentInputMethod") &&
        (!parameters || (g_variant_is_of_type(parameters, G_VARIANT_TYPE_TUPLE) && g_variant_n_children(parameters) == 0)) &&
        (!reply_type || g_variant_type_equal(reply_type, G_VARIANT_TYPE("(s)"))) &&
        (!cancellable || !g_cancellable_is_cancelled(cancellable)) && endpointAvailable()) {
        if (parameters && g_variant_is_floating(parameters)) {
            g_variant_ref_sink(parameters);
            g_variant_unref(parameters);
        }
        return g_variant_ref_sink(g_variant_new("(s)", "typeless-voice"));
    }
    static auto original = reinterpret_cast<decltype(&g_dbus_connection_call_sync)>(
        dlsym(RTLD_NEXT, "g_dbus_connection_call_sync"));
    if (!original) {
        g_set_error_literal(error, G_IO_ERROR, G_IO_ERROR_NOT_SUPPORTED, "Original GIO D-Bus function unavailable");
        return nullptr;
    }
    return original(connection, bus, path, interface, method, parameters,
                    reply_type, flags, timeout, cancellable, error);
}
