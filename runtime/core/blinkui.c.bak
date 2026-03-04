#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "blinkui.h"
#include "reconciler.h"
#include "events.h"
#include "py_host.h"
#include "../animation/animation.h"

/* ─────────────────────────────────────────
   Runtime initialization
───────────────────────────────────────── */
BKRuntime* bk_runtime_init(void) {
    BKRuntime* rt = (BKRuntime*)malloc(sizeof(BKRuntime));
    if (!rt) {
        fprintf(stderr, "[BlinkUI] Failed to allocate runtime\n");
        return NULL;
    }
    rt->root    = NULL;
    rt->running = true;
    rt->next_id = 1;
    printf("[BlinkUI] Runtime initialized\n");
    return rt;
}

/* ─────────────────────────────────────────
   Runtime shutdown
───────────────────────────────────────── */
void bk_runtime_destroy(BKRuntime* rt) {
    if (!rt) return;
    if (rt->root) {
        bk_node_destroy(rt->root);
    }
    free(rt);
    printf("[BlinkUI] Runtime destroyed\n");
}

/* ─────────────────────────────────────────
   Create a new node
───────────────────────────────────────── */
BKNode* bk_node_create(BKRuntime* rt, BKNodeType type) {
    BKNode* node = (BKNode*)calloc(1, sizeof(BKNode));
    if (!node) {
        fprintf(stderr, "[BlinkUI] Failed to allocate node\n");
        return NULL;
    }
    node->id             = rt->next_id++;
    node->type           = type;
    node->visible        = true;
    node->native_ref     = NULL;
    node->children       = NULL;
    node->child_count    = 0;
    node->child_capacity = 0;
    node->on_tap         = NULL;
    node->on_change      = NULL;

    /* default layout */
    node->layout.width          = 0;
    node->layout.height         = 0;
    node->layout.padding_top    = 0;
    node->layout.padding_bottom = 0;
    node->layout.padding_left   = 0;
    node->layout.padding_right  = 0;
    node->layout.corner_radius  = 0;
    node->layout.spacing        = 8;

    /* default background transparent */
    node->background.r = 0;
    node->background.g = 0;
    node->background.b = 0;
    node->background.a = 0;

    return node;
}

/* ─────────────────────────────────────────
   Add child to parent
───────────────────────────────────────── */
void bk_node_append_child(BKNode* parent, BKNode* child) {
    if (!parent || !child) return;

    if (parent->child_count >= parent->child_capacity) {
        int new_capacity = parent->child_capacity == 0 ? 4 : parent->child_capacity * 2;
        BKNode** new_children = (BKNode**)realloc(
            parent->children,
            new_capacity * sizeof(BKNode*)
        );
        if (!new_children) {
            fprintf(stderr, "[BlinkUI] Failed to grow children array\n");
            return;
        }
        parent->children       = new_children;
        parent->child_capacity = new_capacity;
    }
    parent->children[parent->child_count++] = child;
}

/* ─────────────────────────────────────────
   Set text content
───────────────────────────────────────── */
void bk_node_set_text(BKNode* node, const char* text) {
    if (!node || !text) return;
    if (node->text.content) {
        free(node->text.content);
    }
    node->text.content = strdup(text);
}

/* ─────────────────────────────────────────
   Set background color
───────────────────────────────────────── */
void bk_node_set_background(BKNode* node, uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    if (!node) return;
    node->background.r = r;
    node->background.g = g;
    node->background.b = b;
    node->background.a = a;
}

/* ─────────────────────────────────────────
   Destroy node and all children recursively
───────────────────────────────────────── */
void bk_node_destroy(BKNode* node) {
    if (!node) return;
    for (int i = 0; i < node->child_count; i++) {
        bk_node_destroy(node->children[i]);
    }
    if (node->children) free(node->children);
    if (node->text.content) free(node->text.content);
    free(node);
}

static void on_anim_complete(uint32_t node_id, void* user_data) {
    printf("[Anim] Animation finished on node(%u)\n", node_id);
}

/* ─────────────────────────────────────────
   Event callback for test
───────────────────────────────────────── */
static void on_button_tap(BKEvent* event, void* user_data) {
    printf("  → Button tapped at x:%.0f y:%.0f — calling Python on_tap\n",
        event->x, event->y);
}

/* ─────────────────────────────────────────
   Test main
───────────────────────────────────────── */
#ifdef BLINKUI_TEST_MAIN
int main(void) {
    printf("=== BlinkUI Runtime Test ===\n");

    BKRuntime* rt = bk_runtime_init();

    BKNode* root   = bk_node_create(rt, BK_NODE_VSTACK);
    BKNode* text   = bk_node_create(rt, BK_NODE_TEXT);
    BKNode* button = bk_node_create(rt, BK_NODE_BUTTON);

    bk_node_set_text(text, "Welcome to BlinkUI");
    bk_node_set_text(button, "Get Started");
    bk_node_set_background(root, 242, 242, 247, 255);

    bk_node_append_child(root, text);
    bk_node_append_child(root, button);
    rt->root = root;

    printf("Root type:     %d\n", rt->root->type);
    printf("Child count:   %d\n", rt->root->child_count);
    printf("Text content:  %s\n", rt->root->children[0]->text.content);
    printf("Button text:   %s\n", rt->root->children[1]->text.content);
    printf("Root bg color: rgb(%d,%d,%d)\n",
        rt->root->background.r,
        rt->root->background.g,
        rt->root->background.b
    );

    /* ── Reconciler Test ── */
    printf("\n=== Reconciler Test ===\n");

    BKNode* old_tree = bk_node_create(rt, BK_NODE_VSTACK);
    BKNode* old_text = bk_node_create(rt, BK_NODE_TEXT);
    bk_node_set_text(old_text, "Count: 0");
    bk_node_append_child(old_tree, old_text);

    BKNode* new_tree = bk_node_create(rt, BK_NODE_VSTACK);
    BKNode* new_text = bk_node_create(rt, BK_NODE_TEXT);
    bk_node_set_text(new_text, "Count: 1");
    bk_node_append_child(new_tree, new_text);

    BKPatchList* patches = bk_reconcile(old_tree, new_tree);
    bk_apply_patches(patches);
    bk_patch_list_destroy(patches);
    bk_node_destroy(old_tree);
    bk_node_destroy(new_tree);

    /* ── Event System Test ── */
    printf("\n=== Event System Test ===\n");

    BKEventSystem* es  = bk_events_init();
    uint32_t button_id = 99;

    bk_events_on(es, button_id, BK_EVENT_TAP, on_button_tap, NULL);

    BKEvent tap = {
        .type    = BK_EVENT_TAP,
        .node_id = button_id,
        .x       = 195.0f,
        .y       = 420.0f,
    };
    bk_events_fire(es, &tap);

    BKEvent orphan_tap = {
        .type    = BK_EVENT_TAP,
        .node_id = 999,
        .x       = 0,
        .y       = 0,
    };
    bk_events_fire(es, &orphan_tap);
    bk_events_destroy(es);

    /* ── Python Host Test ── */
    printf("\n=== Python Host Test ===\n");

    bk_py_init();
    PyRun_SimpleString("import sys; sys.path.insert(0, '../python')");

    bk_py_call("test_screen", "on_mount");
    bk_py_call_with_string("test_screen", "on_tap", "Get Started");
    bk_py_call_with_int("test_screen", "on_count_change", 5);

    char* title = bk_py_call_get_string("test_screen", "get_title");
    if (title) {
        printf("[PyHost] Got title from Python: \"%s\"\n", title);
        free(title);
    }

    bk_py_shutdown();

    /* ── Animation Engine Test ── */
printf("\n=== Animation Engine Test ===\n");

BKAnimEngine* anim = bk_anim_engine_init();

/* fade in a card — opacity 0 to 1 over 300ms */
uint32_t fade_id = bk_anim_add(
    anim, 10, BK_ANIM_OPACITY,
    0.0f, 1.0f, 300.0f, BK_EASE_OUT
);
bk_anim_set_on_complete(anim, fade_id, on_anim_complete, NULL);

/* slide in from bottom — translateY 100 to 0 over 400ms */
bk_anim_add(
    anim, 10, BK_ANIM_TRANSLATE_Y,
    100.0f, 0.0f, 400.0f, BK_EASE_SPRING
);

/* simulate 4 frames at 16ms each (60fps) */
printf("\n-- Simulating 4 frames at 16ms --\n");
for (int frame = 0; frame < 4; frame++) {
    printf("\n[Frame %d]\n", frame + 1);
    bk_anim_tick(anim, 16.0f);
}

/* simulate jumping to end */
printf("\n-- Jumping to completion --\n");
bk_anim_tick(anim, 1000.0f);

bk_anim_engine_destroy(anim);

    /* ── Cleanup ── */
    bk_runtime_destroy(rt);

    printf("\n=== All tests passed ===\n");
    return 0;
}
#endif