## tests.unit.docs.test_unit_py_splitter
from unittest import TestCase
from unittest.mock import patch, MagicMock
import ast
from langchain.schema import Document
from pyfiles.docs.ast_code_splitter import ASTCodeSplitter 

class TestPythonSplitterUnit(TestCase):
    @staticmethod
    def _make_func_def():
        """Return the AST node for `def foo(): pass`."""
        return ast.parse("def foo():\n    pass\n").body[0]

    @staticmethod
    def _make_import_node():
        """Return the AST node for `import os, sys`."""
        return ast.parse("import os, sys\n").body[0]

    @staticmethod
    def _make_assign_nodes():
        """Return a list of assignment nodes: `a = 1; b = 'x'`."""
        tree = ast.parse("a = 1\nb = 'x'\n")
        return [node for node in tree.body if isinstance(node, ast.Assign)]

    @staticmethod
    def _simple_code():
        """A short Python snippet that will generate several document types."""
        return (
            "import os\n"
            "x = 42\n\n"
            "def foo():\n"
            "    return x\n\n"
            "class Bar:\n"
            "    def __init__(self, y):\n"
            "        self.y = y\n"
            "    def bar(self):\n"
            "        return self.y\n"
        )

    def test_init_success(self):
        """Test successful initialization of ASTCodeSplitter."""
        code = "import os\nx = 1\n"
        splitter = ASTCodeSplitter("test.py", code)
        self.assertEqual(splitter.source, "test.py")
        self.assertEqual(splitter.content, code)
        self.assertEqual(splitter.chunk_size, 512)
        self.assertIsNotNone(splitter.tree)
        self.assertIsNone(splitter.docstring)

    def test_init_failure_invalid_syntax(self):
        """Test initialization failure with invalid Python syntax."""
        invalid_code = "import os\nx = 1\ninvalid syntax here"
        with self.assertRaises(Exception):
            ASTCodeSplitter("test.py", invalid_code)

    def test_create_document_success(self):
        """Test successful document creation."""
        code = "import os\nx = 1\n"
        splitter = ASTCodeSplitter("test.py", code)
        func_node = self._make_func_def()
        doc = splitter._create_document(
            node=func_node,
            content="def foo():\n    pass\n",
            section_type="function",
            name="foo"
        )
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.metadata["type"], "FunctionDef")
        self.assertEqual(doc.metadata["name"], "foo")
        self.assertEqual(doc.metadata["section_type"], "function")

    def test_create_document_failure(self):
        """Test document creation failure."""
        code = "import os\nx = 1\n"
        splitter = ASTCodeSplitter("test.py", code)
        with patch('pyfiles.docs.ast_code_splitter.Document') as mock_document:
            mock_document.side_effect = Exception("Document creation failed")
            with self.assertRaises(Exception):
                splitter._create_document(
                    node=self._make_func_def(),
                    content="def foo():\n    pass\n",
                    section_type="function",
                    name="foo"
                )

    def test_prepend_comments_success(self):
        """Test successful comment prepending."""
        code = "import os\nx = 1\n"
        splitter = ASTCodeSplitter("test.py", code)
        comments = ["# This is a comment", "# Another comment"]
        result = splitter._prepend_comments("x = 1", comments)
        expected = "# This is a comment\n# Another comment\nx = 1"
        self.assertEqual(result, expected)

    def test_prepend_comments_failure(self):
        """Test comment prepending failure."""
        code = "import os\nx = 1\n"
        splitter = ASTCodeSplitter("test.py", code)
        result = splitter._prepend_comments(None, [])
        self.assertIsNone(result)
        result = splitter._prepend_comments("content", None)
        self.assertEqual(result, "content")

    def test_process_import_group_success(self):
        """Test successful import group processing."""
        code = "import os\nimport sys\n"
        splitter = ASTCodeSplitter("test.py", code)
        import_node = self._make_import_node()
        documents = []
        splitter._process_import_group(documents, [import_node], [])
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].metadata["section_type"], "import_group")

    def test_process_import_group_failure(self):
        """Test import group processing failure."""
        code = "import os\nimport sys\n"
        splitter = ASTCodeSplitter("test.py", code)
        with patch('pyfiles.docs.ast_code_splitter.get_source_segment') as mock_get_segment:
            mock_get_segment.side_effect = Exception("Source segment failed")
            documents = []
            import_node = self._make_import_node()
            with self.assertRaises(Exception):
                splitter._process_import_group(documents, [import_node], [])

    def test_process_assign_group_success(self):
        """Test successful assignment group processing."""
        code = "a = 1\nb = 'x'\n"
        splitter = ASTCodeSplitter("test.py", code)
        assign_nodes = self._make_assign_nodes()
        documents = []
        splitter._process_assign_group(documents, assign_nodes, [])
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0].metadata["section_type"], "assignment_group")

    def test_process_assign_group_failure(self):
        """Test assignment group processing failure."""
        code = "a = 1\nb = 'x'\n"
        splitter = ASTCodeSplitter("test.py", code)
        with patch('pyfiles.docs.ast_code_splitter.get_source_segment') as mock_get_segment:
            mock_get_segment.side_effect = Exception("Source segment failed")
            documents = []
            assign_nodes = self._make_assign_nodes()
            with self.assertRaises(Exception):
                splitter._process_assign_group(documents, assign_nodes, [])

    def test_process_nodes_success(self):
        """Test successful node processing."""
        code = self._simple_code()
        splitter = ASTCodeSplitter("test.py", code)
        documents = splitter._process_nodes(splitter.tree.body)
        self.assertGreater(len(documents), 0)
        section_types = [doc.metadata["section_type"] for doc in documents]
        self.assertIn("import_group", section_types)
        self.assertIn("assignment_group", section_types)
        self.assertIn("function", section_types)
        self.assertIn("class_with_init", section_types)

    def test_process_nodes_failure(self):
        """Test node processing failure."""
        code = self._simple_code()
        splitter = ASTCodeSplitter("test.py", code)
        with patch('pyfiles.docs.ast_code_splitter.get_source_segment') as mock_get_segment:
            mock_get_segment.side_effect = Exception("Source segment failed")
            with self.assertRaises(Exception):
                splitter._process_nodes(splitter.tree.body)

    def test_split_success(self):
        """Test successful document splitting."""
        code = self._simple_code()
        splitter = ASTCodeSplitter("test.py", code)
        documents = splitter.split()
        self.assertGreater(len(documents), 0)
        section_types = [doc.metadata["section_type"] for doc in documents]
        self.assertIn("import_group", section_types)
        self.assertIn("assignment_group", section_types)
        self.assertIn("function", section_types)
        self.assertIn("class_with_init", section_types)

    def test_split_failure(self):
        """Test document splitting failure."""
        code = self._simple_code()
        splitter = ASTCodeSplitter("test.py", code)
        with patch.object(splitter, '_process_nodes') as mock_process_nodes:
            mock_process_nodes.side_effect = Exception("Processing failed")
            with self.assertRaises(Exception):
                splitter.split()