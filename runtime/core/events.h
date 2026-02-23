#ifndef BK_EVENTS_H
#define BK_EVENTS_H

#include "blinkui.h"
#include <stdbool.h>

/* ─────────────────────────────────────────
   Event types
───────────────────────────────────────── */
typedef enum {
    BK_EVENT_TAP,
    BK_EVENT_LONG_PRESS,
    BK_EVENT_SWIPE_LEFT,
    BK_EVENT_SWIPE_RIGHT,
    BK_EVENT_SWIPE_UP,
    BK_EVENT_SWIPE_DOWN,
    BK_EVENT_TEXT_CHANGE,
    BK_EVENT_FOCUS,
    BK_EVENT_BLUR,
    BK_EVENT_SCROLL,
} BKEventType;

/* ─────────────────────────────────────────
   An event — fired when user interacts
───────────────────────────────────────── */
typedef struct {
    BKEventType type;
    uint32_t    node_id;    /* which node was interacted with */
    float       x;          /* touch x position */
    float       y;          /* touch y position */
    const char* text_value; /* for text change events */
} BKEvent;

/* ─────────────────────────────────────────
   Event callback type
   Python side registers these
───────────────────────────────────────── */
typedef void (*BKEventCallback)(BKEvent* event, void* user_data);

/* ─────────────────────────────────────────
   Event listener — registered per node
───────────────────────────────────────── */
typedef struct BKEventListener {
    uint32_t            node_id;
    BKEventType         event_type;
    BKEventCallback     callback;
    void*               user_data;
    struct BKEventListener* next;
} BKEventListener;

/* ─────────────────────────────────────────
   Event system context
───────────────────────────────────────── */
typedef struct {
    BKEventListener*    listeners;
    int                 listener_count;
} BKEventSystem;

/* ─────────────────────────────────────────
   Public API
───────────────────────────────────────── */

/* Initialize event system */
BKEventSystem* bk_events_init(void);

/* Destroy event system */
void bk_events_destroy(BKEventSystem* es);

/* Register a listener on a node */
void bk_events_on(
    BKEventSystem*  es,
    uint32_t        node_id,
    BKEventType     event_type,
    BKEventCallback callback,
    void*           user_data
);

/* Fire an event — runtime calls this when native UI sends interaction */
void bk_events_fire(BKEventSystem* es, BKEvent* event);

/* Remove all listeners for a node */
void bk_events_remove(BKEventSystem* es, uint32_t node_id);

#endif /* BK_EVENTS_H */