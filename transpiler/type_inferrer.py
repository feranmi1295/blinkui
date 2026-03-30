"""
BlinkUI Transpiler — Type Inferrer

Infers C types from Python state variable defaults
and analyses event handlers to confirm types.

Python → C type mapping:
  int   → int
  str   → char[256]
  bool  → int  (C has no bool, use 0/1)
  float → float
  list  → not supported yet
  None  → void*
"""

from parser import ScreenDef, StateVar
from dataclasses import dataclass
from typing import Optional
import ast

# ── C type mapping ──

def infer_c_type(default) -> str:
    if isinstance(default, bool):
        return "int"           # bool before int — bool is subclass of int
    if isinstance(default, int):
        return "int"
    if isinstance(default, float):
        return "float"
    if isinstance(default, str):
        return "char"          # char[256] — handled specially in codegen
    if default is None:
        return "void*"
    return "int"               # safe fallback

def infer_c_declaration(sv: StateVar) -> str:
    """Returns the C struct field declaration for a state variable."""
    t = sv.inferred_type
    if t == "char":
        return f"char {sv.name}[256]"
    return f"{t} {sv.name}"

def infer_c_initial(sv: StateVar) -> str:
    """Returns C initializer value for a state variable."""
    t = sv.inferred_type
    if t == "char":
        return f'"{sv.default}"'
    if t == "int":
        val = 1 if sv.default is True else (0 if sv.default is False else sv.default)
        return str(val)
    if t == "float":
        return str(sv.default)
    return "0"

# ── Handler analyser ──

class TypeInferrer:

    def infer(self, screen: ScreenDef) -> ScreenDef:
        # Step 1 — infer types from default values
        for sv in screen.state_vars:
            sv.inferred_type = infer_c_type(sv.default)

        # Step 2 — analyse event handlers to catch reassignments
        # e.g. self.count = 0 confirms count is int
        for handler in screen.event_handlers:
            self._analyse_handler(handler, screen)

        return screen

    def _analyse_handler(self, handler, screen: ScreenDef):
        for stmt in handler.body:
            # self.name = value
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if (isinstance(target, ast.Attribute) and
                        isinstance(target.value, ast.Name) and
                        target.value.id == "self"):
                        sv = self._find_state(screen, target.attr)
                        if sv and sv.inferred_type == "unknown":
                            val = self._eval_literal(stmt.value)
                            if val is not None:
                                sv.inferred_type = infer_c_type(val)

            # self.count += 1
            elif isinstance(stmt, ast.AugAssign):
                target = stmt.target
                if (isinstance(target, ast.Attribute) and
                    isinstance(target.value, ast.Name) and
                    target.value.id == "self"):
                    sv = self._find_state(screen, target.attr)
                    if sv and sv.inferred_type == "unknown":
                        sv.inferred_type = "int"

    def _find_state(self, screen: ScreenDef, name: str) -> Optional[StateVar]:
        for sv in screen.state_vars:
            if sv.name == name:
                return sv
        return None

    def _eval_literal(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        return None


# ── Test ──

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from parser import BlinkUIParser

    test_source = '''
from blinkui import Screen, state

class HomeScreen(Screen):
    count  = state(0)
    name   = state("John")
    active = state(True)
    score  = state(0.0)

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
        self.active = False
'''

    parser  = BlinkUIParser()
    screen  = parser.parse_source(test_source)
    inferrer = TypeInferrer()
    screen  = inferrer.infer(screen)

    print(f"Screen: {screen.name}")
    print(f"\nState vars with C types:")
    for sv in screen.state_vars:
        decl = infer_c_declaration(sv)
        init = infer_c_initial(sv)
        print(f"  {decl} = {init}")
