### tests.unit.agents.test_unit_tools
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock
from pydantic import BaseModel, Field

from pyfiles.agents.tools import (
    _enhance_query, 
    _aenhance_query, 
    EnhancedQuery, 
    enhanced_retriever_tool, 
    general_retriever_tool, 
    _searx_search, 
    _searx_asearch
)

searxng_url: str = "http://localhost:8080"

class EnhancedQueryTest(BaseModel):
    query: str = Field(description="Enhanced query.")
    source: str = Field(description="Name of the file to be queried.")

class SearchInputTest(BaseModel):
    query: str = Field(description="search query")
    num_results: int = Field(description="number of search results")

class TestAToolsUnit(IsolatedAsyncioTestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_llm = MagicMock()
        self.mock_llm.with_structured_output = MagicMock(return_value=self.mock_llm)
        self.mock_llm.ainvoke = AsyncMock()
        self.mock_models = MagicMock()
        self.mock_models.llm = self.mock_llm
        self.mock_enhanced_query_result = EnhancedQueryTest(
            query="Overview of architecture and points of time and memory consumption",
            source="file_1.py"
        )
        self.mock_wrapper_instance = MagicMock()
        self.mock_wrapper_instance.aresults = AsyncMock()

    async def test_aenhance_query_success(self):
        """Test successf of _aenhance_query"""
        query = "How can I optimize file1.py?"
        codebase_name = "my_codebase"
        self.mock_models.llm.ainvoke.return_value = self.mock_enhanced_query_result
        result, code_elements = await _aenhance_query(query, codebase_name, self.mock_models)
        expected_result = "[my_codebase] Overview of architecture and points of time and memory consumption"
        assert result == expected_result
        assert code_elements == {"source": "file_1.py"}
        self.mock_models.llm.with_structured_output.assert_called_once_with(EnhancedQuery)
        self.mock_models.llm.ainvoke.assert_called_once()

    @patch('pyfiles.agents.tools.logger')
    async def test_aenhance_query_exception_handling(
        self,
        mock_logger
    ):
        """Test exception handling of _aenhance_query"""
        query = "test query"
        codebase_name = "test_codebase"
        self.mock_models.llm.ainvoke.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            await _aenhance_query(query, codebase_name, self.mock_models)
        mock_logger.error.assert_called_once()

    @patch('pyfiles.agents.tools.SearxSearchWrapper')
    async def test_searx_asearch_success(
        self, 
        mock_searx_wrapper
    ):
        """Test successful async Searx search"""
        query = "test query"
        num_results = 5
        mock_results = [{"title": "Result 1", "url": "http://example.com/1"}, 
                        {"title": "Result 2", "url": "http://example.com/2"}]
        self.mock_wrapper_instance.aresults = AsyncMock(return_value=mock_results)
        mock_searx_wrapper.return_value = self.mock_wrapper_instance
        result = await _searx_asearch(query, num_results)
        assert result == mock_results
        mock_searx_wrapper.assert_called_once_with(searx_host=searxng_url)
        self.mock_wrapper_instance.aresults.assert_called_once_with(query=query, num_results=num_results)

    @patch('pyfiles.agents.tools.SearxSearchWrapper')
    @patch('pyfiles.agents.tools.logger')
    async def test_searx_asearch_exception_handling(
        self, 
        mock_logger,
        mock_searx_wrapper
    ):
        """Test exception handling in _searx_asearch"""
        query = "test query"
        num_results = 5
        self.mock_wrapper_instance = MagicMock()
        self.mock_wrapper_instance.aresults.side_effect = Exception("Async search error")
        mock_searx_wrapper.return_value = self.mock_wrapper_instance
        with self.assertRaises(Exception):
            await _searx_asearch(query, num_results)
        mock_logger.error.assert_called_once()

class TestToolsUnit(TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_llm = MagicMock()
        self.mock_llm.with_structured_output = MagicMock(return_value=self.mock_llm)
        self.mock_llm.invoke = MagicMock()
        self.mock_models = MagicMock()
        self.mock_models.llm = self.mock_llm
        self.mock_enhanced_query_result = EnhancedQueryTest(
            query="Overview of architecture and points of time and memory consumption",
            source="file_1.py"
        )
        self.mock_wrapper_instance = MagicMock()
        self.mock_wrapper_instance.results = MagicMock()
        self.mock_original_tool = MagicMock()
        self.mock_original_tool.name = "original_tool"
        self.mock_original_tool.description = "Original tool description"
        self.mock_original_tool.args_schema = None
        self.mock_vectorstore = MagicMock()
        self.mock_retriever = MagicMock()

    def test_enhanced_query_model_structure(self):
        """Test that EnhancedQuery model has correct structure"""
        query_instance = EnhancedQueryTest(
            query="test query",
            source="test_file.py"
        )
        assert query_instance.query == "test query"
        assert query_instance.source == "test_file.py"

    def test_enhance_query_success(self):
        """Test successful query enhancement"""
        query = "How can I optimize file1.py?"
        codebase_name = "my_codebase"
        self.mock_models.llm.invoke.return_value = self.mock_enhanced_query_result
        result, code_elements = _enhance_query(query, codebase_name, self.mock_models)
        expected_result = "[my_codebase] Overview of architecture and points of time and memory consumption"
        assert result == expected_result
        assert code_elements == {"source": "file_1.py"}
        self.mock_models.llm.with_structured_output.assert_called_once_with(EnhancedQuery)
        self.mock_models.llm.invoke.assert_called_once()

    def test_enhance_query_exception_handling(self):
        """Test exception handling of _enhance_query"""
        query = "test query"
        codebase_name = "test_codebase"
        self.mock_models.llm.invoke.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            _enhance_query(query, codebase_name, self.mock_models)

    @patch('pyfiles.agents.tools.create_retriever_tool')
    def test_general_retriever_tool_success(
        self, 
        mock_create_retriever_tool
    ):
        """Test successful creation of general retriever tool"""
        self.mock_vectorstore.as_retriever.return_value = self.mock_retriever
        mock_create_retriever_tool.return_value = "mock_tool"
        result = general_retriever_tool(
            vectorstore=self.mock_vectorstore,
            name="test_tool",
            description="Test description",
            expr="test_expr",
            num_results=10
        )
        assert result == "mock_tool"
        self.mock_vectorstore.as_retriever.assert_called_once_with(
            search_kwargs={
                "k": 10,
                "params": {
                    "anns_field": "dense",
                    "topk": 10,
                },
                "sparse_params": {
                    "anns_field": "sparse",
                    "topk": 10, 
                },
                "ranker_type": "weighted", 
                "ranker_params": {"weights": [0.8, 0.2]}, 
                "expr": "test_expr"
            }
        )
        mock_create_retriever_tool.assert_called_once_with(
            self.mock_retriever,
            "test_tool",
            "Test description"
        )

    @patch('pyfiles.agents.tools.create_retriever_tool')
    @patch('pyfiles.agents.tools.logger')
    def test_general_retriever_tool_exception_handling(
        self, 
        mock_logger,
        mock_create_retriever_tool
    ):
        """Test that exceptions in general_retriever_tool"""
        self.mock_vectorstore.as_retriever.side_effect = Exception("Test error")
        with self.assertRaises(Exception):
            general_retriever_tool(
                vectorstore=self.mock_vectorstore,
                name="test_tool",
                description="Test description",
                expr="test_expr",
                num_results=10
            )
        mock_logger.error.assert_called_once()

    def test_enhanced_retriever_success(self):
        """Test that succes of enhanced_retriever_tool"""
        codebase_name = "test_codebase"
        result = enhanced_retriever_tool(self.mock_original_tool, codebase_name, self.mock_models)
        assert hasattr(result, 'name')
        assert hasattr(result, 'func')
        assert hasattr(result, 'coroutine')
        assert hasattr(result, 'description')
        assert hasattr(result, 'args_schema')
        assert result.name == "original_tool"
        assert result.description == "Original tool description"
        assert result.args_schema is None

    @patch('pyfiles.agents.tools._enhance_query')
    def test_enhanced_retriever_tool_exception_handling(
        self, 
        mock_enhance_query
    ):
        """Test that exceptions in enhanced_retriever_tool"""
        codebase_name = "my_codebase"
        mock_enhance_query.side_effect = Exception("Enhancement error")
        result = enhanced_retriever_tool(self.mock_original_tool, codebase_name, self.mock_models)
        assert result is not None
        

    def test_search_input_model_structure(self):
        """Test that EnhancedQuery model has correct structure"""
        query_instance = SearchInputTest(
            query="test query",
            num_results=1
        )
        assert query_instance.query == "test query"
        assert query_instance.num_results == 1       

    @patch('pyfiles.agents.tools.SearxSearchWrapper')
    def test_searx_search_success(
        self, 
        mock_searx_wrapper
    ):
        """Test successful Searx search"""
        query = "test query"
        num_results = 5
        mock_searx_wrapper.return_value = self.mock_wrapper_instance
        self.mock_wrapper_instance.results.return_value = [
            {"title": "Result 1", "url": "http://example.com/1"},
            {"title": "Result 2", "url": "http://example.com/2"}
        ]
        result = _searx_search(query, num_results)
        assert result == [
            {"title": "Result 1", "url": "http://example.com/1"},
            {"title": "Result 2", "url": "http://example.com/2"}
        ]
        mock_searx_wrapper.assert_called_once_with(searx_host=searxng_url)
        self.mock_wrapper_instance.results.assert_called_once_with(query=query, num_results=num_results)

    @patch('pyfiles.agents.tools.SearxSearchWrapper')
    @patch('pyfiles.agents.tools.logger')
    def test_searx_search_exception_handling(
        self, 
        mock_logger, 
        mock_searx_wrapper
    ):
        """Test that exceptions in searx_search"""
        query = "test query"
        num_results = 5
        self.mock_wrapper_instance.results.side_effect = Exception("Search failed")
        mock_searx_wrapper.return_value = self.mock_wrapper_instance
        with self.assertRaises(Exception):
            _searx_search(query, num_results)
        mock_logger.error.assert_called_once()