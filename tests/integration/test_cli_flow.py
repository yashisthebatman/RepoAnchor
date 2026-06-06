import unittest
import os
import tempfile
import json
from repoanchor.cli import run_engine

class TestCLIFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        # Save working directory to return to it later
        self.old_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

    def tearDown(self):
        os.chdir(self.old_cwd)
        self.temp_dir.cleanup()

    def test_cli_integration_and_cache_reload(self):
        # 1. Create a mock Python and Go file inside our temporary repository context
        py_file = "utils.py"
        go_file = "db.go"
        
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def helper():\n    '''Prints helper info'''\n    pass\n")

        with open(go_file, "w", encoding="utf-8") as f:
            f.write("func Query() {}\n")

        cache_name = "test_cache.json"
        md_name = "test_blueprint.md"

        # 2. Run CLI in standard mode to parse both files
        run_engine(pre_commit_mode=False, cache_file=cache_name, output_file=md_name)

        # Assert output documents were created
        self.assertTrue(os.path.exists(cache_name))
        self.assertTrue(os.path.exists(md_name))

        # Check content inside the markdown blueprint
        with open(md_name, "r", encoding="utf-8") as f:
            md_content = f.read()

        self.assertIn("def helper():", md_content)
        self.assertIn("func Query() {}", md_content)

        # 3. Modify the files and run again to verify incremental changes
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def helper_updated():\n    pass\n")

        run_engine(pre_commit_mode=False, cache_file=cache_name, output_file=md_name)

        with open(md_name, "r", encoding="utf-8") as f:
            updated_md_content = f.read()

        self.assertIn("def helper_updated():", updated_md_content)
        self.assertNotIn("def helper():", updated_md_content)