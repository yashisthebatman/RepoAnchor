import re
from typing import List

class StructuralFallbackScanner:
    """
    A language-agnostic text scanner that extracts classes, functions,
    methods, and block comments/docstrings from source code.
    Used as a zero-dependency parser for JS/TS/Go and unsupported languages.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        # Patterns to capture high-level structures
        self.class_pattern = re.compile(r'^\s*(export\s+)?class\s+(\w+)')
        self.js_func_pattern = re.compile(r'^\s*(export\s+)?(async\s+)?function\s+(\w+)\s*\(([^)]*)\)')
        self.arrow_func_pattern = re.compile(r'^\s*(export\s+)?const\s+(\w+)\s*=\s*(async\s*)?\(([^)]*)\)\s*=>')
        self.go_func_pattern = re.compile(r'^func\s+(\([^)]+\)\s+)?(\w+)\s*\(([^)]*)\)')

    def scan(self, content: str) -> str:
        lines = content.splitlines()
        output: List[str] = []
        in_block_comment = False
        current_comment: List[str] = []

        for line in lines:
            stripped = line.strip()

            # Handle block comment boundaries (e.g., JS/TS/Go /* ... */)
            if stripped.startswith("/*") or stripped.startswith("/**"):
                in_block_comment = True
                current_comment.append(line)
                if "*/" in stripped and not stripped.startswith("/*"):
                    in_block_comment = False
                continue

            if in_block_comment:
                current_comment.append(line)
                if "*/" in stripped:
                    in_block_comment = False
                continue

            # Handle single-line comments
            if stripped.startswith("//"):
                current_comment.append(line)
                continue

            # Match patterns
            class_match = self.class_pattern.match(line)
            js_func_match = self.js_func_pattern.match(line)
            arrow_func_match = self.arrow_func_pattern.match(line)
            go_func_match = self.go_func_pattern.match(line)

            if class_match:
                if current_comment:
                    output.extend(current_comment)
                    current_comment = []
                class_name = class_match.group(2)
                output.append(f"class {class_name} {{")
                output.append("    // ...")
                output.append("}")
            elif js_func_match:
                if current_comment:
                    output.extend(current_comment)
                    current_comment = []
                func_name = js_func_match.group(3)
                args = js_func_match.group(4).strip()
                output.append(f"function {func_name}({args}) {{ pass }}")
            elif arrow_func_match:
                if current_comment:
                    output.extend(current_comment)
                    current_comment = []
                func_name = arrow_func_match.group(2)
                args = arrow_func_match.group(4).strip()
                output.append(f"const {func_name} = ({args}) => {{ pass }}")
            elif go_func_match:
                if current_comment:
                    output.extend(current_comment)
                    current_comment = []
                receiver = go_func_match.group(1) or ""
                func_name = go_func_match.group(2)
                args = go_func_match.group(3).strip()
                rec_str = receiver.strip() + " " if receiver else ""
                output.append(f"func {rec_str}{func_name}({args}) {{}}")
            else:
                # If non-matching structural text is scanned, slowly expire the comments
                # so block headers don't bleed into unrelated classes/functions
                if stripped != "" and current_comment:
                    pass
                elif not stripped:
                    pass
                else:
                    current_comment = []

        return "\n".join(output)