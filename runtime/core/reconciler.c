#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "reconciler.h"

/* ─────────────────────────────────────────
   Internal helpers
───────────────────────────────────────── */
static BKPatchList* bk_patch_list_create(void) {
    BKPatchList* list = (BKPatchList*)calloc(1, sizeof(BKPatchList));
    return list;
}

static void bk_patch_list_add(BKPatchList* list, BKPatchType type, BKNode* node) {
    BKPatch* patch = (BKPatch*)calloc(1, sizeof(BKPatch));
    patch->type    = type;
    patch->node_id = node->id;
    patch->node    = node;
    patch->next    = NULL;

    /* append to end of linked list */
    if (!list->head) {
        list->head = patch;
    } else {
        BKPatch* current = list->head;
        while (current->next) {
            current = current->next;
        }
        current->next = patch;
    }
    list->count++;
}

/* ─────────────────────────────────────────
   Compare two colors
───────────────────────────────────────── */
static bool bk_color_equals(BKColor a, BKColor b) {
    return a.r == b.r && a.g == b.g && a.b == b.b && a.a == b.a;
}

/* ─────────────────────────────────────────
   Compare two layouts
───────────────────────────────────────── */
static bool bk_layout_equals(BKLayout a, BKLayout b) {
    return a.width          == b.width
        && a.height         == b.height
        && a.padding_top    == b.padding_top
        && a.padding_bottom == b.padding_bottom
        && a.padding_left   == b.padding_left
        && a.padding_right  == b.padding_right
        && a.spacing        == b.spacing;
}

/* ─────────────────────────────────────────
   Core diff — compare old node vs new node
   recursively walk the tree
───────────────────────────────────────── */
static void bk_diff_nodes(
    BKNode*      old_node,
    BKNode*      new_node,
    BKPatchList* patches
) {
    if (!old_node || !new_node) return;

    /* if types differ completely replace the node */
    if (old_node->type != new_node->type) {
        bk_patch_list_add(patches, BK_PATCH_REPLACE, new_node);
        return;
    }

    /* check visibility changed */
    if (old_node->visible != new_node->visible) {
        bk_patch_list_add(patches, BK_PATCH_VISIBILITY, new_node);
    }

    /* check text changed */
    if (old_node->text.content && new_node->text.content) {
        if (strcmp(old_node->text.content, new_node->text.content) != 0) {
            bk_patch_list_add(patches, BK_PATCH_UPDATE_TEXT, new_node);
        }
    }

    /* check background color changed */
    if (!bk_color_equals(old_node->background, new_node->background)) {
        bk_patch_list_add(patches, BK_PATCH_UPDATE_COLOR, new_node);
    }

    /* check layout changed */
    if (!bk_layout_equals(old_node->layout, new_node->layout)) {
        bk_patch_list_add(patches, BK_PATCH_UPDATE_LAYOUT, new_node);
    }

    /* check children */
    int old_count = old_node->child_count;
    int new_count = new_node->child_count;

    /* new children added */
    if (new_count > old_count) {
        for (int i = old_count; i < new_count; i++) {
            bk_patch_list_add(patches, BK_PATCH_ADD_CHILD, new_node->children[i]);
        }
    }

    /* children removed */
    if (new_count < old_count) {
        for (int i = new_count; i < old_count; i++) {
            bk_patch_list_add(patches, BK_PATCH_REMOVE_CHILD, old_node->children[i]);
        }
    }

    /* recurse into matching children */
    int min_count = old_count < new_count ? old_count : new_count;
    for (int i = 0; i < min_count; i++) {
        bk_diff_nodes(old_node->children[i], new_node->children[i], patches);
    }
}

/* ─────────────────────────────────────────
   Public reconcile function
───────────────────────────────────────── */
BKPatchList* bk_reconcile(BKNode* old_tree, BKNode* new_tree) {
    BKPatchList* patches = bk_patch_list_create();

    if (!old_tree && !new_tree) return patches;

    /* first render — everything is new */
    if (!old_tree && new_tree) {
        bk_patch_list_add(patches, BK_PATCH_ADD_CHILD, new_tree);
        return patches;
    }

    bk_diff_nodes(old_tree, new_tree, patches);
    return patches;
}

/* ─────────────────────────────────────────
   Apply patches
   On Linux — prints what would happen
   On mobile — calls native bridge
───────────────────────────────────────── */
void bk_apply_patches(BKPatchList* patches) {
    if (!patches || patches->count == 0) {
        printf("[Reconciler] Nothing changed. No updates needed.\n");
        return;
    }

    printf("[Reconciler] Applying %d patch(es):\n", patches->count);

    BKPatch* current = patches->head;
    while (current) {
        switch (current->type) {
            case BK_PATCH_UPDATE_TEXT:
                printf("  → UPDATE TEXT  node(%u): \"%s\"\n",
                    current->node_id,
                    current->node->text.content);
                break;
            case BK_PATCH_UPDATE_COLOR:
                printf("  → UPDATE COLOR node(%u): rgb(%d,%d,%d)\n",
                    current->node_id,
                    current->node->background.r,
                    current->node->background.g,
                    current->node->background.b);
                break;
            case BK_PATCH_UPDATE_LAYOUT:
                printf("  → UPDATE LAYOUT node(%u)\n", current->node_id);
                break;
            case BK_PATCH_ADD_CHILD:
                printf("  → ADD CHILD    node(%u)\n", current->node_id);
                break;
            case BK_PATCH_REMOVE_CHILD:
                printf("  → REMOVE CHILD node(%u)\n", current->node_id);
                break;
            case BK_PATCH_REPLACE:
                printf("  → REPLACE      node(%u)\n", current->node_id);
                break;
            case BK_PATCH_VISIBILITY:
                printf("  → VISIBILITY   node(%u): %s\n",
                    current->node_id,
                    current->node->visible ? "visible" : "hidden");
                break;
            default:
                break;
        }
        current = current->next;
    }
}

/* ─────────────────────────────────────────
   Free patch list
───────────────────────────────────────── */
void bk_patch_list_destroy(BKPatchList* patches) {
    if (!patches) return;

    BKPatch* current = patches->head;
    while (current) {
        BKPatch* next = current->next;
        free(current);
        current = next;
    }
    free(patches);
}