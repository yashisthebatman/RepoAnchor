import ast
from .python_parser import CodeSkeletonizer
from ..cache.manager import CacheManager

def process_python_file(filepath: str, cache_manager: CacheManager) -> str:
    """
    Inspects, parses, and skeletonizes a Python file. Resolves syntax failures 
    by injecting warnings and reverting to cached baseline definitions.
    """
    if not cache_manager.is_changed(filepath):
        cached_skel = cache_manager.get_cached_skeleton(filepath)
        if cached_skel is not None:
            return cached_skel

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        parsed_ast = ast.parse(content, filename=filepath)
        visitor = CodeSkeletonizer()
        visitor.visit(parsed_ast)
        skeleton = visitor.get_skeleton()
        
        cache_manager.update_cache(filepath, skeleton)
        return skeleton
        
    except (SyntaxError, IndentationError) as e:
        cached_skel = cache_manager.get_cached_skeleton(filepath)
        warning_tag = f"# <!-- Error Tag: Syntax error while parsing {filepath}. Retaining last known-good state. Error: {str(e)} -->"
        if cached_skel:
            return f"{warning_tag}\n{cached_skel}"
        else:
            return f"{warning_tag}\n# Error parsing source code and no cached skeleton available."
    except OSError as e:
        return f"# <!-- Error Tag: Unable to read file {filepath}. Error: {str(e)} -->"