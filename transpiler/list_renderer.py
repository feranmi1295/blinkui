"""
BlinkUI Transpiler — List Renderer

Handles for loops inside build() methods.

Python:
    for item in self.items:
        Card(Text(item["name"]))

Generated C:
    for (int _i = 0; _i < self->items_count; _i++) {
        // render Card with item data
    }

For now: handles static list state and simple iteration.
"""

import ast

def detect_for_loops(build_tree) -> list:
    """Find all for loops inside a build() method."""
    loops = []
    if not build_tree:
        return loops
    for node in ast.walk(build_tree):
        if isinstance(node, ast.For):
            loops.append(node)
    return loops
