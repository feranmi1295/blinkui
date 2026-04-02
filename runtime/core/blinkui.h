/* runtime/core/blinkui.h */
#ifndef BLINKUI_H
#define BLINKUI_H

#include <stdint.h>
#include <stdbool.h>

/* ─────────────────────────────────────────
   Component types
   Every UI element is one of these types
───────────────────────────────────────── */
typedef enum {
    BK_NODE_VIEW,
    BK_NODE_TEXT,
    BK_NODE_BUTTON,
    BK_NODE_IMAGE,
    BK_NODE_SCROLL,
    BK_NODE_INPUT,
    BK_NODE_VSTACK,
    BK_NODE_HSTACK,
    BK_NODE_ZSTACK,
} BKNodeType;

/* ─────────────────────────────────────────
   Color
───────────────────────────────────────── */
typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} BKColor;

/* ─────────────────────────────────────────
   Layout and sizing
───────────────────────────────────────── */
typedef struct {
    float width;
    float height;
    float padding_top;
    float padding_bottom;
    float padding_left;
    float padding_right;
    float margin_top;
    float margin_bottom;
    float margin_left;
    float margin_right;
    float corner_radius;
    float spacing;          /* gap between children in stacks */
} BKLayout;

/* ─────────────────────────────────────────
   Text properties
───────────────────────────────────────── */
typedef struct {
    char*   content;
    float   font_size;
    bool    bold;
    bool    italic;
    BKColor color;
} BKTextProps;

/* ─────────────────────────────────────────
   The core node — every UI element is a node
───────────────────────────────────────── */
typedef struct BKNode {
    uint32_t        id;             /* unique id for reconciler */
    BKNodeType      type;           /* what kind of component */
    BKLayout        layout;         /* sizing and spacing */
    BKColor         background;     /* background color */
    BKTextProps     text;           /* text properties if text node */
    bool            visible;        /* is it on screen */

    /* children */
    struct BKNode** children;
    int             child_count;
    int             child_capacity;

    /* native view reference */
    /* points to UIView on iOS or View on Android */
    void*           native_ref;

    /* event callbacks — called from C into Python */
    void (*on_tap)(struct BKNode* node);
    void (*on_change)(struct BKNode* node, const char* value);

} BKNode;

/* ─────────────────────────────────────────
   The runtime context
   One instance for the whole app lifetime
───────────────────────────────────────── */
typedef struct {
    BKNode*     root;           /* root of component tree */
    bool        running;        /* is app running */
    uint32_t    next_id;        /* id counter for new nodes */
} BKRuntime;

/* ─────────────────────────────────────────
   Public API
───────────────────────────────────────── */

/* Initialize the runtime */
BKRuntime* bk_runtime_init(void);

/* Shut down and free everything */
void bk_runtime_destroy(BKRuntime* rt);

/* Create a new node */
BKNode* bk_node_create(BKRuntime* rt, BKNodeType type);

/* Add child to parent node */
void bk_node_append_child(BKNode* parent, BKNode* child);

/* Free a node and all its children */
void bk_node_destroy(BKNode* node);

/* Set text content on a node */
void bk_node_set_text(BKNode* node, const char* text);

/* Set background color */
void bk_node_set_background(BKNode* node, uint8_t r, uint8_t g, uint8_t b, uint8_t a);

/* Show a toast notification */
void bk_toast(const char* message, const char* type);
#define BK_TOAST_SUCCESS "success"
#define BK_TOAST_ERROR   "error"
#define BK_TOAST_INFO    "info"
#define BK_TOAST_WARNING "warning"

/* Set the render callback (called by Android bridge) */
void bk_set_render_callback(void (*cb)(void* screen));

/* ─────────────────────────────────────────
   High-level component API
   Used by transpiler-generated C code
───────────────────────────────────────── */

/* Layout components */
BKNode* bk_vstack(BKNode** children, int count, int node_id);
BKNode* bk_hstack(BKNode** children, int count, int node_id);
BKNode* bk_zstack(BKNode** children, int count, int node_id);
BKNode* bk_scroll(BKNode** children, int count, int node_id);
BKNode* bk_card(BKNode** children, int count, int node_id);

/* Text components */
BKNode* bk_text(const char* content, int node_id);
BKNode* bk_heading(const char* content, int node_id);
BKNode* bk_label(const char* content, int node_id);

/* Interactive components */
BKNode* bk_button(const char* label, int node_id);
BKNode* bk_textfield(const char* placeholder, int node_id);
BKNode* bk_toggle(int value, int node_id);
BKNode* bk_slider(float value, int node_id);

/* Media */
BKNode* bk_image(const char* src, int node_id);

/* Utility */
BKNode* bk_spacer(int node_id);
BKNode* bk_divider(int node_id);

/* ─────────────────────────────────────────
   Render request
   Called by event handlers after state change
───────────────────────────────────────── */
void bk_request_render(void* screen);

/* Show a toast notification */
void bk_toast(const char* message, const char* type);
#define BK_TOAST_SUCCESS "success"
#define BK_TOAST_ERROR   "error"
#define BK_TOAST_INFO    "info"
#define BK_TOAST_WARNING "warning"

/* Set the render callback (called by Android bridge) */
void bk_set_render_callback(void (*cb)(void* screen));

#endif /* BLINKUI_H */
