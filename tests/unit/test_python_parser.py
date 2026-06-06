import unittest
import ast
from repoanchor.parser.python_parser import CodeSkeletonizer

class TestPythonParser(unittest.TestCase):
    def test_basic_skeletonization(self):
        source = """
'''Module docstring'''
import os
from sys import exit

@decorator
class SampleClass(BaseClass):
    '''Class docstring'''
    def __init__(self, val: int = 10) -> None:
        self.val = val
        print("Should get stripped")

    async def get_val(self) -> int:
        return self.val
"""
        parsed_ast = ast.parse(source)
        visitor = CodeSkeletonizer()
        visitor.visit(parsed_ast)
        skeleton = visitor.get_skeleton()

        # Structural assertions
        self.assertIn('"""Module docstring"""', skeleton)
        self.assertIn("import os", skeleton)
        self.assertIn("class SampleClass(BaseClass):", skeleton)
        self.assertIn('"""Class docstring"""', skeleton)
        
        # Accept both formatted variants (tight vs. spaced) across Python minor releases
        self.assertTrue(
            "def __init__(self, val: int=10) -> None:" in skeleton or 
            "def __init__(self, val: int = 10) -> None:" in skeleton
        )
        self.assertIn("async def get_val(self) -> int:", skeleton)
        self.assertNotIn('print("Should get stripped")', skeleton)
        self.assertIn("pass", skeleton)

    def test_empty_class_handles_pass(self):
        source = "class EmptyClass:\n    pass"
        parsed_ast = ast.parse(source)
        visitor = CodeSkeletonizer()
        visitor.visit(parsed_ast)
        skeleton = visitor.get_skeleton()
        self.assertIn("class EmptyClass:\n    pass", skeleton)
