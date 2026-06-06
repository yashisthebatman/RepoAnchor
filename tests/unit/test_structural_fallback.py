import unittest
from repoanchor.parser.structural_fallback import StructuralFallbackScanner

class TestStructuralFallbackScanner(unittest.TestCase):
    def test_js_ts_extraction(self):
        js_source = """
/**
 * Resolves active connection.
 */
export class DBConnection {
    constructor() {
        this.init();
    }
}

// Single line function comment
async function connectToDB(host, port) {
    const raw = await establish();
}

const sendPayload = (data) => {
    return true;
}
"""
        scanner = StructuralFallbackScanner("db.js")
        result = scanner.scan(js_source)

        self.assertIn("class DBConnection {", result)
        self.assertIn("function connectToDB(host, port) { pass }", result)
        self.assertIn("const sendPayload = (data) => { pass }", result)
        self.assertIn("Resolves active connection.", result)
        self.assertIn("Single line function comment", result)

    def test_go_extraction(self):
        go_source = """
// GetUser resolves a user structure.
func (s *Server) GetUser(id string) {
    query()
}
"""
        scanner = StructuralFallbackScanner("server.go")
        result = scanner.scan(go_source)

        self.assertIn("func (s *Server) GetUser(id string) {}", result)
        self.assertIn("GetUser resolves a user structure.", result)