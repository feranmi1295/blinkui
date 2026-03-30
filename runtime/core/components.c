/* ─────────────────────────────────────────
   BlinkUI Component Factory
   High-level API used by transpiler output
───────────────────────────────────────── */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "blinkui.h"

/* ── Internal node allocator ── */
static BKNode* _bk_alloc(int node_id, BKNodeType type) {
    BKNode* node = (BKNode*)calloc(1, sizeof(BKNode));
    if (!node) return NULL;
    node->id      = (uint32_t)node_id;
    node->type    = type;
    node->visible = true;
    return node;
}

static void _bk_set_children(BKNode* node, BKNode** children, int count) {
    if (!children || count == 0) return;
    node->children    = (BKNode**)malloc(sizeof(BKNode*) * count);
    node->child_count = count;
    for (int i = 0; i < count; i++) {
        node->children[i] = children[i];
    }
}

static void _bk_set_text(BKNode* node, const char* content) {
    if (!content) return;
    node->text.content = strdup(content);
}

/* ── Layout components ── */

BKNode* bk_vstack(BKNode** children, int count, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_VSTACK);
    _bk_set_children(n, children, count);
    n->background.r = 242;
    n->background.g = 242;
    n->background.b = 247;
    n->background.a = 255;
    return n;
}

BKNode* bk_hstack(BKNode** children, int count, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_HSTACK);
    _bk_set_children(n, children, count);
    return n;
}

BKNode* bk_zstack(BKNode** children, int count, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_ZSTACK);
    _bk_set_children(n, children, count);
    return n;
}

BKNode* bk_scroll(BKNode** children, int count, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_SCROLL);
    _bk_set_children(n, children, count);
    return n;
}

BKNode* bk_card(BKNode** children, int count, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_VIEW);
    _bk_set_children(n, children, count);
    n->background.r = 255;
    n->background.g = 255;
    n->background.b = 255;
    n->background.a = 255;
    n->layout.corner_radius = 12;
    return n;
}

/* ── Text components ── */

BKNode* bk_text(const char* content, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_TEXT);
    _bk_set_text(n, content);
    n->text.font_size = 16;
    n->text.bold      = false;
    n->text.color.r   = 28;
    n->text.color.g   = 28;
    n->text.color.b   = 30;
    n->text.color.a   = 255;
    return n;
}

BKNode* bk_heading(const char* content, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_TEXT);
    _bk_set_text(n, content);
    n->text.font_size = 28;
    n->text.bold      = true;
    n->text.color.r   = 28;
    n->text.color.g   = 28;
    n->text.color.b   = 30;
    n->text.color.a   = 255;
    return n;
}

BKNode* bk_label(const char* content, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_TEXT);
    _bk_set_text(n, content);
    n->text.font_size = 14;
    n->text.color.r   = 142;
    n->text.color.g   = 142;
    n->text.color.b   = 147;
    n->text.color.a   = 255;
    return n;
}

/* ── Interactive components ── */

BKNode* bk_button(const char* label, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_BUTTON);
    _bk_set_text(n, label);
    n->text.font_size = 18;
    n->text.bold      = true;
    n->text.color.r   = 255;
    n->text.color.g   = 255;
    n->text.color.b   = 255;
    n->text.color.a   = 255;
    n->background.r   = 0;
    n->background.g   = 122;
    n->background.b   = 255;
    n->background.a   = 255;
    n->layout.corner_radius = 14;
    return n;
}

BKNode* bk_textfield(const char* placeholder, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_INPUT);
    _bk_set_text(n, placeholder);
    return n;
}

BKNode* bk_toggle(int value, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_VIEW);
    return n;
}

BKNode* bk_slider(float value, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_VIEW);
    return n;
}

/* ── Media ── */

BKNode* bk_image(const char* src, int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_IMAGE);
    _bk_set_text(n, src);
    return n;
}

/* ── Utility ── */

BKNode* bk_spacer(int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_VIEW);
    return n;
}

BKNode* bk_divider(int node_id) {
    BKNode* n = _bk_alloc(node_id, BK_NODE_VIEW);
    n->background.r = 200;
    n->background.g = 200;
    n->background.b = 200;
    n->background.a = 255;
    n->layout.height = 1;
    return n;
}

/* ── Render request ── */

// Global render callback set by Android bridge
static void (*g_render_callback)(void* screen) = NULL;

void bk_set_render_callback(void (*cb)(void* screen)) {
    g_render_callback = cb;
}

void bk_request_render(void* screen) {
    if (g_render_callback) {
        g_render_callback(screen);
    }
}
