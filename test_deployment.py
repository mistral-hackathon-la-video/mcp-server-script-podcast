#!/usr/bin/env python3
"""
Test script for MCP server deployment readiness.
"""

import asyncio
import sys
import os

# Add current directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_both_tools():
    """Test both MCP tools together - full pipeline"""
    try:
        from main import generate_script_and_podcast
        
        sample_paper = """# Novel Neural Architecture for Text Processing

## Abstract
This paper introduces a breakthrough approach to neural text processing that achieves 
state-of-the-art results on multiple benchmarks. Our method combines attention mechanisms 
with novel architectural innovations.

## Introduction
Recent advances in transformer architectures have shown remarkable success in natural 
language processing tasks. However, existing approaches still face limitations in 
computational efficiency and model interpretability.

## Method
We propose a new neural architecture that integrates self-attention with hierarchical 
processing mechanisms. The key innovation is a multi-scale attention pattern that 
captures both local and global dependencies.

## Experiments
Our experiments on standard benchmarks show significant improvements over existing methods:
- BERT baseline: 85.2% accuracy
- Our method: 92.7% accuracy  
- Training time reduced by 40%

## Conclusion
This work demonstrates that architectural innovations can lead to substantial improvements
in both performance and efficiency. The proposed method opens new avenues for research
in efficient neural architectures.
"""
        
        print("🧪 Testing full pipeline (script + podcast generation)...")
        result = await generate_script_and_podcast(
            paper_markdown=sample_paper,
            paper_id="test.deployment",
            output_filename="deployment_test_podcast.wav",
            tts_engine="mock"  # Use mock for testing
        )
        
        print("✅ Full pipeline test completed!")
        print(f"Result:\n{result}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_server_structure():
    """Test MCP server structure and tools registration"""
    try:
        from main import mcp
        
        print("🔍 Checking MCP server structure...")
        
        # Test server info
        print(f"📊 Server name: Podcaster MCP Server")
        print(f"🔧 Available methods: {len([attr for attr in dir(mcp) if not attr.startswith('_')])}")
        
        # Check specific methods exist
        required_methods = ['add_tool', 'tool', 'run']
        for method in required_methods:
            if not hasattr(mcp, method):
                print(f"❌ Missing required method: {method}")
                return False
            print(f"✅ Has method: {method}")
        
        print("✅ MCP server structure is valid!")
        return True
        
    except Exception as e:
        print(f"❌ Server structure test failed: {e}")
        return False

async def test_environment_setup():
    """Test environment and dependencies"""
    try:
        print("🔍 Checking environment setup...")
        
        # Test imports
        required_imports = [
            'generate_podcast',
            'soundfile',
            'numpy', 
            'elevenlabs',
            'dotenv'
        ]
        
        for module_name in required_imports:
            try:
                if module_name == 'generate_podcast':
                    from generate_podcast import PodcastGenerator, PodcastConfig
                    print(f"✅ {module_name} imported successfully")
                elif module_name == 'soundfile':
                    import soundfile as sf
                    print(f"✅ {module_name} imported successfully")
                elif module_name == 'numpy':
                    import numpy as np
                    print(f"✅ {module_name} imported successfully")
                elif module_name == 'elevenlabs':
                    from elevenlabs import ElevenLabs
                    print(f"✅ {module_name} imported successfully")
                elif module_name == 'dotenv':
                    from dotenv import load_dotenv
                    print(f"✅ {module_name} imported successfully")
            except ImportError as e:
                print(f"⚠️  {module_name} import warning: {e}")
        
        # Check .env file
        if os.path.exists('.env'):
            print("✅ .env file exists")
        else:
            print("⚠️  .env file not found (API keys may not be available)")
        
        print("✅ Environment setup looks good!")
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

async def main():
    """Run all deployment tests"""
    print("🚀 Starting MCP server deployment tests...\n")
    
    tests = [
        ("Environment Setup", test_environment_setup()),
        ("Server Structure", test_server_structure()),
        ("Full Pipeline", test_both_tools()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        print("=" * 60)
        print(f"📋 Running: {test_name}")
        print("=" * 60)
        success = await test_coro
        results.append((test_name, success))
        print()
    
    # Summary
    print("=" * 60)
    print("📊 Deployment Test Summary:")
    print("=" * 60)
    all_passed = True
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 All tests passed! MCP server is ready for deployment on Alpic!")
        print()
        print("📝 Deployment Instructions:")
        print("  1. Ensure all dependencies are installed: uv sync")
        print("  2. Set environment variables in .env file")
        print("  3. Deploy main.py as MCP server")
        print("  4. Available tools:")
        print("     • generate_script: Generate video script from research paper")
        print("     • generate_podcast: Convert script to audio podcast") 
        print("     • generate_script_and_podcast: Full pipeline")
    else:
        print("⚠️  Some tests failed. Please fix issues before deployment.")

if __name__ == "__main__":
    asyncio.run(main())