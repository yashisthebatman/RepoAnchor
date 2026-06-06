import argparse
import os
import sys
import subprocess
from typing import List, Set, Dict, Tuple
from repoanchor.cache.manager import CacheManager
from repoanchor.parser.registry import ParserRegistry
from repoanchor.parser.markdown_compiler import MarkdownCompiler

def get_staged_files() -> List[str]:
    """Queries Git to get only the files that are currently staged for commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True
        )
        files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return files
    except (subprocess.SubprocessError, FileNotFoundError):
        return []

def get_all_repo_files(registry: ParserRegistry) -> List[str]:
    """Recursively finds supported source files in the repo, ignoring standard cache/env directories."""
    supported_files = []
    ignore_dirs = {".git", "__pycache__", "venv", ".venv", "node_modules", "build", "dist"}
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        for file in files:
            filepath = os.path.join(root, file)
            if filepath.startswith("./") or filepath.startswith(".\\"):
                filepath = filepath[2:]
            if registry.get_language(filepath) != "unsupported":
                supported_files.append(filepath)
    return supported_files

def stage_file_in_git(filepath: str):
    """Stages a specific file back into the current Git index."""
    try:
        subprocess.run(["git", "add", filepath], check=True, capture_output=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

def install_hook():
    """Installs the pre-commit hook into the local .git/hooks directory."""
    git_dir = os.path.join(".git", "hooks")
    if not os.path.exists(git_dir):
        print("Error: '.git' directory not found. Please run this command in the root of a Git repository.")
        sys.exit(1)

    hook_path = os.path.join(git_dir, "pre-commit")
    
    # POSIX shell structure compatible across macOS, Linux, and Windows Git Bash/WSL
    hook_content = """#!/bin/sh
# RepoAnchor pre-commit hook
python -m repoanchor.cli --pre-commit
"""
    try:
        with open(hook_path, "w", newline="\n", encoding="utf-8") as f:
            f.write(hook_content)
        
        # Ensure executable permissions on Unix systems
        if os.name != "nt":
            os.chmod(hook_path, 0o755)
        print(f"Successfully installed RepoAnchor pre-commit hook at {hook_path}")
    except OSError as e:
        print(f"Failed to write pre-commit hook: {str(e)}")
        sys.exit(1)

def run_engine(pre_commit_mode: bool = False, cache_file: str = ".repo-anchor.cache.json", output_file: str = ".repo-anchor.md"):
    registry = ParserRegistry()
    cache_manager = CacheManager(cache_filepath=cache_file)

    # 1. Target Isolation Stage (Incremental checks)
    if pre_commit_mode:
        staged_files = get_staged_files()
        # Fast-path check: exit instantly if no modified files are supported
        matching_files = [f for f in staged_files if registry.get_language(f) != "unsupported"]
        if not matching_files:
            sys.exit(0)
        files_to_process = matching_files
    else:
        files_to_process = get_all_repo_files(registry)

    # 2. Parsing and Aggregation Stage
    skeletons: Dict[str, str] = {}
    dependencies: Dict[str, Dict[str, str]] = {}
    call_graphs: Dict[str, Set[Tuple[str, str]]] = {}

    # Seed map with existing cached records so unmodified files don't need re-parsing
    for filepath, cached_entry in cache_manager.cache_data.items():
        if os.path.exists(filepath):
            skeletons[filepath] = cached_entry.get("skeleton", "")
            dependencies[filepath] = cached_entry.get("imports", {})
            raw_calls = cached_entry.get("calls", [])
            call_graphs[filepath] = {tuple(c) for c in raw_calls}

    # Incrementally parse targets that have changed
    updated_any = False
    for filepath in files_to_process:
        if cache_manager.is_changed(filepath):
            try:
                skeleton, imports, calls = registry.parse_file(filepath)
                
                # Update structures
                skeletons[filepath] = skeleton
                dependencies[filepath] = imports
                call_graphs[filepath] = calls
                
                # Write back to cache structures (converting call tuples to list of lists)
                cache_manager.cache_data[filepath] = {
                    "hash": cache_manager.calculate_hash(filepath) or "",
                    "skeleton": skeleton,
                    "imports": imports,
                    "calls": [list(c) for c in calls]
                }
                updated_any = True
            except Exception as e:
                warning_tag = f"# <!-- Error Tag: Exception during parsing of {filepath}. Error: {str(e)} -->"
                cached_skel = cache_manager.get_cached_skeleton(filepath)
                skeletons[filepath] = f"{warning_tag}\n{cached_skel}" if cached_skel else f"{warning_tag}\n# Skeleton unavailable."
                updated_any = True

    if updated_any:
        cache_manager.save_cache()

    # Prune files that no longer exist on disk
    existing_skeletons = {k: v for k, v in skeletons.items() if os.path.exists(k)}

    # 3. Render Combined Markdown Document
    if existing_skeletons:
        markdown = MarkdownCompiler.compile(existing_skeletons, dependencies, call_graphs)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown)

        # Stage files back into git if running under hook lifecycle controls
        if pre_commit_mode:
            stage_file_in_git(output_file)
            stage_file_in_git(cache_file)

def main():
    parser = argparse.ArgumentParser(description="RepoAnchor Autonomous Engine")
    parser.add_argument("--pre-commit", action="store_true", help="Runs the engine in Git pre-commit lifecycle mode.")
    parser.add_argument("--install", action="store_true", help="Installs the pre-commit hook into the current git repository.")
    parser.add_argument("--cache-file", default=".repo-anchor.cache.json", help="Path to cache metadata storage.")
    parser.add_argument("--output", "-o", default=".repo-anchor.md", help="The output path of the compiled blueprint document.")
    args = parser.parse_args()

    if args.install:
        install_hook()
        sys.exit(0)

    run_engine(
        pre_commit_mode=args.pre_commit,
        cache_file=args.cache_file,
        output_file=args.output
    )

if __name__ == "__main__":
    main()