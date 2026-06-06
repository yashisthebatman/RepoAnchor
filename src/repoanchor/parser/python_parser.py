import ast
from typing import List

class CodeSkeletonizer(ast.NodeVisitor):
    """
    AST Visitor to decompose Python files down to structural signatures.
    """
    def __init__(self):
        self.output_buffer: List[str] = []
        self.indentation_level = 0

    def _indent(self, offset: int = 0) -> str:
        return "    " * (self.indentation_level + offset)

    def visit_Module(self, node: ast.Module):
        # Capture module-level docstring if it exists
        docstring = ast.get_docstring(node)
        if docstring:
            self.output_buffer.append(f'"""{docstring}"""\n')
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import):
        if self.indentation_level == 0:
            self.output_buffer.append(ast.unparse(node))

    def visit_ImportFrom(self, node: ast.ImportFrom):
        if self.indentation_level == 0:
            self.output_buffer.append(ast.unparse(node))

    def visit_ClassDef(self, node: ast.ClassDef):
        decorators = [f"@{ast.unparse(dec)}" for dec in node.decorator_list]
        for dec in decorators:
            self.output_buffer.append(self._indent() + dec)
        
        bases_str = f"({', '.join(ast.unparse(b) for b in node.bases)})" if node.bases else ""
        self.output_buffer.append(self._indent() + f"class {node.name}{bases_str}:")
        
        docstring = ast.get_docstring(node)
        self.indentation_level += 1
        if docstring:
            self.output_buffer.append(self._indent() + f'"""{docstring}"""')
        
        # Track output buffer size to check if child members exist
        initial_len = len(self.output_buffer)
        
        # Traverse structural elements nested within the class definition
        for item in node.body:
            if isinstance(item, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                self.visit(item)
        
        # Fallback to standard pass statement if class is empty
        if len(self.output_buffer) == initial_len:
            self.output_buffer.append(self._indent() + "pass")
            
        self.indentation_level -= 1

    def _visit_function_common(self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool = False):
        decorators = [f"@{ast.unparse(dec)}" for dec in node.decorator_list]
        for dec in decorators:
            self.output_buffer.append(self._indent() + dec)
            
        args_signature = ast.unparse(node.args)
        return_annotation = f" -> {ast.unparse(node.returns)}" if node.returns else ""
        prefix = "async def" if is_async else "def"
        func_sig = f"{prefix} {node.name}({args_signature}){return_annotation}:"
        self.output_buffer.append(self._indent() + func_sig)
        
        docstring = ast.get_docstring(node)
        if docstring:
            self.output_buffer.append(self._indent(offset=1) + f'"""{docstring}"""')
        self.output_buffer.append(self._indent(offset=1) + "pass")

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._visit_function_common(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._visit_function_common(node, is_async=True)
        
    def get_skeleton(self) -> str:
        return "\n".join(self.output_buffer)