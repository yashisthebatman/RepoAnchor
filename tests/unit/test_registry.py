import unittest
import tempfile
import os
from repoanchor.parser.registry import ParserRegistry

class TestParserRegistry(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.registry = ParserRegistry()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_routing_by_extension(self):
        # Python
        py_file = os.path.join(self.temp_dir.name, "app.py")
        with open(py_file, "w", encoding="utf-8") as f:
            f.write("def test():\n    return 10\n")

        skeleton, imports, calls = self.registry.parse_file(py_file)
        self.assertIn("def test():", skeleton)

        # Go (routed to fallback scanner)
        go_file = os.path.join(self.temp_dir.name, "main.go")
        with open(go_file, "w", encoding="utf-8") as f:
            f.write("func main() {\n    println(1)\n}\n")

        skeleton, imports, calls = self.registry.parse_file(go_file)
        self.assertIn("func main() {}", skeleton)