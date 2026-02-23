#ifndef BK_RECONCILER_H
#define BK_RECONCILER_H

#include "blinkui.h"

/* ─────────────────────────────────────────
   Diff result — what changed between
   old tree and new tree
───────────────────────────────────────── */
typedef enum {
    BK_PATCH_NONE,          /* nothing changed */
    BK_PATCH_UPDATE_TEXT,   /* text content changed */
    BK_PATCH_UPDATE_COLOR,  /* color changed */
    BK_PATCH_UPDATE_LAYOUT, /* size or spacing changed */
    BK_PATCH_ADD_CHILD,     /* new child was added */
    BK_PATCH_REMOVE_CHILD,  /* child was removed */
    BK_PATCH_REPLACE,       /* node type changed entirely */
    BK_PATCH_VISIBILITY,    /* visible/hidden changed */
} BKPatchType;

/* ─────────────────────────────────────────
   A single patch instruction
   reconciler produces a list of these
───────────────────────────────────────── */
typedef struct BKPatch {
    BKPatchType     type;
    uint32_t        node_id;    /* which node to update */
    BKNode*         node;       /* pointer to the node */
    struct BKPatch* next;       /* linked list of patches */
} BKPatch;

/* ─────────────────────────────────────────
   Patch list — result of reconciliation
───────────────────────────────────────── */
typedef struct {
    BKPatch*    head;
    int         count;
} BKPatchList;

/* ─────────────────────────────────────────
   Public API
───────────────────────────────────────── */

/* Compare old tree and new tree, produce patch list */
BKPatchList* bk_reconcile(BKNode* old_tree, BKNode* new_tree);

/* Apply patches to the actual UI */
/* On Linux this prints what would happen */
/* On mobile this calls the native bridge */
void bk_apply_patches(BKPatchList* patches);

/* Free patch list after applying */
void bk_patch_list_destroy(BKPatchList* patches);

#endif /* BK_RECONCILER_H */