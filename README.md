# cmf-mcp-server

A Model Context Protocol (MCP) server for CMF Server. This server exposes CMF Server functionality as tools that can be used by AI assistants.

## Dependencies

### Docker

- [Docker install guide](https://docs.docker.com/engine/install/)

## Environment
Create a `.env` file in the project root with CMF credentials. Follow example.env

## Project Structure

The project follows a modular organization for better maintainability:

```
/
├── main.py                # Main application entry point
├── tools/                 # MCP CMF tools organized by functionality
│   ├── __init__.py
│   ├── pipeline.py        # Pipeline-related tools
|   ├── execution.py       # Execution-related tools
|   ├── artifact.py        # Artifact-related tools
|   ├── additional.oy      # Additional / Miscellaneous tools
├── resources/             # MCP resources
│   ├── __init__.py
│   └── common.py          # Common resources (cmf://, version://)
├── prompts/               # MCP prompts
│   ├── __init__.py
│   └── guide.py           # CMF MCP Guide for LLMs
├── docker-compose.yml     # Docker Compose configuration for production
└── Dockerfile             # Docker build configuration
```

## Running the Server

### Using Docker

```bash
# Standard deployment
docker-compose up --build -d
docker-compose logs -f
```

The server will be available at `http://localhost:8382`

### MCP Inspector

Can run MCP inspector using `uv` and the `mcp` CLI:

```bash
uv run mcp dev main.py
```

This will start an interactive interface at `http://localhost:6274` where tools and resources are tested.

## API

This MCP server exposes the following resources and tools. It can work across one or more CMF servers configured in .env:

### Resources

- `CMF://`: Returns information about all configured CMF Servers
- `version://`: Returns the MCP server version
- `list-tools://`: Returns a list of tool categories
  - `list-tools://{category}`: Returns a list of tools within a specific category

### Tools

Each tool call returns results as a list of dictionaries with the following structure:
```
[
  {
    "CMF": "CMF Name",
    "data": [...]  # Result data from this CMF Server
  },
  ...
]
```

#### Pipeline

- `cmf_show_pipelines`: Lists all Pipelines in CMF server


#### Execution

- `cmf_show_executions`: Lists all executions for a Pipeline in CMF Server
- `cmf_show_execution_detail`: Lists detailed executions for a Pipeline in CMF Server
- `cmf_execution_lineage`: Fetch execution lineage for a `selected_uuid` and `specific_pipeline`

#### Artifact 

- `cmf_show_artifact_types`: Lists all artifact types in CMF Server (across all Pipelines)
- `cmf_show_artifact_detail`: Lists artifact details for a specific `artifact_type` in a `specific_pipeline`
- `cmf_artifact_lineage`: Fetch artifact lineage for a pipeline

#### Addtional 
- `cmf_show_model_card` : Get model card
- `cmf_show_python_env` : Get Python Environment
- `cmf_mlmd_pull` : Fetch mlmd as a file
- `cmf_mlmd_push` : Push mlmd as POST body 


## License
- Apache 2.0 License

## Usage 
- To use in VSCode with properly configured copilot: 
  - Add a .vscode in current project. 
  - Add the following to: `./vscode/mcp.json`
  - VSCode will work only with `tools` in MCP server. It doesn't know how to interprete `resources` and `prompts` yet
    ```
    {
      "servers": {
        "cmf-mcp-server": {
          "type": "sse",
          "url": "http://localhost:8382/sse",
          "headers": { "VERSION": "1.2" }
        }
      }
    }
    ```
- To use in n8n 
- To use in Langflow 
- To use in Claude Desktop
- To use in Cursor 

## Configuration/Setup
- This will read the pyproject.toml file and create requirements.txt
```
  pip install pip-tools
  pip-compile pyproject.toml  
```
- This will read the pyproject.toml file and create a uv.lock file with the locked dependencies.
  ```
  pip install uv
  uv lock
  ```
