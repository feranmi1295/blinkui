# This Python code runs on the Android device inside CPython
# It produces component trees that the C runtime renders

import json

# ── State ──
state = {
    "count": 0,
    "message": "Hello from Python on Android!"
}

def build_tree():
    """Build component tree JSON from current state"""
    tree = {
        "type": "VStack",
        "padding": [24, 24, 24, 24],
        "spacing": 16,
        "background": "#F2F2F7",
        "corner_radius": 0,
        "opacity": 1.0,
        "visible": True,
        "margin": [0, 0, 0, 0],
        "children": [
            {
                "type": "Heading",
                "content": state["message"],
                "font_size": 24,
                "bold": True,
                "color": "#1C1C1E",
                "padding": [0, 0, 8, 0],
                "margin": [0, 0, 0, 0],
                "opacity": 1.0,
                "visible": True,
                "children": []
            },
            {
                "type": "Text",
                "content": f"Count: {state['count']}",
                "font_size": 56,
                "bold": True,
                "color": "#007AFF",
                "padding": [0, 0, 16, 0],
                "margin": [0, 0, 0, 0],
                "opacity": 1.0,
                "visible": True,
                "children": []
            },
            {
                "type": "Button",
                "label": "Tap Me",
                "background": "#007AFF",
                "color": "#FFFFFF",
                "corner_radius": 14,
                "font_size": 18,
                "bold": True,
                "padding": [16, 20, 16, 20],
                "margin": [0, 0, 0, 0],
                "opacity": 1.0,
                "visible": True,
                "node_id": 42,
                "children": []
            },
            {
                "type": "Button",
                "label": "Reset",
                "background": "#FF3B30",
                "color": "#FFFFFF",
                "corner_radius": 14,
                "font_size": 18,
                "bold": True,
                "padding": [16, 20, 16, 20],
                "margin": [8, 0, 0, 0],
                "opacity": 1.0,
                "visible": True,
                "node_id": 43,
                "children": []
            },
            {
                "type": "Text",
                "content": "Built with Python and C on Android",
                "font_size": 13,
                "bold": False,
                "color": "#8E8E93",
                "padding": [16, 0, 0, 0],
                "margin": [0, 0, 0, 0],
                "opacity": 1.0,
                "visible": True,
                "children": []
            }
        ]
    }
    return json.dumps(tree)

def on_event(node_id, event_type):
    """Handle events from the C runtime"""
    if node_id == 42 and event_type == 0:  # Tap Me
        state["count"] += 1
        state["message"] = f"Tapped {state['count']} times!"
    elif node_id == 43 and event_type == 0:  # Reset
        state["count"] = 0
        state["message"] = "Reset! Tap again."

    return build_tree()

def get_initial_tree():
    """Called on startup"""
    return build_tree()
