import argparse
import os
import sys
from repoanchor.cache.manager import CacheManager
from repoanchor.parser.orchestrator import process_python_file

def main():
    parser = argparse.ArgumentParser(description="RepoAnchor CLI - Phase 1")
    parser.add_argument("files", nargs="*", help="Python files to analyze.")
    parser.add_argument("--cache-file", default=".repo-anchor.cache.json", help="Path to JSON cache file.")
    parser.add_argument("--output", "-o", help="Aggregated structural map output path.")
    args = parser.parse_args()

    if not args.files:
        print("Error: No files provided for parsing.", file=sys.stderr)
        sys.exit(1)

    cache_manager = CacheManager(cache_filepath=args.cache_file)
    outputs = []

    for filepath in args.files:
        if not os.path.exists(filepath):
            print(f"Skipping: file not found '{filepath}'", file=sys.stderr)
            continue
        
        skeleton = process_python_file(filepath, cache_manager)
        outputs.append(f"# File: {filepath}\n{skeleton}\n")

    cache_manager.save_cache()
    combined_output = "\n".join(outputs)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(combined_output)
    else:
        print(combined_output)

if __name__ == "__main__":
    main()