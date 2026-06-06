import unittest
import ast
import tempfile
import os
from repoanchor.parser.python_parser import CodeSkeletonizer
from repoanchor.parser.relation_analyzer import RelationAnalyzer
from repoanchor.parser.markdown_compiler import MarkdownCompiler

class TestCompilerFlow(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_end_to_end_markdown_generation(self):
        file_path = os.path.join(self.temp_dir.name, "service.py")
        source = """
from db import session

def run_query():
    '''Runs db verification'''
    session.execute("SELECT 1")
"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(source)

        parsed_ast = ast.parse(source)
        skel_visitor = CodeSkeletonizer()
        skel_visitor.visit(parsed_ast)
        skeleton = skel_visitor.get_skeleton()

        rel_visitor = RelationAnalyzer("service.py")
        rel_visitor.visit(parsed_ast)

        skeletons = {"service.py": skeleton}
        dependencies = {"service.py": rel_visitor.import_map}
        call_graphs = {"service.py": rel_visitor.calls}

        markdown = MarkdownCompiler.compile(skeletons, dependencies, call_graphs)

        self.assertIn("# RepoAnchor Repository Structural Blueprint", markdown)
        self.assertIn("db.session", markdown)
        self.assertIn("run_query()", markdown)
        self.assertIn("pass", markdown)
