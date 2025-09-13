# 🎙️ Podcast Generator MCP Server - Deployment Guide

## Overview

This MCP (Model Context Protocol) server provides podcast generation capabilities for Alpic. It can:

1. Generate video scripts from research papers
2. Convert text scripts to audio podcasts using TTS
3. Full pipeline: paper → script → podcast

## 📦 MCP Tools Available

### 1. `generate_script`
Generates video scripts from research papers using AI models.

**Parameters:**
- `paper_markdown` (required): Research paper content in markdown format
- `paper_id` (required): ArXiv paper ID (e.g., '2405.11273')
- `method` (optional): AI method to use (default: 'openrouter')
- `from_pdf` (optional): Whether paper comes from PDF extraction

**Returns:** Formatted script text with `\\Headline:` and `\\Text:` components

### 2. `generate_podcast`
Converts text scripts to audio podcasts using TTS engines.

**Parameters:**
- `script_text` (required): Formatted script text to convert
- `output_filename` (optional): Output filename (default: 'podcast.wav')
- `tts_engine` (optional): TTS engine ('elevenlabs', 'kokoro', 'mixed', 'mock')
- `headline_voice_id` (optional): ElevenLabs voice ID for headlines
- `text_voice_id` (optional): ElevenLabs voice ID for main text
- `sample_rate`, `silence_duration`, `headline_silence`: Audio settings

**Returns:** Status message with file info, duration, and size

### 3. `generate_script_and_podcast`
Complete pipeline combining both tools.

**Parameters:** Combines parameters from both tools above

**Returns:** Status message with both script and podcast information

## 🚀 Deployment Steps

### 1. Dependencies
The server requires these Python packages (already in `pyproject.toml`):

```toml
dependencies = [
    "black>=25.1.0",
    "mcp",
    "python-dotenv>=1.1.0",
    "openai>=1.99.1",
    "instructor>=1.10.0",
    "requests>=2.31.0",
    "pydantic>=2.11.5",
    # Audio processing for podcast generation
    "soundfile>=0.13.1",
    "numpy>=1.24.0",
    "elevenlabs>=2.1.0",
    "kokoro>=0.9.4",
]
```

### 2. Environment Variables (.env file)
Create a `.env` file with these variables:

```bash
# Required for script generation
OPENROUTER_API_KEY=your_openrouter_api_key_here
SCRIPGENETOR_MODEL=google/gemini-2.5-pro

# Required for ElevenLabs TTS (optional - can use mock for testing)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Other optional variables
OCR_MODEL=google/gemini-2.0-flash-001
OCR_PROVIDER=openrouter
# ... (other existing variables)
```

### 3. Deploy to Alpic

1. **Upload Files**: Upload `main.py` and all supporting files to Alpic
2. **Install Dependencies**: Run `uv sync` to install dependencies
3. **Set Environment**: Configure environment variables in Alpic
4. **Start Server**: Deploy `main.py` as an MCP server

## 🧪 Testing

Run the test suite before deployment:

```bash
uv run python test_deployment.py
```

This will test:
- Environment setup and dependencies
- MCP server structure
- Full pipeline functionality

## 🎵 Audio Generation Options

### Mock Audio (Testing)
- Use `tts_engine="mock"` for testing
- Generates pleasant sine wave tones
- No API keys required

### ElevenLabs TTS (Production)
- Use `tts_engine="elevenlabs"` for high-quality speech
- Requires `ELEVENLABS_API_KEY` environment variable
- Default voices:
  - Headlines: Rachel (`21m00Tcm4TlvDq8ikWAM`)
  - Main text: Clyde (`2EiwWnXFnvU5JabPnv8n`)

### Mixed Engine (Recommended)
- Use `tts_engine="mixed"` for best results
- Automatically selects best engine per component
- Falls back gracefully if engines unavailable

## 📋 Usage Examples

### Generate Script Only
```python
# Call generate_script tool
result = await generate_script(
    paper_markdown="# Research Paper Content...",
    paper_id="1706.03762",
    method="openrouter"
)
```

### Generate Podcast Only  
```python
# Call generate_podcast tool
result = await generate_podcast(
    script_text="\\Headline: Introduction\n\\Text: Welcome...",
    output_filename="my_podcast.wav",
    tts_engine="elevenlabs"
)
```

### Full Pipeline
```python
# Call generate_script_and_podcast tool
result = await generate_script_and_podcast(
    paper_markdown="# Research Paper Content...",
    paper_id="1706.03762",
    output_filename="research_podcast.wav",
    tts_engine="mixed"
)
```

## ⚠️ Error Handling

The server includes robust error handling:
- Graceful fallback to mock audio if TTS engines fail
- Detailed error messages for debugging
- Automatic retries for API calls
- Safe parameter extraction from MCP Field objects

## 📊 Performance

Typical processing times:
- Script generation: 10-30 seconds (depends on paper length)
- Audio generation: 1-5 minutes (depends on script length and TTS engine)
- Full pipeline: 2-8 minutes total

## 🔧 Troubleshooting

### Common Issues

1. **"Invalid method" errors**
   - Ensure `method="openrouter"` for script generation
   - Check `OPENROUTER_API_KEY` is set

2. **Constant beeping in audio**
   - Set `ELEVENLABS_API_KEY` for real TTS
   - Or use `tts_engine="mock"` for testing

3. **FieldInfo object errors**
   - The server automatically handles MCP parameter extraction
   - If you see these errors, check MCP tool parameter definitions

### Debug Mode

Enable verbose logging:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## ✅ Deployment Checklist

- [ ] Dependencies installed (`uv sync`)
- [ ] Environment variables configured
- [ ] Test suite passes (`python test_deployment.py`)
- [ ] API keys are valid and have sufficient credits
- [ ] File permissions are correct
- [ ] MCP server starts without errors

## 🎉 Success Indicators

When deployed successfully, you should see:
- MCP server starts on specified port (default: 3000)
- All three tools are registered and available
- Test calls return proper responses
- Audio files are generated correctly

## 📞 Support

For issues or questions:
1. Check logs for error messages
2. Verify environment variables are set correctly
3. Test with mock audio first to isolate TTS issues
4. Run the deployment test suite for comprehensive diagnostics