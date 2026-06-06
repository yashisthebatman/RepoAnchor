import unittest
import ast
from repoanchor.parser.relation_analyzer import RelationAnalyzer

class TestRelationAnalyzer(unittest.TestCase):
    def test_import_and_call_resolution(self):
        source = """
import json
from os import path as local_path
import client

class Connection:
    def connect(self):
        local_path.exists("test")
        client.send_data()
"""
        parsed_ast = ast.parse(source)
        analyzer = RelationAnalyzer("test.py")
        analyzer.visit(parsed_ast)

        self.assertEqual(analyzer.import_map["json"], "json")
        self.assertEqual(analyzer.import_map["local_path"], "os.path")
        self.assertEqual(analyzer.import_map["client"], "client")

        calls = analyzer.calls
        self.assertTrue(any(caller == "Connection.connect" and target == "os.path.exists" for caller, target in calls))
        self.assertTrue(any(caller == "Connection.connect" and target == "client.send_data" for caller, target in calls))
