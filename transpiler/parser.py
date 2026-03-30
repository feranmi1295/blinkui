"""
BlinkUI Python-to-C Transpiler — Parser Stage

Reads a BlinkUI screen file and extracts:
- Screen name
- State variables and their types
- build() method component tree
- Event handler methods
"""

import ast
import sys
from dataclasses import dataclass, field
from typing import Optional

# ── Data structures ──

@dataclass
class StateVar:
    name:         str
    default:      object
    inferred_type: str = "unknown"  # int, str, bool, float

@dataclass
class EventHandler:
    name:   str
    body:   list  # list of AST statements

@dataclass
class Component:
    type:     str                    # VStack, Text, Button etc
    props:    dict                   # label, color, font_size etc
    children: list                   # list of Component
    node_id:  int = 0

@dataclass
class ScreenDef:
    name:          str
    state_vars:    list = field(default_factory=list)
    build_tree:    Optional[object] = None  # raw AST node
    event_handlers: list = field(default_factory=list)
    imports:       list = field(default_factory=list)

# ── Parser ──

class BlinkUIParser:

    def __init__(self):
        self.node_counter = 0

    def parse_file(self, filepath: str) -> ScreenDef:
        with open(filepath) as f:
            source = f.read()
        return self.parse_source(source)

    def parse_source(self, source: str) -> ScreenDef:
        tree = ast.parse(source)
        screen = None

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # check if it inherits from Screen
                bases = [self._name(b) for b in node.bases]
                if "Screen" in bases:
                    screen = self._parse_screen(node)
                    break

        if not screen:
            raise ValueError("No Screen subclass found in file")

        return screen

    def _parse_screen(self, cls_node: ast.ClassDef) -> ScreenDef:
        screen = ScreenDef(name=cls_node.name)

        for item in cls_node.body:
            # state variables: count = state(0)
            if isinstance(item, ast.Assign):
                sv = self._try_parse_state(item)
                if sv:
                    screen.state_vars.append(sv)

            # methods
            elif isinstance(item, ast.FunctionDef):
                if item.name == "build":
                    screen.build_tree = item
                elif item.name not in ("__init__", "on_mount", "on_unmount"):
                    screen.event_handlers.append(
                        EventHandler(name=item.name, body=item.body)
                    )

        return screen

    def _try_parse_state(self, assign: ast.Assign) -> Optional[StateVar]:
        if len(assign.targets) != 1:
            return None
        target = assign.targets[0]
        if not isinstance(target, ast.Name):
            return None

        value = assign.value
        # must be state(default_value)
        if not (isinstance(value, ast.Call) and
                self._name(value.func) == "state"):
            return None

        if not value.args:
            return None

        default = self._eval_literal(value.args[0])
        return StateVar(name=target.id, default=default)

    def _eval_literal(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [self._eval_literal(e) for e in node.elts]
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -self._eval_literal(node.operand)
        return None

    def _name(self, node) -> str:
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return node.attr
        return ""


# ── Test ──

if __name__ == "__main__":
    test_source = '''
from blinkui import Screen, state
from blinkui.components import VStack, Text, Button

class HomeScreen(Screen):
    count = state(0)
    name  = state("John")
    active = state(True)

    def build(self):
        return VStack(
            Text(f"Count: {self.count}"),
            Button("Tap Me").on_tap(self.increment),
        )

    def increment(self):
        self.count += 1

    def reset(self):
        self.count = 0
        self.name  = "Reset"
'''

    parser = BlinkUIParser()
    screen = parser.parse_source(test_source)

    print(f"Screen: {screen.name}")
    print(f"State vars:")
    for sv in screen.state_vars:
        print(f"  {sv.name} = {sv.default!r}")
    print(f"Event handlers:")
    for eh in screen.event_handlers:
        print(f"  {eh.name}()")
    print(f"Has build(): {screen.build_tree is not None}")
