![GitHub Workflow Status](https://github.com/anima-kit/pycoder/actions/workflows/ci.yml/badge.svg?branch=main) [![codecov](https://codecov.io/gh/anima-kit/pycoder/graph/badge.svg)](https://codecov.io/gh/anima-kit/pycoder)

# PyCoder

![image](https://anima-kit.github.io/pycoder/assets/pycoder.png)

## 🔖 About This Project 

> TL;DR Chat with an agent about Python and Markdown files on your local machine 🤖. 

This repo demonstrates how to set up a [LangChain][langchain]/[LangGraph][langgraph] agent powered by LLMs and tools served locally in [Docker][docker]. An [Ollama][ollama] server is used for local LLMs and embedding models, a [Milvus][milvus] server for creating a vectorstore tool to store and query data, and a [SearXNG][searxng] server for a metasearch engine tool.

The Milvus server is based on the [official Docker setup from Milvus][milvus-docker] and utilizes a [MinIO][minio] server for data storage and an [etcd][etcd] server for storage and coordination. The SearXNG server is based on SearXNG's [searxng-docker repo][searxng-docker] and utilizes a [Caddy][caddy] server for a reverse proxy and a [Valkey][valkey] server (acting through the [Redis][redis] API) for storage.

By connecting these servers to LangChain and LangGraph, we create an agent that can make decisions, generate responses, and use tools to obtain relevant information pertaining to our personal docs or up to date information from the web. We can also interact with the agent and manage our personal docs intuitively with a [Gradio][gradio] web UI.

This project is part of my broader goal to create tutorials and resources for building agents. For more details, [check it out here][animakit].

Now, let's get building!

## 🏁 Getting Started 

1.  Make sure [Docker][docker] is installed and running.

1.  Clone the repo, head there, then create a Python environment:

    ```bash
    git clone https://github.com/anima-kit/pycoder.git
    cd pycoder
    python -m venv venv
    ```

    <a id="gs-activate"></a>

1.  Activate the Python environment:

    ```bash
    venv/Scripts/activate
    ```

1.  Install the necessary Python libraries and create the `.env` file:

    ```bash
    pip install -r requirements.txt
    cp .env.example .env
    ```

1.  Generate a new secret key for the SearXNG server (see the README instructions of the [searxng-docker][searxng-docker] repo for similar methods):

    <details>
    <summary>Windows</summary>

    ```bash
    $key = python -c "import secrets; print(secrets.token_bytes(32).hex())"
    $content = Get-Content .env
    $content = $content -replace 'SEARXNG_SECRET=.*', "SEARXNG_SECRET=$key"
    Set-Content .env $content
    ```
    </details>

    <details>
    <summary>Linux/macOS</summary>

    ```bash
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_bytes(32).hex())")
    sed -i.bak "s/SEARXNG_SECRET=.*/SEARXNG_SECRET=$SECRET_KEY/" .env
    ```
    </details>

    You need to change the secret key from the default `ultrasecretkey` to get the server running properly.

    <a id="gs-start"></a>

1.  Choose to build the Ollama server for GPU or CPU support, then build and run all Docker containers:

    <details>
    <summary>GPU</summary>

    ```bash
    docker compose -f docker-compose-gpu.yml up -d
    ```
    </details>

    <details>
    <summary>CPU</summary>

    ```bash
    docker compose -f docker-compose-cpu.yml up -d
    ```
    </details>

    After successfully completing this step: 
    -  You can check that the Ollama server is running on [http://localhost:11434][ollama-url]. 
    -  The SearXNG server can be used through a web browser by navigating to [http://localhost:8080/][searxng-url]. 
    -  You can head to [http://127.0.0.1:9091/webui/][milvus-webui] to check out some useful Milvus client information.

    <a id="gs-run"></a>

1.  Run the main app:

    ```bash
    python main.py
    ```

    <a id="gs-stop"></a>

1.  When you're done, stop the Docker containers and cleanup with:
    <details>
    <summary>GPU</summary>

    ```bash
    docker compose -f docker-compose-gpu.yml down
    ```
    </details>

    <details>
    <summary>CPU</summary>

    ```bash
    docker compose -f docker-compose-cpu.yml down
    ```
    </details>

## 📝 Example Use Cases 

After setting everything up, you can now use the web UI to manage user profiles and codebases and to chat with agents about your documents. 

The web UI can be utilized to manage different user profiles and codebases by uploading Python or Markdown files. Each user profile can have main codebases for which the agent will have a document retrieval tool. The agent will have access to one main codebase at a time, i.e. the selected main codebase. So, main codebase docs aren't shared between different main codebases. 

Each user can also have some number of external codebases which can be shared across agent sessions for different main codebases. The agent will have a document retrieval tool for each selected external codebase. The agent will also have access to a SearXNG metasearch tool to get up to date or unfamiliar info from the web.

After setting up, for example, you can run the main app, create a user, create a codebase, and chat with the agent about your codebase with the following:

1.  Activate the Python environment ([step 3][step-activate] of the `🏁 Getting Started` section).
1.  Start the Docker containers ([step 6][step-start] of the `🏁 Getting Started` section).
1.  Run the main app ([step 7][step-run] of the `🏁 Getting Started` section).
1.  Navigate to the `Users` tab and create a user named `My Name`.
1.  Select the `My_Name` user.
1.  Navigate to the `Docs` tab and create a codebase named `PyCoder`. 
1.  Navigate to the `Docs/Codebase Details` tab and upload the README.md of this repo.
1.  Navigate to the `Chats` tab and input a message to the agent: `Summarize my main docs`


## 🛠️ Next Steps

This project can be improved in many ways. I used it mostly as a means of learning how to create agent apps from start to finish, and I learned many things out of order, so the code is a bit chaotic. 

Some of the ways to improve this app:

- Agents: 
    - Can update to use the new LangChain `create_agent` from langchain v1.0.
    - Cleanup and separation of AI responses can be improved (should cover more situations, especially when code contains <think></think> tags)

- Agent prompts:
    - All agent prompts can be improved (system prompt for agent to get response for user's query; enhancing user's query for better information retrieval)
    - Can create functionality for user to add their own system prompts. 
    - Can add more to user profiles which can be translated to more informative agent prompt (user's preferred libraries, methods for coding, template files, etc.)

- Doc retrieval
    - Can create summary docs for codebases/codebase docs for better information retrieval
    - Can add functionality to obtain entire file instead of snippets so that code files can be edited more easily 
    - Can add more embedding models to get an ensemble type method for better search retrieval 
    - Update to PyMilvus 2.6 - not working with current structure

- Doc processing 
    - Markdown and General docs creaters can be improved with more metadata and more informed splitting
    - Python splitter has lots of metadata that isn't currently being utilized for doc retrieval 
    - Can add a web loader to create docs from URLs

- Tools:
    - Can use MilvusRetriever instead of `create_retriever_tool`
    - Can cleanup output from LangChain's SearxSearchWrapper's results
    - SearxSearchWrapper is part of `langchain-community` which (I think) won't be maintained with new langchain v1.0, can update to newer functionality 
    - Can add file system tools 
    - Can add code sandbox and interpreter 

- Code structure:
    - Replan the structures of the `docs_handler`, `codebases`, `threads`, `users`, and ui files for cleaner implementations.

- UI
    - Status messages can be handled for many more executions.
    - Can display external codebases, LLM being used, tools being used. 
    - Can toggle metasearch tool use. 

- Tests
    - Coverage is pretty low.

## 📚 Learning Resources 

This project is part of a series on building AI agents. For a deeper dive, [check out my tutorials][tutorials]. Topics include:

- Setting up local servers to power the agent (like the ones built here)
- Example agent workflows (simple chatbots to specialized agents)
- Implementing complex RAG techniques
- Discussing various aspects of AI beyond agents

Want to learn how to expand this setup? [Visit my portfolio][animakit] to explore more tutorials and projects!

## 🏯 Project Structure

```
├── Caddyfile               # Caddy reverse proxy configuration
├── docker-compose-cpu.yml  # Docker settings for CPU build
├── docker-compose-gpu.yml  # Docker settings for GPU build      
├── pyfiles/                # Python source code for main app
├── requirements.txt        # Required Python libraries for main app
├── requirements-dev.txt    # Required Python libraries for development
├── searxng/                # SearXNG configuration directory
│   └── limiter.toml        # Bot protection and rate limiting settings
│   └── settings.yml        # Further custom SearXNG settings
├── tests/                  # Testing suite
├── third-party/            # Third-party licensing
└── .env.example            # Custom environment variables for servers
```

## ⚙️ Tech 

- [aiosqlite][aiosqlite]: Asynchronous SQLite3
- [Caddy][caddy]: Reverse proxy for SearXNG server
- [Docker][docker]: Building and running local servers
- [Gradio][gradio]: Web UI
- [gradio-modal][gradio-modal]: Confirmation pop up windows
- [LangChain][langchain]: Creating tools and agent resources
- [LangGraph][langgraph]: Creating agents
- [Milvus][milvus]: Local vectorstore setup and run in Docker
- [Ollama][ollama]: Local LLM and embedding server setup and run in Docker
- [Ollama Python library][ollama-python]: Interacting with the Ollama server
- [PyMilvus][pymilvus]: Interacting with the Milvus server
- [Python-Markdown][python-markdown]: Processing Markdown files with LangChain
- [SearXNG][searxng]: Metasearch engine
- [searxng-docker][searxng-docker]: Local metasearch engine setup and run in Docker
- [unstructured][unstructured]: Processing Markdown files with LangChain
- [Valkey][valkey] (acting through the [Redis][redis] API): Data storage for SearXNG server

## 🔗 Contributing 

This repo is a work in progress. If you'd like to suggest or add improvements, fix bugs or typos etc., feel free to contribute. Check out the [contributing guidelines][contributing] to get started.

<a id="license-section"></a>

## 📑 License

The Docker setup for this repo is heavily based on the [searxng-docker][searxng-docker] repo and is [licensed under AGPL3][license] in accordance with the [original license][searxng-docker-license].


[aiosqlite]: https://github.com/omnilib/aiosqlite
[animakit]: http://anima-kit.github.io/
[caddy]: https://caddyserver.com/
[contributing]: CONTRIBUTING.md
[docker]: https://www.docker.com/
[etcd]: https://etcd.io/
[gradio]: https://www.gradio.app/
[gradio-modal]: https://pypi.org/project/gradio-modal/
[langchain]: https://www.langchain.com/
[langgraph]: https://www.langchain.com/langgraph/
[license]: LICENSE
[milvus]: https://milvus.io/
[milvus-docker]: https://github.com/milvus-io/milvus/releases
[milvus-webui]: http://127.0.0.1:9091/webui/
[minio]: https://www.min.io/
[ollama]: https://ollama.com/
[ollama-python]: https://github.com/ollama/ollama-python/
[ollama-url]: http://localhost:11434/
[pymilvus]: https://github.com/milvus-io/pymilvus
[python-markdown]: https://github.com/Python-Markdown/markdown
[redis]: https://redis.io/
[searxng]: https://docs.searxng.org/
[searxng-docker]: https://github.com/searxng/searxng-docker/tree/master
[searxng-docker-license]: third-party/searxng-docker-LICENSE
[searxng-url]: http://127.0.0.1:8080/
[step-activate]: https://github.com/anima-kit/pycoder/blob/main/README.md#gs-activate
[step-run]: https://github.com/anima-kit/pycoder/blob/main/README.md#gs-run
[step-start]: https://github.com/anima-kit/pycoder/blob/main/README.md#gs-start
[step-stop]: https://github.com/anima-kit/pycoder/blob/main/README.md#gs-stop
[tutorials]: https://anima-kit.github.io/tutorials/
[unstructured]: https://github.com/Unstructured-IO/unstructured
[valkey]: https://valkey.io/