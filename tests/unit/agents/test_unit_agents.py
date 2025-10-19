### tests.unit.agents.test_unit_agents
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock, call
from pyfiles.agents.agent import Agent

model_name = 'model-name'

class TestAgentsUnitAsync(IsolatedAsyncioTestCase):  
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_threads = MagicMock()
        self.mock_threads.load_all_from_sqlite = AsyncMock()
        self.mock_threads.sqlite_db = MagicMock()
        self.mock_threads.sqlite_db.insert_documents = AsyncMock()
        self.mock_models = MagicMock()
        self.agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        self.agent._get_checkpoint_state = MagicMock()
        self.agent.agent.update_state = MagicMock()

    @patch('pyfiles.agents.agent.logger')
    async def test_update_current_state_success(
        self, 
        mock_logger
    ):
        """
        Test successful of _update_current_state.
        """
        self.mock_threads.load_all_from_sqlite.return_value = {
            "test_thread": {
                "source": "source_1",
                "group": "group_1",
                "content": """[{
                    "role": "user", 
                    "content": "Hello", 
                    "metadata": {"key": "value"}
                }, {
                    "role": "assistant", "content": "Hi there!", "metadata": {}
                }]
                """
            }
        }
        self.agent._get_checkpoint_state.return_value = (
            {"thread_id": "test_thread"},
            {"messages": []}
        )
        result = await self.agent._update_current_state(
            query="Hello",
            selected_thread="test_thread",
            mode="main"
        )
        self.assertEqual(result[0], "Hello") 
        self.assertIsInstance(result[1], list) 
        self.assertEqual(result[2], "source_1") 
        self.assertEqual(result[3], "group_1")
        self.agent.agent.update_state.assert_called_once()
  
    async def test_update_current_state_exception(self):
        """
        Test exception handling in _update_current_state
        """
        self.agent._get_checkpoint_state.side_effect = Exception("Error")
        with self.assertRaises(Exception):
            await agent._update_current_state(query="query", selected_thread="thread")

    @patch('pyfiles.agents.agent.logger')
    async def test_update_current_state_retry_mode(
        self,
        mock_logger
    ):
        """
        Test retry mode in _update_current_state.
        """
        self.mock_threads.load_all_from_sqlite.return_value = {
            "test_thread": {
                "source": "source_1",
                "group": "group_1",
                "content": """[{
                    "role": "user", 
                    "content": "Hello", 
                    "metadata": {"key": "value"}
                }, {
                    "role": "assistant", 
                    "content": "Hi there!", 
                    "metadata": {}
                }]"""
            }
        }
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        agent._get_checkpoint_state = MagicMock()
        agent._get_checkpoint_state.return_value = (
            {"thread_id": "test_thread"}, 
            {"messages": []}
        )
        agent.agent.update_state = MagicMock()
        result = await agent._update_current_state(
            query="Hello",
            selected_thread="test_thread",
            mode="retry"
        )
        self.assertEqual(result[0], "Hello") 
        self.assertIsInstance(result[1], list) 
        self.assertEqual(result[2], "source_1") 
        self.assertEqual(result[3], "group_1")

    @patch('pyfiles.agents.agent.logger')
    async def test_update_current_state_undo_mode(
        self,
        mock_logger
    ):
        """
        Test undo mode in _update_current_state.
        """
        self.mock_threads.load_all_from_sqlite.return_value = {
            "test_thread": {
                "source": "source_1",
                "group": "group_1",
                "content": """[{
                    "role": "user", 
                    "content": "Hello", 
                    "metadata": {"key": "value"}
                }, {
                    "role": "assistant", 
                    "content": "Hi there!", 
                    "metadata": {}
                }]"""
            }
        }
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        agent._get_checkpoint_state = MagicMock()
        agent._get_checkpoint_state.return_value = (
            {"thread_id": "test_thread"}, 
            {"messages": []}
        )
        agent.agent.update_state = MagicMock()
        result = await agent._update_current_state(
            query="Hello",
            selected_thread="test_thread",
            mode="undo"
        )
        self.assertEqual(result[0], "") 
        self.assertIsInstance(result[1], list) 
        self.assertEqual(result[2], "source_1") 
        self.assertEqual(result[3], "group_1")

    @patch('pyfiles.agents.agent.logger')
    async def test_update_current_state_edit_mode(
        self,
        mock_logger
    ):
        """
        Test edit mode in _update_current_state.
        """
        self.mock_threads.load_all_from_sqlite.return_value = {
            "test_thread": {
                "source": "source_1",
                "group": "group_1",
                "content": """[{
                    "role": "user", 
                    "content": "Hello", 
                    "metadata": {"key": "value"}
                }, {
                    "role": "assistant", 
                    "content": "Hi there!", 
                    "metadata": {}
                }]"""
            }
        }
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        agent._get_checkpoint_state = MagicMock()
        agent._get_checkpoint_state.return_value = (
            {"thread_id": "test_thread"}, 
            {"messages": []}
        )
        agent.agent.update_state = MagicMock()
        edit_data = MagicMock()
        edit_data.value = "Edited message"
        edit_data.index = 1
        result = await agent._update_current_state(
            query="Hello",
            selected_thread="test_thread",
            mode="edit",
            edit_data=edit_data
        )
        self.assertEqual(result[0], "Edited message") 
        self.assertIsInstance(result[1], list) 
        self.assertEqual(result[2], "source_1") 
        self.assertEqual(result[3], "group_1")

    async def test_astream_response_empty_query(self):
        """
        Test _astream_response with empty query.
        """
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = []
        async for item in agent._astream_response([], "", "test_thread"):
            result.append(item)
        self.assertEqual(result, [])

    @patch('pyfiles.agents.agent.logger')
    async def test_update_thread_history_success(
        self,
        mock_logger
    ):
        """
        Test success of _update_thread_history
        """
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = await agent._update_thread_history(
            [{"role": "user", "content": "Test transcript"}],
            'group',
            'source',
            "test_thread"
        )
        self.mock_threads.sqlite_db.insert_documents.assert_called_once()
    
    @patch('pyfiles.agents.models.Models')
    @patch('pyfiles.bases.threads.Threads')
    async def test_update_thread_history_exception(
        self,
        mock_threads,
        mock_models
    ):
        """
        Test exception handling in _update_thread_history
        """
        mock_threads.sqlite_db.insert_documents = AsyncMock()
        mock_threads.sqlite_db.insert_documents.side_effect = Exception("Database error")
        agent = Agent(
            models=mock_models,
            tools=[],
            codebase=mock_threads
        )
        with self.assertRaises(Exception):
            await agent._update_thread_history(
                [{"role": "user", "content": "Test transcript"}],
                'group',
                'source',
                "test_thread"
            )
    
    async def test_aget_agent_response_exception(self):
        """
        Test exception handling in aget_agent_response
        """
        self.mock_threads.load_all_from_sqlite.side_effect = Exception("Database error")
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        with self.assertRaises(Exception):
            async for response in agent.aget_agent_response(
                "Test query", 
                "test_thread", 
                [], 
                mode="main"
            ):
                pass

class TestAgentsUnit(TestCase):   
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_threads = MagicMock()
        self.mock_threads.load_all_from_sqlite = AsyncMock()
        self.mock_threads.sqlite_db = MagicMock()
        self.mock_threads.sqlite_db.insert_documents = AsyncMock()
        self.mock_models = MagicMock()

    @patch('pyfiles.agents.agent.ChatPromptTemplate.from_messages')
    @patch('pyfiles.agents.agent.create_react_agent')
    @patch('pyfiles.agents.code_agent_prompt.prompt')
    def test_init_agent_success(
        self,
        mock_code_prompt, 
        mock_react_agent, 
        mock_prompt
    ):
        """
        Test success of _init_agent
        """
        mock_code_prompt.return_value = "test prompt"
        mock_prompt.return_value = MagicMock()
        mock_agent = MagicMock()
        mock_react_agent.return_value = mock_agent
        agent = Agent(
            codebase=self.mock_threads,
            models=self.mock_models,
            tools=[]
        )
        self.assertEqual(agent.agent, mock_agent)

    @patch('pyfiles.agents.code_agent_prompt.prompt')
    def test_init_agent_exception(
        self, 
        mock_code_prompt
    ):
        """
        Test exception handling of _init_agent
        """
        mock_code_prompt.side_effect = Exception("Init failed")
        with self.assertRaises(Exception):
            Agent(
                codebase=self.mock_threads,
                models=self.mock_models,
                tools=[]
            )

    def test_get_checkpoint_state_success(self):
        """
        Test success of _get_checkpoint_state
        """
        agent_instance = Agent(
            codebase=self.mock_threads,
            models=self.mock_models,
            tools=[]
        )
        agent_instance.agent.checkpointer.get = MagicMock()
        agent_instance.agent.checkpointer.get.return_value = {"channel_values": {"messages": []}}
        config, state = agent_instance._get_checkpoint_state(thread_id="test_thread")
        self.assertEqual(config["configurable"]["thread_id"], "test_thread")
        self.assertIsNotNone(state)

    def test_get_checkpoint_state_exception(self):
        """
        Test exception handling of _get_checkpoint_state
        """
        agent_instance = Agent(
            codebase=self.mock_threads,
            models=self.mock_models,
            tools=[]
        )
        agent_instance.agent.checkpointer.get = MagicMock()
        agent_instance.agent.checkpointer.get.side_effect = Exception("Checkpoint error")
        with self.assertRaises(Exception):
            agent_instance._get_checkpoint_state(thread_id="test_thread")

    def test_get_checkpoint_state_no_checkpoint(self):
        """
        Test _get_checkpoint_state with no checkpoint.
        """
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        agent.agent.checkpointer = None
        result = agent._get_checkpoint_state("test_thread")
        self.assertIsInstance(result[0], dict) 
        self.assertIsNone(result[1])

    def test_separate_messages_success(self):
        """
        Text success of _separate_ai_messages
        """
        text = "<think>Some context</think> This is actual content."
        client = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = client._separate_ai_messages(text)
        self.assertEqual(result, ("Some context", "This is actual content."))

    def test_separate_messages_none_input(self):
        """Test exception handling of _separate_ai_messages"""
        client = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        with self.assertRaises(ValueError):
            client._separate_ai_messages(None)

    def test_separate_messages_only_opening(self):
        """
        Text _separate_ai_messages with only one opening tag
        """
        text = "<think> Some content"
        client = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = client._separate_ai_messages(text)
        self.assertEqual(result, ("", "Some content"))

    def test_separate_messages_only_closing(self):
        """
        Text _separate_ai_messages with only one closing tag
        """
        text = "Some content </think>"
        client = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = client._separate_ai_messages(text)
        self.assertEqual(result, ("", "Some content </think>"))

    def test_separate_messages_multiple_closed(self):
        """
        Text _separate_ai_messages with multiple closed tags
        """
        text = "<think>First</think> and <think>Second</think>"
        client = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = client._separate_ai_messages(text)
        self.assertEqual(result, ("First", "and"))

    def test_separate_messages_closed_and_opening(self):
        """
        Text _separate_ai_messages with closed and one opening tags
        """
        text = "<think>First</think> and <think>"
        client = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = client._separate_ai_messages(text)
        self.assertEqual(result, ("First", "and <think>"))

    def test_separate_messages_closed_and_closing(self):
        """
        Text _separate_ai_messages with closed and one closing tags
        """
        text = "<think>First</think> and </think>"
        client = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = client._separate_ai_messages(text)
        self.assertEqual(result, ("First", "and </think>"))

    def test_separate_ai_messages_no_tags(self):
        """
        Test _separate_ai_messages with no tags.
        """
        agent = Agent(
            models=self.mock_models,
            tools=[],
            codebase=self.mock_threads
        )
        result = agent._separate_ai_messages("No tags here")
        self.assertEqual(result[0], "") 
        self.assertEqual(result[1], "No tags here")