/* ─────────────────────────────────────────
   BlinkUI Network Layer
   Async HTTP requests from transpiled C screens
   Uses Android's Java HTTP via JNI callback
───────────────────────────────────────── */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "network.h"

/* Global JNI callback for network requests */
static BKNetworkCallback g_network_cb = NULL;

void bk_set_network_callback(BKNetworkCallback cb) {
    g_network_cb = cb;
}

/* Async GET request */
void bk_http_get(const char* url, int request_id, void* screen) {
    if (g_network_cb) {
        g_network_cb(BK_HTTP_GET, url, NULL, request_id, screen);
    }
}

/* Async POST request */
void bk_http_post(const char* url, const char* body,
                  int request_id, void* screen) {
    if (g_network_cb) {
        g_network_cb(BK_HTTP_POST, url, body, request_id, screen);
    }
}

/* Called when response arrives — triggers re-render */
void bk_http_on_response(void* screen, int request_id,
                         int status, const char* body) {
    /* screen's on_response handler sets state and calls bk_request_render */
    /* This is called from Java on the network thread */
}
