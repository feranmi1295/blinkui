#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "events.h"

/* ─────────────────────────────────────────
   Initialize event system
───────────────────────────────────────── */
BKEventSystem* bk_events_init(void) {
    BKEventSystem* es = (BKEventSystem*)calloc(1, sizeof(BKEventSystem));
    if (!es) {
        fprintf(stderr, "[Events] Failed to allocate event system\n");
        return NULL;
    }
    es->listeners      = NULL;
    es->listener_count = 0;
    printf("[Events] Event system initialized\n");
    return es;
}

/* ─────────────────────────────────────────
   Register a listener
───────────────────────────────────────── */
void bk_events_on(
    BKEventSystem*  es,
    uint32_t        node_id,
    BKEventType     event_type,
    BKEventCallback callback,
    void*           user_data
) {
    if (!es || !callback) return;

    BKEventListener* listener = (BKEventListener*)calloc(1, sizeof(BKEventListener));
    listener->node_id    = node_id;
    listener->event_type = event_type;
    listener->callback   = callback;
    listener->user_data  = user_data;
    listener->next       = NULL;

    /* prepend to list */
    listener->next = es->listeners;
    es->listeners  = listener;
    es->listener_count++;

    printf("[Events] Listener registered on node(%u) for event type %d\n",
        node_id, event_type);
}

/* ─────────────────────────────────────────
   Fire an event
   Walks listener list and calls matching callbacks
───────────────────────────────────────── */
void bk_events_fire(BKEventSystem* es, BKEvent* event) {
    if (!es || !event) return;

    printf("[Events] Firing event type(%d) on node(%u)\n",
        event->type, event->node_id);

    bool handled = false;
    BKEventListener* current = es->listeners;

    while (current) {
        if (current->node_id   == event->node_id &&
            current->event_type == event->type) {
            current->callback(event, current->user_data);
            handled = true;
        }
        current = current->next;
    }

    if (!handled) {
        printf("[Events] No listener found for node(%u)\n", event->node_id);
    }
}

/* ─────────────────────────────────────────
   Remove all listeners for a node
───────────────────────────────────────── */
void bk_events_remove(BKEventSystem* es, uint32_t node_id) {
    if (!es) return;

    BKEventListener* current  = es->listeners;
    BKEventListener* previous = NULL;

    while (current) {
        if (current->node_id == node_id) {
            if (previous) {
                previous->next = current->next;
            } else {
                es->listeners = current->next;
            }
            BKEventListener* to_free = current;
            current = current->next;
            free(to_free);
            es->listener_count--;
        } else {
            previous = current;
            current  = current->next;
        }
    }
}

/* ─────────────────────────────────────────
   Destroy event system
───────────────────────────────────────── */
void bk_events_destroy(BKEventSystem* es) {
    if (!es) return;

    BKEventListener* current = es->listeners;
    while (current) {
        BKEventListener* next = current->next;
        free(current);
        current = next;
    }

    free(es);
    printf("[Events] Event system destroyed\n");
}