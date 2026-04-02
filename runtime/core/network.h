#ifndef BLINKUI_NETWORK_H
#define BLINKUI_NETWORK_H

/* HTTP method constants */
#define BK_HTTP_GET    0
#define BK_HTTP_POST   1
#define BK_HTTP_PUT    2
#define BK_HTTP_DELETE 3

/* Callback type: method, url, body, request_id, screen */
typedef void (*BKNetworkCallback)(
    int method, const char* url, const char* body,
    int request_id, void* screen
);

/* Set the platform network callback */
void bk_set_network_callback(BKNetworkCallback cb);

/* Make HTTP requests */
void bk_http_get(const char* url, int request_id, void* screen);
void bk_http_post(const char* url, const char* body,
                  int request_id, void* screen);

/* Called when response arrives */
void bk_http_on_response(void* screen, int request_id,
                         int status, const char* body);

#endif
