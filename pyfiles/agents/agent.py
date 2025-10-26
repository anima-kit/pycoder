### pyfiles.agents.agent
## This file creates the agent with given models and tools and takes care of response generation for different chat modes.
## The agent is initialized for a given codebase which determines the Milvus vectorstore and SQLite DB to use for information retrieval and conversation history update.
## The user can interact with the agent through the different modes:
##     `main`:  The user submits a specific message to the agent and it responds. 
#               All user, agent, and tool messages are saved.
##     `retry`: The user retries the most recent agent response. 
#               All agent and tool messages are saved.
##     `undo`:  All messages up to and including the most recent user message are deleted.
##     `edit`:  The user edits one of their messages and deletes all messages after that. 
#               The agent responds to the new message, and all user, agent, and tool messages are saved.
##
## Get an agent response is as follows:
##     1. The existing conversation history is truncated if greater than a max amount then is updated based on the chat mode. 
##        The agent's memory is loaded with this history (if chat mode in [`main`, `retry`, `edit`]).
##     2. The agent responds to the given query (if chat mode in [`main`, `retry`, `edit`]).
##     3. The response is separated into agent and tool messages for presentation.
##     4. The conversation is history is updated to include any new responses (if chat mode in [`main`, `retry`, `edit`]).
##     5. All new responses generated are streamed.

## External imports
from json import loads, dumps
from re import search, sub, DOTALL, Match
from langgraph.checkpoint.base import BaseCheckpointSaver, Checkpoint
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
## TODO: Update to use langchain.agents create_react_agent
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableConfig
from langchain_classic.schema import Document
from langchain_core.tools.simple import Tool
from langchain_core.tools import StructuredTool
from gradio import EditData
from typing import (
    Any, 
    AsyncIterator, 
    Dict, 
    Hashable, 
    List, 
    Set, 
    Tuple, 
    Collection
)
## Internal imports
from pyfiles.agents import code_agent_prompt
from pyfiles.agents.models import Models
from pyfiles.bases.logger import logger
from pyfiles.bases.threads import Threads
from pyfiles.docs.general_splitter import GeneralSplitter


## The agent class
class Agent:
    """
    An Agent that can be used to create, edit, and understand Python codebases.

    The agent is initialized for a given codebase which determines the Milvus vectorstore and SQLite DB to use for information retrieval and conversation history update.
    The user can interact with the agent through the different modes:
        `main`:  The user submits a specific message to the agent and it responds. 
                 All user, agent, and tool messages are saved.
        `retry`: The user retries the most recent agent response. 
                  All agent and tool messages are saved.
        `undo`:  All messages up to and including the most recent user message are deleted.
        `edit`:  The user edits one of their messages and deletes all messages after that. 
                 The agent responds to the new message, and all user, agent, and tool messages are saved.
    
    Get an agent response is as follows:
        1. The existing conversation history is truncated if greater than a max amount then is updated based on the chat mode. 
           The agent's memory is loaded with this history (if chat mode in [`main`, `retry`, `edit`]).
        2. The agent responds to the given query (if chat mode in [`main`, `retry`, `edit`]).
        3. The response is separated into agent and tool messages for presentation.
        4. The conversation is history is updated to include any new responses (if chat mode in [`main`, `retry`, `edit`]).
        5. All new responses generated are streamed.

    Attributes
    ------------
        codebase: Threads
            The Threads manager that handles chat and document creation.
        models: Models
            The Models manager that handle the LLM and embedding model from Ollama.
        tools: Tools
            The list of tools
            This includes a SearxSearchWrapper tool for searching the internet,
            a Milvus vectorstore retrieval tool for searching the user's main codebase,
            a number of Milvus vectorstore retrievals tools for searching the user's external codebases.
    """
    def __init__(
        self, 
        codebase: Threads, 
        models: Models, 
        tools: List[Tool | StructuredTool]
    ):
        """
        Initialize the Agent for the given Threads manager, Models manager, and list of tools.
        
        Args
        ------------
            codebase: Threads
                The Threads manager.
            models: Models
                The Models manager.
            tools: Tools
                The list of tools.
            
        Raises
        ------------
            Exception: 
                If initialization fails, error is logged and raised.
        """
        try:
            logger.info(f'⚙️ Initializing Agent')
            self.models = models
            self.tools = tools
            self.codebase = codebase
            ## Create a LangGraph react agent
            self.agent: CompiledStateGraph = self._init_agent()
            logger.info(f'✅ Successfully initialized Agent.')
            logger.info(f'📝 Agent using model {self.models.llm_name}.')
            tool_names = [tool.name for tool in self.tools]
            logger.info(f'📝 Agent using tools {tool_names}.')
        except Exception as e:
            logger.error(f'❌ Problem initializng Agent {str(e)}')
            raise

    ## Create the agent
    def _init_agent(
        self
    ) -> CompiledStateGraph:
        """
        Create the agent from LangGraph's `create_react_agent`.

        Returns
        ------------
            CompiledStateGraph: 
                The `create_react_agent` instance.
            
        Raises
        ------------
            Exception: 
                If initialization fails, error is logged and raised.
        """
        try:
            ## Get the system prompt for the given user and selected codebase
            system_prompt: str = code_agent_prompt.prompt(
                user_name=self.codebase.milvus_db.db_name, 
                user_codebase=self.codebase.codebase
            )
            ## Create the prompt template for the agent
            prompt: ChatPromptTemplate = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("messages"),
                ("placeholder", "{agent_scratchpad}")
            ])
            ## Create memory persistence throughout the session
            checkpointer: MemorySaver = MemorySaver()
            return create_react_agent(self.models.llm, self.tools, prompt=prompt, checkpointer=checkpointer)
        except Exception as e:
            logger.error(f'❌ Problem creating Agent: `{str(e)}`')
            raise

    ## Cleanup agent messages
    def _separate_ai_messages(
        self, 
        text: str
    ) -> Tuple[str, str]:
        """
        Extract content within <think></think> tags and separate it from the rest of the text.
        
        Args
        ------------
            text: str 
                Input string containing potential <think></think> tags.
            
        Returns
        ------------
            Tuple[str, str]: 
                A tuple containing (inside_tags, outside_tags) where:
                    inside_tags: Extracted content from within <think></think> tags.
                    outside_tags: Text outside the <think></think> tags.
                
        Raises
        ------------
            Exception: 
                If cleaning the text fails, error is logged and raised.
        """
        ## Check that the text exists
        if text is None:
            error_message: str = '❌ Argument `text` should not be None.'
            logger.error(error_message)
            raise ValueError(error_message)
        try:
            ## Check if there's a closed <think>...</think>
            _match: Match[str] | None = search(r'<think>(.*?)</think>', text, flags=DOTALL)
            # if matched and closed, set inside tags to inside content
            inside_tags: str = _match.group(1).strip() if _match else ''

            ## If the thinking phase isn't fully closed
            if not _match:
                # Try to find a <think> without its closing tag
                # TODO: Do the same for only </think> tag
                start_match: Match[str] | None = search(r'<think>', text)
                # If <think> tag found
                if start_match:
                    inside_content_start: int = start_match.end()
                    inside_content: str = text[inside_content_start:].strip()
                    # Split content by first newline
                    # TODO: Will thinking and response phase always be separated by first new line?
                    lines: List[str] = inside_content.split('\n', 1)
                    # If there's a newline
                    if len(lines) > 1:
                        # Separate the inside and outside tags by the new line
                        inside_tags = lines[0].strip()
                        outside_tags: str = lines[1].strip()
                    # No newline found
                    else:
                        # Just put everything in outside tags
                        inside_tags = ''
                        outside_tags = inside_content.strip()
                # No <think> tag at all
                else:
                    # Return full text as outside
                    inside_tags = ''
                    outside_tags = text

            # If matched and closed
            else:
                # Take outside tags as content outside
                outside_tags = sub(r'\s*<think>.*?</think>\s*', '', text, flags=DOTALL)
                outside_tags = outside_tags.strip()
                # TODO: Should also check for leftover tags
            return inside_tags, outside_tags
        except Exception as e:
            logger.error(f'❌ Problem separating cleaning text: `{str(e)}`')
            raise

    ## Get agent checkpoint
    def _get_checkpoint_state(
        self, 
        thread_id: str
    ) -> Tuple[RunnableConfig, Checkpoint | None]:
        """
        Get the agent's checkpoint state for the given thread.
        
        Args
        ------------
            thread_id: str 
                The ID of the thread state to get.
            
        Returns
        ------------
            Tuple[RunnableConfig, Checkpoint | None]: 
                A tuple containing (the agent's runnable thread configurable, the agent's checkpointer)
                
        Raises
        ------------
            Exception: 
                If getting the agent's checkpoint state fails, error is logged and raised.
        """
        try:
            ## Get the config and checkpoint to pass to the agent for memory
            config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
            current_checkpoint: bool | BaseCheckpointSaver[Any] | None = self.agent.checkpointer
            # If the agent's checkpoint exists
            if isinstance(current_checkpoint, BaseCheckpointSaver):
                # Retrieve current state from the checkpointer
                current_state: Checkpoint | None = current_checkpoint.get(config)                
                return config, current_state
            # If the agent's checkpoint doesn't exist
            else:
                # Return the config with a warning   
                logger.warning(f'⚠️ Successfully got thread configurable, but no agent checkpoint available.')  
                return config, None
        except Exception as e:
            logger.error(f'❌ Problem getting agent checkpoint: `{str(e)}`')
            raise

    ## Update the agent state
    async def _update_current_state(
        self, 
        query: str,
        selected_thread: str, 
        mode: str = "main", 
        edit_data: EditData | None = None
    ) -> Tuple[str, List[Dict[str, Any]], str, str]:
        """
        Update the conversation history state with the current conversation history.
        The convo history is truncated to 10 messages then edited according to the chat mode.
        The agent's state is updated if the chat mode is `main`, `retry`, or `edit`.
        
        Args
        ------------
            selected_thread: str 
                The thread containing the current chat history.
            mode: str
                The chat mode. 
            edit_data (Optional): EditData | None
                Data containing the index of the message to edit and the new value of the message for `edit` mode.
            
        Returns
        ------------
            str: 
                The new query for modes `retry`, and `edit`.
                
        Raises
        ------------
            Exception: 
                If updated the conversation state fails, error is logged and raised.
        """
        try:
            ## Get the thread configurable and the current checkpoint state
            config, current_state = self._get_checkpoint_state(thread_id=selected_thread)
            ## Get the conversation history from the SQLite DB
            thread_state: Dict[str, Dict[str, str]] = await self.codebase.load_all_from_sqlite(load_type="threads")
            existing_thread: Dict[str, str] = thread_state.get(selected_thread, {})
            source = existing_thread['source']
            group = existing_thread['group']
            ## Reverse the history for truncation
            existing_convo: List[Dict[str, Any]] = list(reversed(loads(existing_thread['content'])))
            converted_convo: List[BaseMessage] = []
            counting_messages: int = 0
            ## Loop through the messages and standardize them
            for msg in existing_convo:
                if isinstance(msg, dict):
                    role: Any | None = msg.get("role")
                    content: Any | None = msg.get("content")
                    metadata: Any | None = msg.get("metadata")
                    if role == "user":
                        converted_convo.append(HumanMessage(
                            content=str(content),
                            response_metadata=metadata
                        ))
                    elif role == "assistant":
                        converted_convo.append(AIMessage(
                            content=str(content), 
                            response_metadata=metadata
                        ))
                elif isinstance(msg, (HumanMessage, AIMessage)):
                    converted_convo.append(msg)
                ## Break the loop of past the threshold
                counting_messages += 1
                if counting_messages == 10:
                    break
            ## Reverse the conversation history back
            converted_convo = list(reversed(converted_convo))   

            ## Handle different modes for modifying the convo
            # For modes other than 'main', need to truncate chat convo and set new query if applicable 
            if converted_convo:
                ## Retry and Undo Modes
                if mode in ["retry", "undo"]:
                    # Find the index of the latest user message to truncate convo up to that point
                    latest_index: int | None = None
                    for idx, item in enumerate(converted_convo):
                        if isinstance(item, HumanMessage):
                            latest_index = idx
                    # For 'retry' mode, set new query to pass to agent
                    if mode=='retry':
                        if latest_index != None:
                            query = str(converted_convo[latest_index].content)
                    elif mode=='undo':
                        query=''
                    # Then truncate chat convo for both modes
                    converted_convo = converted_convo[:latest_index]

                ## Edit Mode
                elif mode == "edit":
                    # Set new query and truncate chat convo
                    # New query will be edit_data.value and index of message will be edit_data.index
                    if edit_data:
                        query = edit_data.value
                        if isinstance(edit_data.index, int):
                            converted_convo = converted_convo[:edit_data.index]

                ## Update the agent state if need to get new response
                if mode in ['retry', 'edit', 'main']:
                    self.agent.update_state(config, {"messages": converted_convo})
                
            ## Convert back for chatbot transcript
            transcript: List[Dict[str, Any]] = []
            for msg in converted_convo:
                if isinstance(msg, HumanMessage):
                    transcript.extend([{
                        'role': 'user',                   
                        'content': msg.content, 
                        'metadata': msg.response_metadata
                    }])
                elif isinstance(msg, AIMessage):
                    transcript.extend([{
                        'role': 'assistant',                   
                        'content': msg.content, 
                        'metadata': msg.response_metadata
                    }])

            if query:
                transcript.extend([{
                    "role": "user", 
                    "content": query,
                    "metadata": {"title": "User Message"}
                }])
            return (
                query, 
                transcript, 
                source, 
                group
            )
        except Exception as e:
            logger.error(f'❌ Problem updating conversation history state: `{str(e)}`')
            raise

    ## Stream the agent response
    async def _astream_response(
        self, 
        transcript: List[Dict[str, Any]],
        query: str | None, 
        selected_thread: str
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Stream the agent response asynchronously.
        Each different response type (ToolMessage, AIMessage) is separated for better presentation.
        
        Args
        ------------
            query: str
                The query with which to invoke the agent.
            selected_thread: str 
                The thread containing the current chat history.
            
        Returns
        ------------
            AsyncIterator[List[dict]]: 
                A list of response dictionaries.
                
        Raises
        ------------
            Exception: 
                If streaming the agent response fails, error is logged and raised.
        """
        try:
            ## If query is empty, don't get any agent response 
            if query:
                ## Standardize the user message and add it to the response
                content: str = query if isinstance(query, str) else str(query)
                human_message: HumanMessage = HumanMessage(content=content)
                messages: List[HumanMessage] = [human_message]

                # Get agent checkpoint state
                config, current_state = self._get_checkpoint_state(thread_id=selected_thread)
                # Keep track of existing messages
                existing_messages_count: int = len(current_state['channel_values']["messages"]) if current_state else 0
                processed_hashes: Set = set()

                async for step in self.agent.astream(
                    {"messages": messages},
                    config=config,
                    stream_mode="values"
                ):
                    if step.get("messages"):
                        current_messages: List[BaseMessage] = step["messages"]
                        new_messages: List[BaseMessage] = current_messages[existing_messages_count:]
                        valid_new_messages: List[BaseMessage] = [
                            msg for msg in new_messages
                            if not (isinstance(msg, HumanMessage) and msg.content == human_message.content)
                        ]

                        for content_part in valid_new_messages:
                            # Keep track of existing messages
                            msg_hash: Hashable = hash((type(content_part), content_part.content))
                            if msg_hash in processed_hashes:
                                continue
                            processed_hashes.add(msg_hash)

                            ## Get agent messages
                            if isinstance(content_part, AIMessage):
                                if isinstance(content_part.content, str):
                                    # Separate thinking and response phases
                                    inside_tags, outside_tags = self._separate_ai_messages(content_part.content)
                                    if inside_tags!='' and inside_tags!=None:
                                        inside_content: str = inside_tags if isinstance(inside_tags, str) else str(inside_tags)
                                        transcript.append({
                                            "role": "assistant",
                                            "content": inside_content,
                                            "metadata": {"title": "Assistant Thinking...", "status": "done"}
                                        })
                                        yield transcript

                                    if outside_tags!='' and outside_tags!=None:
                                        outside_content: str = outside_tags if isinstance(outside_tags, str) else str(outside_tags)
                                        transcript.append({
                                            "role": "assistant",
                                            "content": outside_content,
                                            "metadata": {"title": "Assistant Message"}
                                        })
                                        yield transcript

                            ## Get Tool messages
                            elif isinstance(content_part, ToolMessage):
                                message_out = f"\nContent from `{content_part.name}` toolcall:\n{content_part.content}"
                                if message_out!='' and message_out!=None:
                                    content = message_out if isinstance(message_out, str) else str(message_out)
                                    transcript.append({
                                        "role": "assistant",
                                        "content": content,
                                        "metadata": {"title": f"Tool call output", "status": "done"}
                                    })
                                    yield transcript
        except Exception as e:
            logger.error(f'❌ Problem streaming agent response: `{str(e)}`')
            raise

    async def _update_thread_history(
        self, 
        transcript: List[Dict[str, Any]],
        group: str,
        source: str,
        selected_thread: str, 
    ) -> None:
        """
        Update the SQLite DB with the new conversation history.
        
        Args
        ------------
            transcript: List[Dict[str, Any]]
                The conversation history to save.
            group: str 
                The value for the `group` metadata.
            source: str 
                The value for the `source` metadata.
            selected_thread: str
                The thread ID to update.
                
        Raises
        ------------
            Exception: 
                If saving the converation history fails, error is logged and raised.
        """
        try:
            ## Create document for updated history
            metadata: Dict[str, str] = {"group": group, "source": source} 
            content: str = dumps(transcript)
            splitter: GeneralSplitter = GeneralSplitter(source=source, content=content)
            doc: Document = splitter._create_document(content)
            doc.metadata = metadata
            ## Update document in SQLite
            await self.codebase.sqlite_db.insert_documents([doc], [selected_thread])
        except Exception as e:
            logger.error(f'❌ Problem updating SQLite DB: `{str(e)}`')
            raise

    async def aget_agent_response(
        self, 
        query: str, 
        selected_thread: str, 
        mode: str = "main", 
        edit_data: EditData | None = None
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Get the agent response.
        This updates the conversation history, loads it into the agent's memory, invokes an agent response, then saves the conversation history to the SQLite DB.
        
        Args
        ------------
            query: str
                The query for the agent response.
            selected_thread: str
                The thread ID to update.
            mode: str
                The chat mode.
                Can be `main`, `retry`, `edit`, `undo`.
            edit_data (Optional): EditData | None
                The data for editing messages in `edit` mode.
                
        Raises
        ------------
            Exception: 
                If get the agent response fails, error is logged and raised.
        """
        try:
            ## Update the conversation state
            # If main mode, don't need a new query
            if mode=="main":
                _, transcript, source, group = await self._update_current_state(
                    query=query,
                    selected_thread=selected_thread, 
                    mode=mode
                )
            # For all other modes
            else:
                query, transcript, source, group = await self._update_current_state(
                    query=query,
                    selected_thread=selected_thread, 
                    mode=mode, 
                    edit_data=edit_data
                )
            # Yield the new conversation history
            yield transcript

            ## Stream the agent response
            response: List[Dict[str, Any]] | None = None
            # Stream each different type of message (AIMessage, ToolMessage)
            async for response in self._astream_response(
                transcript=transcript,
                query=query, 
                selected_thread=selected_thread
            ):
                yield response

            ## Save the conversation history
            await self._update_thread_history(
                transcript=transcript,
                group=group,
                source=source,
                selected_thread=selected_thread
            )
        except Exception as e:
            logger.error(f'❌ Problem executing agent mode: `{str(e)}`')
            raise