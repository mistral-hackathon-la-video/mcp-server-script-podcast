# 🎙️ MCP Podcast Generator for Alpic

A Model Context Protocol (MCP) server that generates audio podcasts from research papers, optimized for **Alpic** deployment.

## 🚀 Quick Start for Alpic

### 1. Deploy Files
Upload these files to your Alpic environment:
```
main.py              # MCP server (entry point)
generate_podcast.py  # Podcast generation engine
generate_script.py   # Script generation engine  
alpic_config.py      # Alpic-specific configuration
pyproject.toml       # Dependencies
.env                 # Environment variables
```

### 2. Environment Setup
Configure these environment variables in Alpic:

**Required:**
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
SCRIPGENETOR_MODEL=google/gemini-2.5-pro
```

**Optional (for high-quality TTS):**
```bash
ELEVENLABS_API_KEY=your_elevenlabs_key_here
```

### 3. Install Dependencies
```bash
uv sync
```

### 4. Deploy as MCP Server
```bash
python main.py
```

## 🔧 Alpic Configuration

The server is pre-configured for Alpic with:
- **Transport**: `streamable-http`
- **Port**: 3000
- **Stateless**: True (required for Alpic)
- **Debug**: Enabled for troubleshooting

## 📦 Available MCP Tools

### `generate_script`
Convert research papers to video scripts.
```json
{
  "paper_markdown": "# Research Paper Content...",
  "paper_id": "1706.03762", 
  "method": "openrouter"
}
```

### `generate_podcast`
Convert scripts to audio podcasts.
```json
{
  "script_text": "\\Headline: Introduction\n\\Text: Welcome...",
  "output_filename": "podcast.wav",
  "tts_engine": "elevenlabs"
}
```

### `generate_script_and_podcast`
Full pipeline: paper → script → podcast.
```json
{
  "paper_markdown": "# Research Paper Content...",
  "paper_id": "1706.03762",
  "output_filename": "research_podcast.wav",
  "tts_engine": "mixed"
}
```

## 🎵 Audio Options

### Production (ElevenLabs)
- Set `ELEVENLABS_API_KEY` environment variable
- Use `tts_engine: "elevenlabs"` or `"mixed"`
- High-quality human voices (Rachel & Clyde)

### Testing (Mock Audio)
- No API keys required
- Use `tts_engine: "mock"`
- Pleasant sine wave tones for validation

### Mixed Mode (Recommended)
- Use `tts_engine: "mixed"`
- Automatically selects best available engine
- Falls back gracefully if APIs unavailable

## 🧪 Alpic Testing

Test the deployment:
```bash
python test_deployment.py
```

Check Alpic readiness:
```bash
python alpic_config.py
```

## 📊 Performance on Alpic

Typical processing times:
- **Script Generation**: 10-30 seconds
- **Audio Generation**: 1-5 minutes  
- **Full Pipeline**: 2-8 minutes

Output files:
- **Audio Format**: WAV (24kHz, 16-bit)
- **Typical Size**: 10-50MB (5-20 minutes audio)

## ⚠️ Alpic-Specific Notes

### File Management
- Temporary files stored in `/tmp/podcast_generation/`
- Auto-cleanup after generation
- Maximum output size: 100MB

### Error Handling
- Graceful fallback to mock audio if TTS fails
- Detailed logging for Alpic debugging
- Robust parameter extraction from MCP calls

### Resource Usage
- Memory: ~500MB during processing
- CPU: Moderate (audio processing)
- Network: API calls to OpenRouter/ElevenLabs

## 🔍 Troubleshooting

### Common Alpic Issues

**1. "Missing environment variables"**
```bash
# Check configuration
python alpic_config.py
```

**2. "Import errors"**
```bash
# Reinstall dependencies
uv sync
```

**3. "TTS engine not available"**
```bash
# Use mock for testing
{"tts_engine": "mock"}
```

### Debug Mode
The server runs with `debug=True` by default for Alpic deployment. Check logs for detailed error information.

### Health Check
```bash
# Test all components
python test_deployment.py
```

## ✅ Alpic Deployment Checklist

- [ ] Files uploaded to Alpic
- [ ] Environment variables configured
- [ ] Dependencies installed (`uv sync`)
- [ ] MCP server starts without errors
- [ ] Test calls return successful responses
- [ ] Audio files generate correctly

## 🎉 Success Indicators

When successfully deployed on Alpic:
- ✅ MCP server responds on port 3000
- ✅ All 3 tools are registered and callable
- ✅ Environment validation passes
- ✅ Test audio files generate properly
- ✅ No import or configuration errors

## 📞 Alpic Support

For Alpic-specific deployment issues:
1. Run `python alpic_config.py` for environment check
2. Run `python test_deployment.py` for full validation
3. Check server logs for detailed error messages
4. Verify all environment variables are set correctly

The server is fully optimized for Alpic deployment with robust error handling and graceful degradation! 🚀