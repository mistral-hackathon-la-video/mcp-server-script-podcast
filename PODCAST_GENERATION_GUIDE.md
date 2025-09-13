# Podcast Generation Guide

This guide explains how to use the podcast generation system to convert research paper scripts into high-quality audio podcasts using AI-powered text-to-speech.

## Overview

The podcast generation system consists of two main components:

1. **Script Generation** (`generate_script.py`) - Converts research papers into structured scripts
2. **Audio Generation** (`generate_podcast.py`) - Converts scripts into audio using TTS engines

## Features

### 🎤 Dual TTS Engine Support
- **Kokoro TTS** - High-quality, natural-sounding voices (recommended for main content)
- **ElevenLabs** - Professional voice synthesis with emotional range (great for headlines)
- **Mixed Mode** - Automatically uses the best engine for each component type

### 🎛️ Audio Processing
- Automatic audio normalization
- Configurable silence between segments
- Sample rate conversion and resampling
- Support for multiple output formats (WAV, MP3, etc.)

### 📝 Script Parsing
- Parses structured script format from `generate_script.py`
- Handles Headlines and Text components differently
- Intelligent text cleaning for TTS engines

## Installation

The required dependencies are included in `pyproject.toml`:

```toml
dependencies = [
    # ... other dependencies
    "soundfile>=0.13.1",   # Audio file I/O
    "numpy>=1.24.0",       # Audio processing
    "elevenlabs>=2.1.0",   # ElevenLabs TTS
    "kokoro>=0.9.4",       # Kokoro TTS
]
```

Install with:
```bash
uv sync
```

## Environment Setup

### Required Environment Variables

Create a `.env` file with your API keys:

```bash
# Required for script generation
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Optional: For ElevenLabs TTS (if not provided, only Kokoro will be used)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here

# Optional: TTS model configuration
SCRIPGENETOR_MODEL=qwen/qwen3-235b-a22b-thinking-2507
```

### Getting API Keys

1. **OpenRouter API Key**: 
   - Sign up at [openrouter.ai](https://openrouter.ai)
   - Get API key from your dashboard
   - Required for script generation

2. **ElevenLabs API Key**:
   - Sign up at [elevenlabs.io](https://elevenlabs.io)  
   - Get API key from your profile
   - Optional - enhances audio quality for headlines

## Usage

### 1. Basic Podcast Generation

```python
from generate_podcast import generate_podcast_from_script

# Sample script (output from generate_script.py)
script_text = """\\Headline: Welcome to today's research paper review
\\Text: Hello everyone, and welcome back to our channel! Today we're diving into an exciting paper about transformer architectures.
\\Headline: Let's explore the key innovations presented in this work  
\\Text: The paper introduces several breakthrough concepts that have revolutionized natural language processing."""

# Generate podcast
podcast_path = generate_podcast_from_script(
    script_text=script_text,
    output_path="my_podcast.wav"
)

print(f"Podcast saved to: {podcast_path}")
```

### 2. Advanced Configuration

```python
from generate_podcast import PodcastGenerator, PodcastConfig

# Create custom configuration
config = PodcastConfig(
    tts_engine="mixed",           # "kokoro", "elevenlabs", or "mixed"
    sample_rate=24000,           # Audio quality
    headline_voice="narrator",    # Voice for headlines
    text_voice="host",           # Voice for main content
    silence_duration=0.8,        # Seconds between segments
    headline_silence=1.5,        # Extra silence after headlines
    elevenlabs_stability=0.5,    # ElevenLabs voice stability
    elevenlabs_similarity=0.8,   # ElevenLabs similarity boost
    normalize_audio=True,        # Prevent clipping
    output_format="wav"          # Output format
)

# Generate podcast with custom config
generator = PodcastGenerator(config)
podcast_path = await generator.generate_podcast(script_text, "custom_podcast.wav")
```

### 3. Command Line Interface

```bash
# Basic usage
uv run python generate_podcast.py --script "path/to/script.txt" --output "podcast.wav"

# With custom settings
uv run python generate_podcast.py \
    --script "script.txt" \
    --output "podcast.wav" \
    --engine mixed \
    --sample-rate 24000 \
    --format wav \
    --verbose

# Direct script text
uv run python generate_podcast.py --script "\\Headline: Test\\Text: This is a test"
```

### 4. Complete Pipeline Example

```python
# Full pipeline: Paper URL -> Script -> Podcast
import asyncio
from generate_script import process_script, _fetch_paper_html
from generate_podcast import generate_podcast_from_script

async def paper_to_podcast(paper_url: str, paper_id: str):
    # 1. Fetch paper
    paper_content = _fetch_paper_html(paper_url)
    
    # 2. Generate script
    script_text = process_script(
        method="openrouter",
        paper_markdown=paper_content,
        paper_id=paper_id,
        from_pdf=False
    )
    
    # 3. Generate podcast
    podcast_path = generate_podcast_from_script(
        script_text=script_text,
        output_path=f"podcast_{paper_id}.wav",
        tts_engine="mixed",
        sample_rate=24000
    )
    
    return podcast_path

# Usage
podcast_path = await paper_to_podcast(
    "https://ar5iv.labs.arxiv.org/html/1706.03762", 
    "1706.03762"
)
```

## Script Format

The system expects scripts in this format (output from `generate_script.py`):

```
\\Headline: Your headline content here
\\Text: Your main text content here
\\Text: More text content
\\Headline: Another headline
\\Text: More content
```

### Component Types

- **Headlines** (`\\Headline:`): 
  - Used for section titles and emphasis
  - Typically use ElevenLabs for dramatic effect
  - Followed by longer silence

- **Text** (`\\Text:`): 
  - Main narrative content
  - Typically use Kokoro for natural speech
  - Standard silence duration

## Audio Configuration

### TTS Engine Selection

| Engine | Best For | Pros | Cons |
|--------|----------|------|------|
| `kokoro` | Main content | Natural, fast, free | Limited voice options |
| `elevenlabs` | Headlines, drama | High quality, many voices | Requires API key, costs money |
| `mixed` | Best results | Automatic optimization | Requires both engines |

### Voice Configuration

Configure voices in `PodcastConfig`:

```python
config = PodcastConfig(
    headline_voice="narrator",  # ElevenLabs voice ID or Kokoro voice name
    text_voice="host",          # ElevenLabs voice ID or Kokoro voice name
)
```

### Audio Quality Settings

```python
config = PodcastConfig(
    sample_rate=24000,          # 24kHz for high quality
    silence_duration=0.5,       # Short pauses between segments  
    headline_silence=1.0,       # Longer pauses after headlines
    normalize_audio=True,       # Prevent clipping
)
```

## Output Formats

Supported formats:
- **WAV** - Uncompressed, high quality
- **MP3** - Compressed, smaller file size  
- **FLAC** - Lossless compression
- **OGG** - Open source compressed format

## Troubleshooting

### Common Issues

1. **"Kokoro TTS initialization failed"**
   - Solution: Kokoro will auto-install on first use
   - Alternative: Use `tts_engine="elevenlabs"` if you have an API key

2. **"ElevenLabs not available"**
   - Solution: Add `ELEVENLABS_API_KEY` to your `.env` file
   - Alternative: Use `tts_engine="kokoro"` for free option

3. **"No TTS engines available"**
   - Solution: Install missing dependencies with `uv sync`
   - Check your API keys in `.env` file

4. **Audio quality issues**
   - Increase `sample_rate` (24000 or 48000)
   - Enable `normalize_audio=True`
   - Check input text for special characters

5. **Import errors**
   - Run `uv sync` to install missing packages
   - Check that you're using the virtual environment

### Performance Tips

- Use `tts_engine="kokoro"` for faster generation
- Lower `sample_rate` for smaller files
- Process long scripts in batches
- Use `normalize_audio=False` to skip normalization step

### Audio Quality Tips

- Use `tts_engine="mixed"` for best results
- Set `sample_rate=24000` or higher
- Configure appropriate silence durations
- Clean input text of URLs and special characters

## Example Scripts

### Test with Sample Data

```bash
# Run the example script
uv run python example_podcast_generation.py --mode sample
```

### Full Pipeline Test

```bash  
# Requires API keys in .env
uv run python example_podcast_generation.py --mode full
```

## Integration with MCP Server

The podcast generation can be integrated with the MCP server by adding a new tool:

```python
@mcp.tool(
    title="Generate Podcast from Script", 
    description="Convert a text script into an audio podcast"
)
async def generate_podcast_tool(
    script_text: str = Field(description="Script text to convert to audio"),
    output_filename: str = Field(default="podcast.wav", description="Output filename")
) -> str:
    """Generate a podcast from script text."""
    from generate_podcast import generate_podcast_from_script
    
    podcast_path = generate_podcast_from_script(
        script_text=script_text,
        output_path=output_filename,
        tts_engine="mixed"
    )
    
    return f"Podcast generated: {podcast_path}"
```

## Advanced Usage

### Custom Voice Training

For advanced users with ElevenLabs Pro:

```python
# Use custom voice IDs
config = PodcastConfig(
    headline_voice="your_custom_voice_id",
    text_voice="another_custom_voice_id", 
    elevenlabs_stability=0.7,     # Higher for consistency
    elevenlabs_similarity=0.9,    # Higher for voice matching
)
```

### Batch Processing

```python
async def process_multiple_papers(paper_list):
    """Process multiple papers in batch."""
    for paper_url, paper_id in paper_list:
        try:
            podcast_path = await paper_to_podcast(paper_url, paper_id)
            print(f"✅ Generated: {podcast_path}")
        except Exception as e:
            print(f"❌ Failed {paper_id}: {e}")
```

## Contributing

To contribute to the podcast generation system:

1. Fork the repository
2. Add features to `generate_podcast.py`
3. Update this documentation
4. Add tests in `test_podcast_generation.py`
5. Submit a pull request

## License

This project is part of the ArXiv Script Generator MCP Server and follows the same license terms.