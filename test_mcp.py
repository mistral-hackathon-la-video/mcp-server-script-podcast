#!/usr/bin/env python3
"""
Test script to verify MCP tools are working properly.
"""

import asyncio
import sys
import os

# Add current directory to path to import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_podcast_generation():
    """Test the podcast generation MCP tool"""
    try:
        from main import generate_podcast
        
        # Sample script text for testing
        sample_script = """\\Headline: Let's explore the world of artificial intelligence
\\Text: Welcome to this podcast about AI research! Today we're going to discuss some fascinating developments in the field.
\\Headline: Now let's look at the key findings
\\Text: The research shows that these new methods can significantly improve performance across various tasks."""
        
        print("🧪 Testing podcast generation MCP tool...")
        result = await generate_podcast(
            script_text=sample_script,
            output_filename="test_mcp_podcast.wav",
            tts_engine="mock"  # Use mock to avoid API calls
        )
        
        print("✅ Podcast generation test completed!")
        print(f"Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_script_generation():
    """Test the script generation MCP tool"""
    try:
        from main import generate_script
        
        sample_paper = """# Sample Research Paper
        
        ## Abstract
        This paper presents a novel approach to neural networks that improves performance by 15%.
        
        ## Introduction
        Recent advances in deep learning have shown promising results...
        
        ## Methods
        We propose a new architecture that combines attention mechanisms with...
        
        ## Results  
        Our experiments show significant improvements over baseline methods...
        
        ## Conclusion
        This work demonstrates the effectiveness of our proposed approach...
        """
        
        print("🧪 Testing script generation MCP tool...")
        result = await generate_script(
            paper_markdown=sample_paper,
            paper_id="test.paper",
            method="openrouter"
        )
        
        print("✅ Script generation test completed!")
        print(f"Script length: {len(result)} characters")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Note: This may fail without proper API keys, which is expected")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting MCP tools test suite...\n")
    
    # Test 1: Podcast generation (should work with mock engine)
    print("=" * 50)
    success1 = await test_podcast_generation()
    print()
    
    # Test 2: Script generation (may fail without API keys) 
    print("=" * 50)
    success2 = await test_script_generation()
    print()
    
    # Summary
    print("=" * 50)
    print("📊 Test Summary:")
    print(f"  Podcast Generation: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"  Script Generation:  {'✅ PASS' if success2 else '❌ FAIL (expected without API keys)'}")
    print()
    
    if success1:
        print("🎉 MCP tools are ready for deployment!")
    else:
        print("⚠️  Some issues found - check logs above")

if __name__ == "__main__":
    asyncio.run(main())