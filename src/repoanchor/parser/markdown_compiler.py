import os
import re
from typing import Dict, List, Set, Tuple

class MarkdownCompiler:
    """
    Serializes structural source code and call-graphs into a clean, 
    highly compressed Markdown document optimized for LLM consumption.
    """
    @staticmethod
    def clean_excessive_whitespace(text: str) -> str:
        # Collapse multiple empty lines down to a single empty line
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()

    @classmethod
    def compile(
        cls, 
        skeletons: Dict[str, str], 
        dependencies: Dict[str, Dict[str, str]], 
        call_graphs: Dict[str, Set[Tuple[str, str]]]
    ) -> str:
        lines: List[str] = []
        lines.append("# RepoAnchor Repository Structural Blueprint\n")
        
        # 1. System Map & Modules
        lines.append("## 1. System Index")
        for filepath in sorted(skeletons.keys()):
            lines.append(f"- `{filepath}`")
        lines.append("")

        # 2. Global Import Dependencies
        lines.append("## 2. Dependency Registry")
        has_imports = False
        for filepath, import_map in sorted(dependencies.items()):
            if import_map:
                has_imports = True
                lines.append(f"### `{filepath}` Imports:")
                for alias, source in sorted(import_map.items()):
                    if alias != source:
                        lines.append(f"  - `{alias}` -> `{source}`")
                    else:
                        lines.append(f"  - `{source}`")
        if not has_imports:
            lines.append("*No modules currently import external references.*")
        lines.append("")

        # 3. Call Graphs
        lines.append("## 3. Execution Sequences")
        has_calls = False
        for filepath, calls in sorted(call_graphs.items()):
            if calls:
                has_calls = True
                lines.append(f"### `{filepath}` Callflows:")
                for caller, target in sorted(calls):
                    lines.append(f"  - `{caller}()` -> calls `{target}()`")
        if not has_calls:
            lines.append("*No functional invocations analyzed.*")
        lines.append("")

        # 4. Skeletons
        lines.append("## 4. Class and Function Signatures")
        for filepath, skeleton in sorted(skeletons.items()):
            lines.append(f"### `{filepath}` Skeletons")
            lines.append("```python")
            lines.append(cls.clean_excessive_whitespace(skeleton))
            lines.append("```")
            lines.append("")

        return "\n".join(lines).strip()