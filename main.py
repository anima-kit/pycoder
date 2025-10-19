### main
## This file runs the main Gradio app.
## The user can manange different user profiles (right now just names - but can add preferences and templates).
## Each different user profile can have different main codebases created by uploading Python or Markdown files.
## Each different codebase can have various chat threads where the user can interact with an agent about their codebase files.
## All chat threads for a particular codebase are only associated with that codebase, so the agent won't know about any other main codebases when chatting on these threads.
## The user can select different codebases to chat about that particular codebase.
## Each user profile can also have a number of external codebases or libraries that the user can chat with regardless of the main codebase selected.
## The agent will have access to these external codebases as long as they're selected. 
## The agent is powered by LLMs served in Ollama, a metasearch engine tool served in SearXNG, and codebase retrieval tools served in Milvus all containerized locally in Docker.

### TODO:
## There are so many ways this project can be improved. Here are but a few:

## Code structure:
## I basically learned how to code apps with this project, and did many things out of order. 
## My philosophy was to get something to work, then figure out how it worked and how to apply best practices for CI/CD, so the code is a bit chaotic. 
## If I were to go back, I would replan the structures of the `docs_handler`, `codebases`, `threads`, `users`, and ui files for cleaner implementations.

## Agents:
## Can update to use the new LangChain `create_agent` from langchain v1.0.
## Cleanup and separation of AI responses can be improved (should cover more situations, especially when code contains <think></think> tags)

## Agent prompts:
## All agent prompts can be improved (system prompt for agent to get response for user's query; enhancing user's query for better information retrieval)
## Can create functionality for user to add their own system prompts. 
## Can add more to user profiles which can be translated to more informative agent prompt (user's preferred libraries, methods for coding, template files, etc.)

## Doc retrieval
## Can create summary docs for codebases/codebase docs for better information retrieval
## Can add functionality to obtain entire file instead of snippets so that code files can be edited more easily 
## Can add more embedding models to get an ensemble type method for better search retrieval 
## Update to PyMilvus 2.6.2 - not working with current structure

## Doc processing 
## Markdown and General docs creaters can be improved with more metadata and more informed splitting
## Python splitter has lots of metadata that isn't currently being utilized for doc retrieval 
## Can add a web loader to create docs from URLs

## Tools:
## Can use MilvusRetriever instead of `create_retriever_tool`
## Can cleanup output from LangChain's SearxSearchWrapper's results
## SearxSearchWrapper is part of `langchain-community` which (I think) won't be maintained with new langchain v1.0, can update to newer functionality 
## Can add file system tools 
## Can add code sandbox and interpreter 

## UI
## Status messages can be handled for many more executions.
## Can display external codebases, LLM being used, tools being used. 
## Can toggle metasearch tool use. 

## Tests
## Coverage is pretty low.

## External imports
from asyncio import run
from gradio import Blocks

## Internal imports
from pyfiles.agents.models import Models
from pyfiles.bases.logger import logger
from pyfiles.databases.milvus import MilvusClientStart
from pyfiles.ui.gradio_app import GradioApp
from pyfiles.ui.gradio_config import Config

## Create the main function
async def main(
) -> None:
    """
    Run the Gradio app.
        
    Raises
    ------------
        Exception: 
            If running the main Gradio app fails, error is logged and raised.
    """
    try:
        logger.info('⚙️ Starting application')
        config: Config = Config()
        milvus_client: MilvusClientStart = MilvusClientStart()
        models: Models = Models()
        gradio_app_instance: GradioApp = GradioApp(
            config=config, 
            models=models, 
            milvus_client=milvus_client
        )
        app: Blocks = await gradio_app_instance.app()
        app.launch(
            pwa=True, 
            inbrowser=True, 
            share=False
        )
    except Exception as e:
        logger.error(f'❌ Problem starting application: `{str(e)}`')

if __name__ == "__main__":
    run(main())