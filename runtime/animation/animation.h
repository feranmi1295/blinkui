#ifndef BK_ANIMATION_H
#define BK_ANIMATION_H

#include <stdbool.h>
#include <stdint.h>

/* ─────────────────────────────────────────
   Easing curves
   Controls how animation accelerates
───────────────────────────────────────── */
typedef enum {
    BK_EASE_LINEAR,
    BK_EASE_IN,
    BK_EASE_OUT,
    BK_EASE_IN_OUT,
    BK_EASE_BOUNCE,
    BK_EASE_SPRING,
} BKEasingCurve;

/* ─────────────────────────────────────────
   What property is being animated
───────────────────────────────────────── */
typedef enum {
    BK_ANIM_OPACITY,
    BK_ANIM_TRANSLATE_X,
    BK_ANIM_TRANSLATE_Y,
    BK_ANIM_SCALE,
    BK_ANIM_ROTATE,
    BK_ANIM_WIDTH,
    BK_ANIM_HEIGHT,
    BK_ANIM_CORNER_RADIUS,
} BKAnimProperty;

/* ─────────────────────────────────────────
   Animation state
───────────────────────────────────────── */
typedef enum {
    BK_ANIM_IDLE,
    BK_ANIM_RUNNING,
    BK_ANIM_PAUSED,
    BK_ANIM_FINISHED,
} BKAnimState;

/* ─────────────────────────────────────────
   A single animation
───────────────────────────────────────── */
typedef struct BKAnimation {
    uint32_t        id;
    uint32_t        node_id;        /* which node to animate */
    BKAnimProperty  property;       /* what to animate */
    float           from_value;     /* start value */
    float           to_value;       /* end value */
    float           duration_ms;    /* duration in milliseconds */
    float           elapsed_ms;     /* how much time has passed */
    float           delay_ms;       /* delay before starting */
    BKEasingCurve   curve;          /* easing function */
    BKAnimState     state;
    bool            loop;           /* repeat forever */

    /* callback when animation finishes */
    void (*on_complete)(uint32_t node_id, void* user_data);
    void* user_data;

    struct BKAnimation* next;       /* linked list */
} BKAnimation;

/* ─────────────────────────────────────────
   Animation engine
───────────────────────────────────────── */
typedef struct {
    BKAnimation*    animations;
    int             count;
    uint32_t        next_id;
    float           last_tick_ms;
} BKAnimEngine;

/* ─────────────────────────────────────────
   Public API
───────────────────────────────────────── */

/* Initialize animation engine */
BKAnimEngine* bk_anim_engine_init(void);

/* Destroy animation engine */
void bk_anim_engine_destroy(BKAnimEngine* engine);

/* Add a new animation */
uint32_t bk_anim_add(
    BKAnimEngine*   engine,
    uint32_t        node_id,
    BKAnimProperty  property,
    float           from_value,
    float           to_value,
    float           duration_ms,
    BKEasingCurve   curve
);

/* Set delay on animation */
void bk_anim_set_delay(BKAnimEngine* engine, uint32_t anim_id, float delay_ms);

/* Set loop on animation */
void bk_anim_set_loop(BKAnimEngine* engine, uint32_t anim_id, bool loop);

/* Set completion callback */
void bk_anim_set_on_complete(
    BKAnimEngine*   engine,
    uint32_t        anim_id,
    void            (*callback)(uint32_t node_id, void* user_data),
    void*           user_data
);

/* Tick — call every frame with delta time in milliseconds */
/* Returns number of animations still running */
int bk_anim_tick(BKAnimEngine* engine, float delta_ms);

/* Stop a specific animation */
void bk_anim_stop(BKAnimEngine* engine, uint32_t anim_id);

/* Stop all animations on a node */
void bk_anim_stop_node(BKAnimEngine* engine, uint32_t node_id);

/* Get current value of an animating property */
float bk_anim_get_value(BKAnimEngine* engine, uint32_t node_id, BKAnimProperty property);

#endif /* BK_ANIMATION_H */