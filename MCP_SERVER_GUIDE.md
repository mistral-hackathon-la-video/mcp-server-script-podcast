# ArXiv Script Generator MCP Server

This MCP (Model Context Protocol) server provides AI-powered script generation capabilities for research papers, converting academic content into engaging video scripts suitable for YouTube and educational content.

## Features

The server exposes the following MCP capabilities:

### Tools

#### `generate_script`
Generates a video script for a research paper using AI models via OpenRouter.

**Parameters:**
- `paper_markdown` (string, required): The research paper content in markdown format
- `paper_id` (string, required): The ArXiv paper ID (e.g., '2405.11273')
- `method` (string, optional): The AI method to use (default: 'openrouter')
- `from_pdf` (boolean, optional): Whether the paper comes from PDF extraction (default: false)

**Returns:** Generated video script as formatted text

#### `echo`
Simple echo tool for testing the MCP connection.

**Parameters:**
- `text` (string): The text to echo

**Returns:** The same text that was provided

### Resources

#### `greeting://{name}`
Get a personalized greeting for a given name.

**Parameters:**
- `name` (string): The name of the person to greet

**Returns:** A personalized greeting message

### Prompts

#### `greet_user`
Generate a greeting prompt for different styles.

**Parameters:**
- `name` (string, required): The name of the person to greet
- `style` (string, optional): The style of greeting ('friendly', 'formal', 'casual')

**Returns:** A prompt for generating greetings

## Setup

### Prerequisites

- Python 3.13 or higher
- `uv` package manager installed
- OpenRouter API key (set as `OPENROUTER_API_KEY` environment variable)

### Core Dependencies

The server uses only essential dependencies for optimal performance:
- `mcp` - Model Context Protocol SDK
- `openai` - OpenAI/OpenRouter API client
- `instructor` - Structured LLM outputs
- `pydantic` - Data validation
- `requests` - HTTP client
- `python-dotenv` - Environment variables

### Installation

1. Navigate to the project directory:
```bash
cd /path/to/podcaster
```

2. Install dependencies using uv:
```bash
uv sync
```

3. Create a `.env` file with your OpenRouter API key:
```bash
echo "OPENROUTER_API_KEY=your_api_key_here" > .env
```

## Running the Server

### Standard I/O Transport (for MCP clients)
```bash
uv run python main.py
```

### HTTP Transport (for web applications)
The server runs on port 3000 by default with stateless HTTP enabled:
```bash
uv run python main.py
```

The server will be available at `http://localhost:3000`

## Usage Examples

### Using with an MCP Client

Once connected to an MCP client, you can use the tools like this:

1. **Generate a script from a research paper:**
```json
{
  "tool": "generate_script",
  "parameters": {
    "paper_markdown": "# Your Research Paper\n\nAbstract: This paper presents...",
    "paper_id": "2405.11273",
    "method": "openrouter",
    "from_pdf": false
  }
}
```

2. **Test the connection:**
```json
{
  "tool": "echo",
  "parameters": {
    "text": "Hello, MCP server!"
  }
}
```

3. **Get a greeting resource:**
```
greeting://Alice
```

4. **Generate a greeting prompt:**
```json
{
  "prompt": "greet_user",
  "parameters": {
    "name": "Bob",
    "style": "friendly"
  }
}
```

### Configuration

The server supports various configuration options through environment variables:

- `OPENROUTER_API_KEY`: Your OpenRouter API key (required)
- `SCRIPGENETOR_MODEL`: The AI model to use for script generation
- `OCR_MODEL`: Model for OCR tasks
- `OCR_PROVIDER`: OCR service provider

## Script Generation Process

The `generate_script` tool uses the following process:

1. **Input Processing**: Takes the paper markdown and paper ID
2. **Link Adjustment**: Processes and corrects image links in the paper
3. **AI Generation**: Uses OpenRouter API with structured output to generate a script
4. **Validation**: Validates the generated script structure using Pydantic models
5. **Formatting**: Returns the script in a readable format

The generated script includes:
- **Title**: Video title derived from the paper
- **Target Duration**: Estimated video length (5-6 minutes)
- **Components**: Structured list of script elements:
  - **Headlines**: Engaging section headers for spoken delivery
  - **Text**: Narrative content for video narration

## Error Handling

The server includes comprehensive error handling:
- Invalid paper IDs are caught and corrected
- API failures are logged and reported
- Malformed scripts are validated and rejected
- Network errors are handled gracefully

## Development

To modify the server:

1. Edit `main.py` for MCP server configuration and tool definitions
2. Edit `generate_script.py` for core script generation logic
3. Update `pyproject.toml` for dependencies
4. Test changes with: `uv run python -c "import main; print('OK')"`

## Troubleshooting

### Common Issues

1. **Import errors**: Run `uv sync` to ensure all dependencies are installed
2. **API key errors**: Check that `OPENROUTER_API_KEY` is set in your `.env` file
3. **Model errors**: Verify your OpenRouter API key has access to the specified model
4. **Port conflicts**: The server uses port 3000 by default; ensure it's available

### Logging

The server runs in debug mode by default, providing detailed logging. Check the console output for error messages and debugging information.

## License

This MCP server is part of the ConversationSimulator/podcaster project.