import os
import ast
from typing import Dict, Any, Optional, Tuple, Set
from .python_parser import CodeSkeletonizer
from .relation_analyzer import RelationAnalyzer
from .structural_fallback import StructuralFallbackScanner

class ParserRegistry:
    """
    Routes files to their respective parsers based on extensions.
    Provides a safe structural text scanner fallback for multi-language files.
    """
    def __init__(self):
        self.extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".jsx": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".go": "go"
        }

    def get_language(self, filepath: str) -> str:
        _, ext = os.path.splitext(filepath.lower())
        return self.extension_map.get(ext, "unsupported")

    def parse_file(self, filepath: str) -> Tuple[str, Dict[str, str], Set[Tuple[str, str]]]:
        """
        Parses a file and returns:
        (skeleton_code, import_map, call_graph)
        """
        lang = self.get_language(filepath)
        
        if not os.path.exists(filepath):
            return f"# Error: File {filepath} not found.", {}, set()

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except OSError as e:
            return f"# Error: Unable to read file {filepath}. {str(e)}", {}, set()

        if lang == "python":
            parsed_ast = ast.parse(content, filename=filepath)
            
            # Skeleton
            skel_visitor = CodeSkeletonizer()
            skel_visitor.visit(parsed_ast)
            skeleton = skel_visitor.get_skeleton()

            # Relations
            rel_visitor = RelationAnalyzer(filepath)
            rel_visitor.visit(parsed_ast)
            
            return skeleton, rel_visitor.import_map, rel_visitor.calls
        else:
            # Route other extension files to the fallback structural scanner
            scanner = StructuralFallbackScanner(filepath)
            skeleton = scanner.scan(content)
            # Imports and call paths for fallback files default to empty structures
            return skeleton, {}, set()