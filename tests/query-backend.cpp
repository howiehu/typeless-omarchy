#include <gio/gio.h>
extern "C" GVariant* g_dbus_connection_call_sync(GDBusConnection*, const gchar*, const gchar*, const gchar*, const gchar*, GVariant*, const GVariantType*, GDBusCallFlags, gint, GCancellable*, GError**) {
    return g_variant_ref_sink(g_variant_new("(s)", "real-engine"));
}
