#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "animation.h"

/* ─────────────────────────────────────────
   Easing functions
   Each takes t (0.0 to 1.0) and returns
   the eased value (0.0 to 1.0)
───────────────────────────────────────── */
static float ease_linear(float t) {
    return t;
}

static float ease_in(float t) {
    return t * t;
}

static float ease_out(float t) {
    return t * (2.0f - t);
}

static float ease_in_out(float t) {
    if (t < 0.5f) return 2.0f * t * t;
    return -1.0f + (4.0f - 2.0f * t) * t;
}

static float ease_bounce(float t) {
    if (t < (1.0f / 2.75f)) {
        return 7.5625f * t * t;
    } else if (t < (2.0f / 2.75f)) {
        t -= (1.5f / 2.75f);
        return 7.5625f * t * t + 0.75f;
    } else if (t < (2.5f / 2.75f)) {
        t -= (2.25f / 2.75f);
        return 7.5625f * t * t + 0.9375f;
    } else {
        t -= (2.625f / 2.75f);
        return 7.5625f * t * t + 0.984375f;
    }
}

static float ease_spring(float t) {
    /* spring overshoot effect */
    return 1.0f - cosf(t * 3.14159f * (0.2f + 2.5f * t * t * t))
           * powf(1.0f - t, 2.2f);
}

static float apply_easing(BKEasingCurve curve, float t) {
    /* clamp t between 0 and 1 */
    if (t < 0.0f) t = 0.0f;
    if (t > 1.0f) t = 1.0f;

    switch (curve) {
        case BK_EASE_LINEAR:  return ease_linear(t);
        case BK_EASE_IN:      return ease_in(t);
        case BK_EASE_OUT:     return ease_out(t);
        case BK_EASE_IN_OUT:  return ease_in_out(t);
        case BK_EASE_BOUNCE:  return ease_bounce(t);
        case BK_EASE_SPRING:  return ease_spring(t);
        default:              return ease_linear(t);
    }
}

/* ─────────────────────────────────────────
   Interpolate between two values
───────────────────────────────────────── */
static float interpolate(float from, float to, float t) {
    return from + (to - from) * t;
}

/* ─────────────────────────────────────────
   Initialize engine
───────────────────────────────────────── */
BKAnimEngine* bk_anim_engine_init(void) {
    BKAnimEngine* engine = (BKAnimEngine*)calloc(1, sizeof(BKAnimEngine));
    if (!engine) {
        fprintf(stderr, "[Anim] Failed to allocate animation engine\n");
        return NULL;
    }
    engine->animations   = NULL;
    engine->count        = 0;
    engine->next_id      = 1;
    engine->last_tick_ms = 0;
    printf("[Anim] Animation engine initialized\n");
    return engine;
}

/* ─────────────────────────────────────────
   Add animation
───────────────────────────────────────── */
uint32_t bk_anim_add(
    BKAnimEngine*   engine,
    uint32_t        node_id,
    BKAnimProperty  property,
    float           from_value,
    float           to_value,
    float           duration_ms,
    BKEasingCurve   curve
) {
    if (!engine) return 0;

    BKAnimation* anim = (BKAnimation*)calloc(1, sizeof(BKAnimation));
    if (!anim) return 0;

    anim->id          = engine->next_id++;
    anim->node_id     = node_id;
    anim->property    = property;
    anim->from_value  = from_value;
    anim->to_value    = to_value;
    anim->duration_ms = duration_ms;
    anim->elapsed_ms  = 0;
    anim->delay_ms    = 0;
    anim->curve       = curve;
    anim->state       = BK_ANIM_RUNNING;
    anim->loop        = false;
    anim->on_complete = NULL;
    anim->user_data   = NULL;
    anim->next        = NULL;

    /* prepend to list */
    anim->next        = engine->animations;
    engine->animations = anim;
    engine->count++;

    printf("[Anim] Added animation(%u) on node(%u) property(%d) %.1f→%.1f over %.0fms\n",
        anim->id, node_id, property, from_value, to_value, duration_ms);

    return anim->id;
}

/* ─────────────────────────────────────────
   Set delay
───────────────────────────────────────── */
void bk_anim_set_delay(BKAnimEngine* engine, uint32_t anim_id, float delay_ms) {
    if (!engine) return;
    BKAnimation* current = engine->animations;
    while (current) {
        if (current->id == anim_id) {
            current->delay_ms = delay_ms;
            current->state    = BK_ANIM_PAUSED;
            return;
        }
        current = current->next;
    }
}

/* ─────────────────────────────────────────
   Set loop
───────────────────────────────────────── */
void bk_anim_set_loop(BKAnimEngine* engine, uint32_t anim_id, bool loop) {
    if (!engine) return;
    BKAnimation* current = engine->animations;
    while (current) {
        if (current->id == anim_id) {
            current->loop = loop;
            return;
        }
        current = current->next;
    }
}

/* ─────────────────────────────────────────
   Set completion callback
───────────────────────────────────────── */
void bk_anim_set_on_complete(
    BKAnimEngine*   engine,
    uint32_t        anim_id,
    void            (*callback)(uint32_t node_id, void* user_data),
    void*           user_data
) {
    if (!engine) return;
    BKAnimation* current = engine->animations;
    while (current) {
        if (current->id == anim_id) {
            current->on_complete = callback;
            current->user_data   = user_data;
            return;
        }
        current = current->next;
    }
}

/* ─────────────────────────────────────────
   Tick — advance all animations by delta_ms
   This runs every frame from the render loop
───────────────────────────────────────── */
int bk_anim_tick(BKAnimEngine* engine, float delta_ms) {
    if (!engine) return 0;

    int running = 0;
    BKAnimation* current = engine->animations;

    while (current) {
        if (current->state == BK_ANIM_FINISHED) {
            current = current->next;
            continue;
        }

        /* handle delay */
        if (current->state == BK_ANIM_PAUSED) {
            current->delay_ms -= delta_ms;
            if (current->delay_ms <= 0) {
                current->state = BK_ANIM_RUNNING;
            } else {
                current = current->next;
                continue;
            }
        }

        /* advance time */
        current->elapsed_ms += delta_ms;

        /* calculate progress 0.0 to 1.0 */
        float t = current->elapsed_ms / current->duration_ms;

        if (t >= 1.0f) {
            t = 1.0f;
            if (current->loop) {
                current->elapsed_ms = 0;
            } else {
                current->state = BK_ANIM_FINISHED;
            }
        }

        /* apply easing */
        float eased = apply_easing(current->curve, t);

        /* calculate current value */
        float value = interpolate(current->from_value, current->to_value, eased);

        /* on mobile this would update the native view */
        /* on Linux we just print the current value */
        printf("[Anim] node(%u) property(%d) value=%.3f (t=%.2f)\n",
            current->node_id, current->property, value, t);

        /* fire completion callback */
        if (current->state == BK_ANIM_FINISHED && current->on_complete) {
            current->on_complete(current->node_id, current->user_data);
        }

        if (current->state == BK_ANIM_RUNNING) running++;
        current = current->next;
    }

    return running;
}

/* ─────────────────────────────────────────
   Get current value of animating property
───────────────────────────────────────── */
float bk_anim_get_value(BKAnimEngine* engine, uint32_t node_id, BKAnimProperty property) {
    if (!engine) return 0.0f;
    BKAnimation* current = engine->animations;
    while (current) {
        if (current->node_id == node_id && current->property == property) {
            float t     = current->elapsed_ms / current->duration_ms;
            float eased = apply_easing(current->curve, t);
            return interpolate(current->from_value, current->to_value, eased);
        }
        current = current->next;
    }
    return 0.0f;
}

/* ─────────────────────────────────────────
   Stop animation
───────────────────────────────────────── */
void bk_anim_stop(BKAnimEngine* engine, uint32_t anim_id) {
    if (!engine) return;
    BKAnimation* current = engine->animations;
    while (current) {
        if (current->id == anim_id) {
            current->state = BK_ANIM_FINISHED;
            return;
        }
        current = current->next;
    }
}

/* ─────────────────────────────────────────
   Stop all animations on a node
───────────────────────────────────────── */
void bk_anim_stop_node(BKAnimEngine* engine, uint32_t node_id) {
    if (!engine) return;
    BKAnimation* current = engine->animations;
    while (current) {
        if (current->node_id == node_id) {
            current->state = BK_ANIM_FINISHED;
        }
        current = current->next;
    }
}

/* ─────────────────────────────────────────
   Destroy engine and free all animations
───────────────────────────────────────── */
void bk_anim_engine_destroy(BKAnimEngine* engine) {
    if (!engine) return;
    BKAnimation* current = engine->animations;
    while (current) {
        BKAnimation* next = current->next;
        free(current);
        current = next;
    }
    free(engine);
    printf("[Anim] Animation engine destroyed\n");
}