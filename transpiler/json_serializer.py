"""
BlinkUI Transpiler — JSON Serializer Generator (v2)

Generates C code that serializes the component tree to JSON
at runtime, using current state values.

Supports method chaining: .spacing(), .padding(), .bold(),
.background(), .center(), .size(), .on_tap()
"""

import ast
import sys
import os
sys.path.insert(0, ".")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from parser import ScreenDef, StateVar
from type_inferrer import TypeInferrer
from codegen import CCodeGenerator, COMPONENT_MAP

# import theme if available
try:
    from blinkui.theme import get_theme
    _theme = get_theme()
    _BG       = _theme.background
    _SURFACE  = _theme.surface
    _ACCENT   = _theme.accent
    _TEXT     = _theme.text
    _TEXT2    = _theme.text_secondary
    _DANGER   = _theme.danger
    _BORDER   = _theme.border
    _ON_ACCENT = _theme.text_on_accent
except ImportError:
    _BG       = "#0F0F0F"
    _SURFACE  = "#1A1A1A"
    _ACCENT   = "#00FF88"
    _TEXT     = "#FFFFFF"
    _TEXT2    = "#999999"
    _DANGER   = "#FF3B30"
    _BORDER   = "#2A2A2A"
    _ON_ACCENT = "#0F0F0F"

# ── Method chain extractor ──

def extract_chain(node):
    """
    Unwrap a method chain and return:
    - The base component Call node
    - A dict of props from chained methods
    """
    props  = {}
    current = node

    while isinstance(current, ast.Call):
        if not isinstance(current.func, ast.Attribute):
            break

        method = current.func.attr
        args   = current.args

        if method == "on_tap" and args:
            arg = args[0]
            if isinstance(arg, ast.Attribute):
                props["on_tap"] = arg.attr
        elif method == "spacing" and args:
            if isinstance(args[0], ast.Constant):
                props["spacing"] = args[0].value
        elif method == "padding" and args:
            if isinstance(args[0], ast.Constant):
                v = args[0].value
                props["padding"] = [v, v, v, v]
        elif method == "background" and args:
            if isinstance(args[0], ast.Constant):
                props["background"] = args[0].value
        elif method == "color" and args:
            if isinstance(args[0], ast.Constant):
                props["color"] = args[0].value
        elif method == "size" and args:
            if isinstance(args[0], ast.Constant):
                props["font_size"] = args[0].value
        elif method == "bold":
            props["bold"] = True
        elif method == "center":
            props["text_align"] = "center"
        elif method == "italic":
            props["italic"] = True

        current = current.func.value

    # current is now the base component call
    return current, props


# ── JSON Serializer Generator ──

class JSONSerializerGenerator(CCodeGenerator):

    def __init__(self):
        super().__init__()
        self.tap_map = {}  # handler_name -> node_id

    def _gen_get_tree(self, screen: ScreenDef) -> str:
        if not screen.build_tree:
            return self._get_tree_empty(screen)

        ret_node = None
        for stmt in screen.build_tree.body:
            if isinstance(stmt, ast.Return):
                ret_node = stmt.value
                break

        if not ret_node:
            return self._get_tree_empty(screen)

        self.node_counter = 100
        json_lines = []
        self._gen_json_node(ret_node, screen, json_lines, depth=0)

        body = "\n    ".join(json_lines)
        return f'''// ── get_tree: serialize component tree to JSON ──
char* {screen.name}_get_tree({screen.name}* self) {{
    static char buf[16384];
    int pos = 0;
    {body}
    buf[pos] = '\\0';
    return buf;
}}
'''

    def _get_tree_empty(self, screen):
        return f'''char* {screen.name}_get_tree({screen.name}* self) {{
    return "{{\\"type\\":\\"VStack\\"}}";
}}
'''

    def _gen_json_node(self, node, screen, lines, depth):
        # handle ternary: ComponentA() if condition else ComponentB()
        if isinstance(node, ast.IfExp):
            self._gen_conditional_node(node, screen, lines, depth)
            return

        if not isinstance(node, ast.Call):
            return

        # extract base component and chained props
        base, chain_props = extract_chain(node)

        if not isinstance(base, ast.Call):
            return

        func_name = self._get_func_name(base)
        if func_name not in COMPONENT_MAP:
            return

        self.node_counter += 1
        node_id = self.node_counter

        # track on_tap handler -> node_id
        on_tap = chain_props.get("on_tap")
        if on_tap:
            self.tap_map[on_tap] = node_id

        # get label/content from base args
        content_c = self._gen_content_c(base, screen, lines, node_id)

        # get children from base args
        children = self._get_children_from_base(base, screen, depth)

        # merge default styling with chain props
        styling = self._build_styling(func_name, chain_props, node_id)

        # emit JSON
        self._emit(lines, 'pos += snprintf(buf+pos, 16384-pos, "{");')
        self._emit(lines, f'pos += snprintf(buf+pos, 16384-pos, "\\"type\\":\\"{func_name}\\"");')
        self._emit(lines, f'pos += snprintf(buf+pos, 16384-pos, ",\\"node_id\\":{node_id}");')

        # content
        if func_name in ("Text", "Heading", "Label", "NavigationBar"):
            self._emit(lines,
                f'pos += snprintf(buf+pos, 16384-pos, ",\\"content\\":\\"%s\\"", {content_c});'
            )
        elif func_name == "Button":
            self._emit(lines,
                f'pos += snprintf(buf+pos, 16384-pos, ",\\"label\\":\\"%s\\"", {content_c});'
            )

        # styling
        for key, val in styling.items():
            if isinstance(val, str):
                self._emit(lines,
                    f'pos += snprintf(buf+pos, 16384-pos, ",\\"{key}\\":\\"{val}\\"");'
                )
            elif isinstance(val, bool):
                bval = "true" if val else "false"
                self._emit(lines,
                    f'pos += snprintf(buf+pos, 16384-pos, ",\\"{key}\\":{bval}");'
                )
            elif isinstance(val, list):
                arr = ",".join(str(v) for v in val)
                self._emit(lines,
                    f'pos += snprintf(buf+pos, 16384-pos, ",\\"{key}\\":[{arr}]");'
                )
            else:
                self._emit(lines,
                    f'pos += snprintf(buf+pos, 16384-pos, ",\\"{key}\\":{val}");'
                )

        # children
        if children:
            self._emit(lines, 'pos += snprintf(buf+pos, 16384-pos, ",\\"children\\":[");')
            for i, child in enumerate(children):
                self._gen_json_node(child, screen, lines, depth+1)
                if i < len(children) - 1:
                    self._emit(lines, 'pos += snprintf(buf+pos, 16384-pos, ",");')
            self._emit(lines, 'pos += snprintf(buf+pos, 16384-pos, "]");')
        else:
            self._emit(lines, 'pos += snprintf(buf+pos, 16384-pos, ",\\"children\\":[]");')

        self._emit(lines, 'pos += snprintf(buf+pos, 16384-pos, "}");')

    def _get_children_from_base(self, base, screen, depth):
        children = []
        for arg in base.args:
            # ternary conditional: ComponentA() if x else ComponentB()
            if isinstance(arg, ast.IfExp):
                children.append(arg)
                continue
            if isinstance(arg, ast.Call):
                b, _ = extract_chain(arg)
                if isinstance(b, ast.Call):
                    fname = self._get_func_name(b)
                    if fname in COMPONENT_MAP:
                        children.append(arg)
        for kw in base.keywords:
            if kw.arg == "children" and isinstance(kw.value, ast.List):
                for elt in kw.value.elts:
                    if isinstance(elt, ast.Call):
                        children.append(elt)
                    elif isinstance(elt, ast.IfExp):
                        children.append(elt)
        return children

    def _gen_content_c(self, base, screen, lines, node_id) -> str:
        if not base.args:
            return '""'
        arg = base.args[0]
        if isinstance(arg, ast.Constant):
            return f'"{arg.value}"'
        if isinstance(arg, ast.JoinedStr):
            temp = f"_json_str_{node_id}"
            fmt, vars_ = self._parse_fstring(arg, screen)
            if vars_:
                vars_str = ", ".join(vars_)
                lines.append(
                    f'char {temp}[512]; '
                    f'snprintf({temp}, 512, "{fmt}", {vars_str});'
                )
            else:
                lines.append(
                    f'char {temp}[512]; '
                    f'snprintf({temp}, 512, "{fmt}");'
                )
            return temp
        # keyword arg: title="..."
        for kw in base.keywords:
            if kw.arg == "title" and isinstance(kw.value, ast.Constant):
                return f'"{kw.value.value}"'
        return '"..."'

    def _build_styling(self, func_name, chain_props, node_id) -> dict:
        # defaults per component
        defaults = {
            "VStack": {
                "padding":        [16, 16, 16, 16],
                "background":     _BG,
                "corner_radius":  0,
                "opacity":        1.0,
                "visible":        True,
                "margin":         [0, 0, 0, 0],
            },
            "HStack": {
                "padding":        [0, 0, 0, 0],
                "background":     _BG,
                "corner_radius":  0,
                "opacity":        1.0,
                "visible":        True,
                "margin":         [0, 0, 0, 0],
            },
            "Text": {
                "font_size":  16,
                "bold":       False,
                "color":      _TEXT,
                "padding":    [0, 0, 8, 0],
                "margin":     [0, 0, 0, 0],
                "opacity":    1.0,
                "visible":    True,
            },
            "Heading": {
                "font_size":  28,
                "bold":       True,
                "color":      _TEXT,
                "padding":    [0, 0, 12, 0],
                "margin":     [0, 0, 0, 0],
                "opacity":    1.0,
                "visible":    True,
            },
            "Label": {
                "font_size":  14,
                "bold":       False,
                "color":      _TEXT2,
                "padding":    [0, 0, 4, 0],
                "margin":     [0, 0, 0, 0],
                "opacity":    1.0,
                "visible":    True,
            },
            "Button": {
                "background":    _ACCENT,
                "color":         _BG,
                "corner_radius": 6,
                "font_size":     18,
                "bold":          True,
                "padding":       [16, 20, 16, 20],
                "margin":        [8, 0, 0, 0],
                "opacity":       1.0,
                "visible":       True,
            },
            "Card": {
                "background":    _SURFACE,
                "corner_radius": 12,
                "opacity":       1.0,
                "visible":       True,
                "padding":       [16, 16, 16, 16],
                "margin":        [8, 0, 0, 0],
            },
            "TextField": {
                "font_size":     16,
                "color":         _TEXT,
                "background":    _SURFACE,
                "corner_radius": 8,
                "padding":       [14, 16, 14, 16],
                "margin":        [8, 0, 0, 0],
                "opacity":       1.0,
                "visible":       True,
            },
            "Divider": {
                "background": _BORDER,
                "padding":    [0, 0, 0, 0],
                "margin":     [8, 0, 8, 0],
                "opacity":    1.0,
                "visible":    True,
            },
            "Spacer": {
                "height":  16,
                "opacity": 1.0,
                "visible": True,
                "padding": [0, 0, 0, 0],
                "margin":  [0, 0, 0, 0],
            },
            "NavigationBar": {
                "font_size":  20,
                "bold":       True,
                "color":      _TEXT,
                "background": _BG,
                "padding":    [12, 16, 12, 16],
                "margin":     [0, 0, 0, 0],
                "opacity":    1.0,
                "visible":    True,
            },
        }

        styling = defaults.get(func_name, {
            "opacity": 1.0,
            "visible": True,
            "padding": [0, 0, 0, 0],
            "margin":  [0, 0, 0, 0],
        }).copy()

        # override with chain props
        for k, v in chain_props.items():
            if k == "font_size":
                styling["font_size"] = v
            elif k == "bold":
                styling["bold"] = v
            elif k == "background":
                styling["background"] = v
            elif k == "color":
                styling["color"] = v
            elif k == "padding":
                styling["padding"] = v
            elif k == "spacing":
                styling["spacing"] = v
            elif k == "text_align":
                styling["text_align"] = v

        return styling

    def _gen_on_event(self, screen) -> str:
        cases = []
        for handler_name, nid in self.tap_map.items():
            case = "    if (node_id == " + str(nid) + " && event_type == 0) "
            case += screen.name + "_" + handler_name + "(self);"
            cases.append(case)
        cases_str = "\n".join(cases) if cases else "    // no handlers"
        out  = "// ── on_event dispatcher ──\n"
        out += "void " + screen.name + "_on_event(" + screen.name + "* self, int node_id, int event_type) {\n"
        out += cases_str + "\n"
        out += "}\n"
        return out

    def _gen_conditional_node(self, node, screen, lines, depth):
        """Handle: ComponentA() if self.loading else ComponentB()"""
        test  = self._gen_condition(node.test, screen)
        lines.append(f"if ({test}) {{")
        self._gen_json_node(node.body, screen, lines, depth)
        lines.append("} else {")
        self._gen_json_node(node.orelse, screen, lines, depth)
        lines.append("}")

    def _gen_condition(self, node, screen) -> str:
        """Generate C condition from Python AST."""
        import ast as _ast

        if isinstance(node, _ast.Attribute):
            if (isinstance(node.value, _ast.Name) and
                node.value.id == "self"):
                sv = self._find_state_var(screen, node.attr)
                if sv and sv.inferred_type == "int":
                    return f"self->{node.attr}"
                return f"self->{node.attr}"

        if isinstance(node, _ast.Compare):
            left = self._gen_cond_expr(node.left, screen)
            if node.ops and node.comparators:
                op    = self._gen_cmpop(node.ops[0])
                right = self._gen_cond_expr(node.comparators[0], screen)
                return f"({left} {op} {right})"

        if isinstance(node, _ast.UnaryOp):
            if isinstance(node.op, _ast.Not):
                val = self._gen_condition(node.operand, screen)
                return f"!({val})"

        if isinstance(node, _ast.BoolOp):
            parts = [self._gen_condition(v, screen) for v in node.values]
            op = " && " if isinstance(node.op, _ast.And) else " || "
            return f"({op.join(parts)})"

        return "1"

    def _gen_cond_expr(self, node, screen) -> str:
        import ast as _ast
        if isinstance(node, _ast.Constant):
            if isinstance(node.value, str):
                return f'"{node.value}"'
            return str(node.value)
        if isinstance(node, _ast.Attribute):
            if (isinstance(node.value, _ast.Name) and
                node.value.id == "self"):
                return f"self->{node.attr}"
        return "0"

    def _emit(self, lines, line):
        lines.append(line)


# ── Test ──

if __name__ == "__main__":
    from parser import BlinkUIParser

    test_source = '''
from blinkui import Screen, state
from blinkui.components import VStack, HStack, Text, Heading, Button, Card, Label, NavigationBar

class HomeScreen(Screen):
    count = state(0)

    def build(self):
        return VStack(
            NavigationBar(title="Home"),
            Card(
                VStack(
                    Heading("Welcome to BlinkUI"),
                    Label("Build mobile apps in pure Python"),
                ).spacing(8)
            ),
            Text(f"Count: {self.count}").size(32).bold().center(),
            HStack(
                Button("Increment").on_tap(self.increment),
                Button("Reset").background("#FF3B30").on_tap(self.reset),
            ).spacing(12),
            Button("Go to Detail").on_tap(self.go_detail),
        ).spacing(16).padding(16)

    def increment(self):
        self.count += 1

    def reset(self):
        self.count = 0
'''

    parser   = BlinkUIParser()
    screen   = parser.parse_source(test_source)
    inferrer = TypeInferrer()
    screen   = inferrer.infer(screen)
    gen      = JSONSerializerGenerator()
    c_code   = gen.generate(screen)
    print(c_code)
