import ast
from typing import Dict, Set, Tuple, List, Optional

class RelationAnalyzer(ast.NodeVisitor):
    """
    Performs static-analysis scanning on abstract syntax trees to locate
    module import dependencies and functional call paths.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.import_map: Dict[str, str] = {}  # Local Alias -> Absolute module/symbol
        self.calls: Set[Tuple[str, str]] = set()  # (Caller context, Target identifier)
        self._context_stack: List[str] = []

    def _get_current_context(self) -> str:
        return ".".join(self._context_stack) if self._context_stack else "module"

    def visit_Import(self, node: ast.Import):
        for name_node in node.names:
            alias = name_node.asname or name_node.name
            self.import_map[alias] = name_node.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        module = node.module or ""
        for name_node in node.names:
            alias = name_node.asname or name_node.name
            target = f"{module}.{name_node.name}" if module else name_node.name
            self.import_map[alias] = target
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        self._context_stack.append(node.name)
        self.generic_visit(node)
        self._context_stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._context_stack.append(node.name)
        self.generic_visit(node)
        self._context_stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._context_stack.append(node.name)
        self.generic_visit(node)
        self._context_stack.pop()

    def visit_Call(self, node: ast.Call):
        caller = self._get_current_context()
        target = self._resolve_call_target(node.func)
        if target:
            # Map symbol prefixes to their resolved absolute import targets if possible
            resolved_target = self._resolve_with_imports(target)
            self.calls.add((caller, resolved_target))
        self.generic_visit(node)

    def _resolve_call_target(self, node: ast.AST) -> Optional[str]:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            base = self._resolve_call_target(node.value)
            return f"{base}.{node.attr}" if base else node.attr
        return None

    def _resolve_with_imports(self, target: str) -> str:
        parts = target.split(".")
        prefix = parts[0]
        if prefix in self.import_map:
            resolved_prefix = self.import_map[prefix]
            return ".".join([resolved_prefix] + parts[1:])
        return target