import unittest
import tempfile
import os
from repoanchor.cache.manager import CacheManager
from repoanchor.parser.orchestrator import process_python_file

class TestSkeletonizeFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.cache_path = os.path.join(self.temp_dir.name, ".cache.json")
        self.cache_manager = CacheManager(cache_filepath=self.cache_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_flow_with_syntax_errors(self):
        file_path = os.path.join(self.temp_dir.name, "module.py")
        
        # 1. Store valid implementation
        with open(file_path, "w") as f:
            f.write("def valid_func():\n    return True\n")
        
        initial_skeleton = process_python_file(file_path, self.cache_manager)
        self.assertIn("def valid_func():", initial_skeleton)
        self.assertNotIn("Error Tag", initial_skeleton)

        # 2. Introduce a syntax error
        with open(file_path, "w") as f:
            f.write("def broken_func(\n") # Invalid syntax

        # Ensure the orchestrator intercepts the error and returns cached state with warning tags
        fallback_skeleton = process_python_file(file_path, self.cache_manager)
        self.assertIn("Error Tag: Syntax error while parsing", fallback_skeleton)
        self.assertIn("def valid_func():", fallback_skeleton) # Restored from cache