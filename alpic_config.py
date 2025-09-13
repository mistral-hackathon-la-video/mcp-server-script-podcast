#!/usr/bin/env python3
"""
Alpic-specific configuration for MCP Podcast Generator server.

This module provides optimized settings and utilities for deploying
the Podcast Generator MCP server on Alpic platform.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AlpicConfig:
    """Configuration class optimized for Alpic deployment."""
    
    # Server Configuration
    SERVER_NAME = "Podcast Generator"
    SERVER_PORT = 3000
    DEBUG_MODE = True
    STATELESS_HTTP = True
    TRANSPORT = "streamable-http"
    
    # Required Environment Variables for Alpic
    REQUIRED_ENV_VARS = [
        "OPENROUTER_API_KEY",
        "SCRIPGENETOR_MODEL",
    ]
    
    # Optional Environment Variables
    OPTIONAL_ENV_VARS = [
        "ELEVENLABS_API_KEY",
        "OCR_MODEL",
        "OCR_PROVIDER",
    ]
    
    # Default TTS Settings for Alpic
    DEFAULT_TTS_ENGINE = "mixed"  # Falls back gracefully
    DEFAULT_SAMPLE_RATE = 24000
    DEFAULT_OUTPUT_FORMAT = "wav"
    
    # ElevenLabs Voice Configuration - Using specified high-quality voice
    HEADLINE_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"  # Specified high-quality voice
    TEXT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"     # Specified high-quality voice
    
    # File Management
    MAX_FILE_SIZE_MB = 100  # Maximum output file size
    TEMP_DIR = os.getenv("TEMP_DIR", "/tmp/podcast_generation")  # Allow override
    
    @classmethod
    def validate_environment(cls):
        """Validate that required environment variables are set."""
        missing_vars = []
        
        for var in cls.REQUIRED_ENV_VARS:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise EnvironmentError(
                f"Missing required environment variables for Alpic deployment: {missing_vars}"
            )
        
        return True
    
    @classmethod
    def get_server_config(cls):
        """Get server configuration dictionary."""
        return {
            "name": cls.SERVER_NAME,
            "port": cls.SERVER_PORT,
            "stateless_http": cls.STATELESS_HTTP,
            "debug": cls.DEBUG_MODE,
            "transport": cls.TRANSPORT,
        }
    
    @classmethod
    def get_tts_config(cls):
        """Get TTS configuration optimized for Alpic."""
        return {
            "tts_engine": cls.DEFAULT_TTS_ENGINE,
            "headline_voice": cls.HEADLINE_VOICE_ID,
            "text_voice": cls.TEXT_VOICE_ID,
            "sample_rate": cls.DEFAULT_SAMPLE_RATE,
            "output_format": cls.DEFAULT_OUTPUT_FORMAT,
            "silence_duration": 0.5,
            "headline_silence": 1.0,
            "normalize_audio": True,
        }
    
    @classmethod
    def setup_directories(cls):
        """Create necessary directories for Alpic deployment."""
        temp_dir = Path(cls.TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

def check_alpic_readiness():
    """
    Check if the environment is ready for Alpic deployment.
    
    Returns:
        bool: True if ready, False otherwise
    """
    try:
        # Validate environment
        AlpicConfig.validate_environment()
        
        # Check required modules
        required_modules = [
            'mcp',
            'soundfile', 
            'numpy',
            'elevenlabs',
            'openai',
            'instructor',
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError as e:
                print(f"❌ Missing module: {module}")
                return False
        
        # Setup directories
        AlpicConfig.setup_directories()
        
        print("✅ Environment is ready for Alpic deployment!")
        return True
        
    except Exception as e:
        print(f"❌ Alpic readiness check failed: {e}")
        return False

def get_alpic_optimized_config():
    """
    Get configuration optimized for Alpic platform.
    
    Returns:
        dict: Configuration dictionary
    """
    return {
        "server": AlpicConfig.get_server_config(),
        "tts": AlpicConfig.get_tts_config(),
        "temp_dir": str(AlpicConfig.setup_directories()),
        "max_file_size_mb": AlpicConfig.MAX_FILE_SIZE_MB,
    }

if __name__ == "__main__":
    # Quick readiness check
    print("🚀 Checking Alpic deployment readiness...")
    if check_alpic_readiness():
        config = get_alpic_optimized_config()
        print("📋 Alpic Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    else:
        print("⚠️  Please fix the issues above before deploying to Alpic.")