"""
BlinkUI Transpiler — JSON Serializer Generator

Generates C code that serializes the component tree to JSON
at runtime, using current state values.

This replaces the placeholder in get_tree().
"""

import ast
import sys
sys.path.insert(0, ".")

from parser import ScreenDef, StateVar
from type_inferrer import TypeInferrer
from codegen import CCodeGenerator, COMPONENT_MAP

class JSONSerializerGenerator(CCodeGenerator):
    """
    Extends CCodeGenerator with a real get_tree() implementation
    that emits JSON directly from C state values.
    """

    def _gen_get_tree(self, screen: ScreenDef) -> str:
        if not screen.build_tree:
            return self._get_tree_empty(screen)

        # find return statement
        ret_node = None
        for stmt in screen.build_tree.body:
            if isinstance(stmt, ast.Return):
                ret_node = stmt.value
                break

        if not ret_node:
            return self._get_tree_empty(screen)

        # generate JSON builder
        self.node_counter = 100
        json_lines = []
        self._gen_json_node(ret_node, screen, json_lines, depth=0)

        body = "\n    ".join(json_lines)
        return f'''// ── get_tree: serialize component tree to JSON ──
char* {screen.name}_get_tree({screen.name}* self) {{
    static char buf[8192];
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
        if not isinstance(node, ast.Call):
            return

        func_name = self._get_func_name(node)
        inner     = self._unwrap_component_call(node)

        if func_name not in COMPONENT_MAP:
            return

        self.node_counter += 1
        node_id = self.node_counter

        # get props
        on_tap = self._get_on_tap(node)

        # get label/content
        content_c = self._gen_content_c(inner, screen, lines, node_id)

        # get children
        children = self._get_children(node, screen, depth)

        # emit JSON open
        self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, "{{");')

        # type
        self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, "\\"type\\":\\"{func_name}\\"");')

        # node_id
        self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, ",\\"node_id\\":{node_id}");')

        # content/label
        if func_name in ("Text", "Heading", "Label"):
            self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, ",\\"content\\":\\"%s\\"", {content_c});')
        elif func_name == "Button":
            self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, ",\\"label\\":\\"%s\\"", {content_c});')

        # default styling per component
        styling = self._default_styling(func_name)
        if styling:
            self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, "{styling}");')

        # children
        if children:
            self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, ",\\"children\\":[");')
            for i, child in enumerate(children):
                self._gen_json_node(child, screen, lines, depth+1)
                if i < len(children) - 1:
                    self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, ",");')
            self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, "]");')
        else:
            self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, ",\\"children\\":[]");')

        # close
        self._emit(lines, f'pos += snprintf(buf+pos, 8192-pos, "}}");')

    def _gen_content_c(self, inner, screen, lines, node_id) -> str:
        if not inner.args:
            return '""'

        arg = inner.args[0]

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

        return '"..."'

    def _get_on_tap(self, node) -> str:
        current = node
        while isinstance(current, ast.Call):
            if isinstance(current.func, ast.Attribute):
                if current.func.attr == "on_tap" and current.args:
                    arg = current.args[0]
                    if isinstance(arg, ast.Attribute):
                        return arg.attr
                current = current.func.value
            else:
                break
        return ""

    def _default_styling(self, func_name) -> str:
        styles = {
            "VStack":  ',\\"padding\\":[24,24,24,24],\\"background\\":\\"#F2F2F7\\",'
                       '\\"corner_radius\\":0,\\"opacity\\":1.0,\\"visible\\":true,'
                       '\\"margin\\":[0,0,0,0]',
            "HStack":  ',\\"padding\\":[0,0,0,0],\\"background\\":\\"\\","'
                       '\\"corner_radius\\":0,\\"opacity\\":1.0,\\"visible\\":true,'
                       '\\"margin\\":[0,0,0,0]',
            "Text":    ',\\"font_size\\":16,\\"bold\\":false,\\"color\\":\\"#1C1C1E\\",'
                       '\\"padding\\":[0,0,8,0],\\"margin\\":[0,0,0,0],'
                       '\\"opacity\\":1.0,\\"visible\\":true',
            "Heading": ',\\"font_size\\":28,\\"bold\\":true,\\"color\\":\\"#1C1C1E\\",'
                       '\\"padding\\":[0,0,12,0],\\"margin\\":[0,0,0,0],'
                       '\\"opacity\\":1.0,\\"visible\\":true',
            "Button":  ',\\"background\\":\\"#007AFF\\",\\"color\\":\\"#FFFFFF\\",'
                       '\\"corner_radius\\":14,\\"font_size\\":18,\\"bold\\":true,'
                       '\\"padding\\":[16,20,16,20],\\"margin\\":[8,0,0,0],'
                       '\\"opacity\\":1.0,\\"visible\\":true',
            "Card":    ',\\"background\\":\\"#FFFFFF\\",\\"corner_radius\\":12,'
                       '\\"opacity\\":1.0,\\"visible\\":true,'
                       '\\"padding\\":[16,16,16,16],\\"margin\\":[8,0,0,0]',
        }
        return styles.get(func_name, "")

    def _emit(self, lines, line):
        lines.append(line)


# ── Test ──

if __name__ == "__main__":
    from parser import BlinkUIParser

    test_source = '''
from blinkui import Screen, state
from blinkui.components import VStack, Text, Button, Heading

class HomeScreen(Screen):
    count = state(0)
    name  = state("BlinkUI")

    def build(self):
        return VStack(
            Heading(f"Hello from {self.name}"),
            Text(f"Count: {self.count}"),
            Button("Tap Me").on_tap(self.increment),
            Button("Reset").on_tap(self.reset),
        )

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
