### pyfiles.agents.models
## This file creates the LLM and embedding models to be used by the agent and in the document retrieval tools.
## Model management is handled with Ollama (pulling, listing models) and model creation handled with LangChain (ChatOllama, OllamaEmbeddings).

## External imports
from os import getenv
from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import OllamaEmbeddings, ChatOllama
from ollama import (
    Client, 
    ChatResponse, 
    ListResponse,
    ProgressResponse,
    pull
)
from ollama import list as ollama_list
from typing import Dict, List
## Internal imports
from pyfiles.bases.logger import logger, with_spinner

## Get model parameters from environment
load_dotenv()
llm_name: str = getenv("OLLAMA_LLM", "qwen3:0.6b")
embed_name: str = getenv("OLLAMA_EMBED", "nomic-embed-text:latest")
url: str = getenv("OLLAMA_URL", 'http://localhost:11434')

## The models manager class
class Models:
    """
    A models manager class that handles the LLM and embedding model to be used by the agent.

    Management of the models (listing, pulling) is handled with Ollama and creating the LLM and embedding models is handled with LangChain (ChatOllama, OllamaEmbeddings).

    Attributes
    ------------
        llm_name: str
            The name of the LLM to use.
            Defaults to OLLAMA_LLM in environment file or `qwen3:0.6b` if OLLAMA_LLM doesn't exist.
        embed_name: str
            The name of the embedding model to use.
            Defaults to OLLAMA_EMBED in environment file or `nomic-embed-text:latest` if OLLAMA_EMBED doesn't exist.
        url: str
            The Ollama server URL.
            Defaults to OLLAMA_URL in environment file or `http://localhost:11434` if OLLAMA_URL doesn't exist.
        llm: BaseChatModel
            The LLM model to pass to the agent.
        embed: OllamaEmbeddings
            The embedding model to pass to the agent.
    """
    def __init__(
        self, 
        llm_name: str = llm_name, 
        embed_name: str = embed_name, 
        url: str = url
    ):
        """
        Initialize the Models class.

        Args
        ------------
            llm_name: str
                The name of the LLM to use.
                Defaults to OLLAMA_LLM in environment file or `qwen3:0.6b` if OLLAMA_LLM doesn't exist.
            embed_name: str
                The name of the embedding model to use.
                Defaults to OLLAMA_EMBED in environment file or `nomic-embed-text:latest` if OLLAMA_EMBED doesn't exist.
            url: str
                The Ollama server URL.
                Defaults to OLLAMA_URL in environment file or `http://localhost:11434` if OLLAMA_URL doesn't exist.
            
        Raises
        ------------
            Exception: 
                If initializing LLM fails, error is logged and raised.
        """
        try:
            self.llm_name = llm_name
            self.embed_name = embed_name
            self.url = url
            ## Get the LLM and embedding model to pass to agent
            self.llm: BaseChatModel = self._init_llm()
            self.embed: OllamaEmbeddings = self._init_embed()
        except Exception as e:
            logger.error(f'❌ Problem creating models: `{str(e)}`')
            raise
        
    ## Initialize the LLM
    def _init_llm(
        self
    ) -> BaseChatModel:
        """
        Creates the LLM model to be passed to the agent. 
        Pulls the model from Ollama library if not already pulled.

        Returns
        ------------
            BaseChatModel: 
                The base chat model that can be invoked to get a response for a given message.
            
        Raises
        ------------
            Exception: 
                If initializing LLM fails, error is logged and raised.
        """
        logger.info(f'⚙️ Initializing LLM `{self.llm_name}` on URL `{self.url}`')
        ## Check if LLM exists in Ollama library before creating chat model
        try:
            # Check existing models in Ollama
            model_names: List[str | None] = self._list_pulled_models()
            # If `llm_name` not in model_names, pull it from Ollama
            if self.llm_name not in model_names:
                logger.info(f'⚙️ Pulling LLM `{self.llm_name}` from Ollama')
                with with_spinner(description=f"⚙️ Pulling LLM..."):
                    pull(self.llm_name)
                logger.info(f'✅ Successfully pulled LLM `{self.llm_name}`')
        except Exception as e:
            logger.error(f'❌ Problem pulling LLM from Ollama: `{str(e)}`')
            raise 
        ## Create chat model with LangChain
        try:
            # ChatOllama uses requests library to get Ollama response for given LLM through given url
            model: BaseChatModel = ChatOllama(
                model=self.llm_name,    # Use specified LLM model
                temperature=0.5,        # Control response randomness (higher for more variety)
                base_url=self.url       # Specify Ollama server URL (for Docker setup)
            )
            logger.info(f'✅ Using LLM `{self.llm_name}`')
            return model
        except Exception as e:
            logger.error(f'❌ Problem initializing LLM: `{str(e)}`')
            raise

    ## Initialize the embedding
    def _init_embed(
        self
    ) -> OllamaEmbeddings:
        """
        Creates the embedding model to be passed to the agent. 
        Pulls the model from Ollama library if not already pulled.

        Returns
        ------------
            OllamaEmbeddings: 
                The base embedding model to be used for embedding documents.
            
        Raises
        ------------
            Exception: 
                If initializing embedding model fails, error is logged and raised.
        """
        logger.info(f'⚙️ Initializing embed `{self.embed_name}` on URL `{self.url}`')
        ## Check if LLM exists in Ollama library before creating chat model
        try:
            # Check existing models in Ollama
            model_names: List[str | None] = self._list_pulled_models()
            # If `llm_name` not in model_names, pull it from Ollama
            if self.embed_name not in model_names:
                logger.info(f'⚙️ Pulling embed `{self.embed_name}` from Ollama')
                with with_spinner(description=f"⚙️ Pulling embed..."):
                    pull(self.embed_name)
                logger.info(f'✅ Successfully pulled embed `{self.embed_name}`')
        except Exception as e:
            logger.error(f'❌ Problem pulling embed from Ollama: `{str(e)}`')
            raise 
        ## Create embed model with LangChain
        try:
            embeddings: OllamaEmbeddings = OllamaEmbeddings(
                model=self.embed_name,
            )
            logger.info(f'✅ Using embed `{self.embed_name}`')
            return embeddings
        except Exception as e:
            logger.error(f'❌ Problem initializing embed `{str(e)}`')
            raise

    ## List models available in Ollama
    def _list_pulled_models(
        self
    ) -> List[str | None]:
        """
        List all models available in Ollama model storage.

        Returns
        ------------
            List[str | None]: 
                A list of all the available models.
            
        Raises
        ------------
            Exception: 
                If getting list fails, error is logged and raised.
        """
        try:
            # List all models available with Ollama
            ollama_models: ListResponse = ollama_list()
            # List all model names
            model_names: List[str | None] = [model.model for model in ollama_models.models]
            logger.info(f'📝 Existing models `{model_names}`')
            return model_names
        except Exception as e:
            logger.error(f'❌ Problem listing models available in Ollama: `{str(e)}`')
            raise