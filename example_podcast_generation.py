#!/usr/bin/env python3
"""
Example usage of the podcast generation system.

This script demonstrates how to:
1. Generate a script using generate_script.py
2. Convert the script to audio using generate_podcast.py
"""

import asyncio
from pathlib import Path

# Import our modules
from generate_script import process_script, _fetch_paper_html
from generate_podcast import generate_podcast_from_script, PodcastConfig

async def example_full_pipeline():
    """Example of complete pipeline: Paper -> Script -> Podcast"""
    
    print("🚀 Starting ArXiv Paper to Podcast Pipeline...")
    
    # Step 1: Fetch a research paper
    print("\n📜 Step 1: Fetching research paper...")
    paper_url = "https://ar5iv.labs.arxiv.org/html/1706.03762"  # "Attention Is All You Need"
    paper_id = "1706.03762"
    
    paper_content = _fetch_paper_html(paper_url)
    if not paper_content:
        print("❌ Failed to fetch paper content")
        return
    
    print(f"✅ Fetched paper {paper_id}: {len(paper_content)} characters")
    
    # Step 2: Generate script
    print("\n📝 Step 2: Generating script...")
    try:
        script_text = process_script(
            method="openrouter", 
            paper_markdown=paper_content,
            paper_id=paper_id,
            from_pdf=False
        )
        print(f"✅ Generated script: {len(script_text)} characters")
        
        # Save script to file for inspection
        script_path = f"script_{paper_id}.txt"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_text)
        print(f"💾 Script saved to: {script_path}")
        
    except Exception as e:
        print(f"❌ Script generation failed: {e}")
        return
    
    # Step 3: Generate podcast
    print("\n🎙️ Step 3: Generating podcast...")
    try:
        # Configure podcast generation
        config = PodcastConfig(
            tts_engine="mixed",        # Use both engines  
            sample_rate=24000,
            headline_voice="narrator", 
            text_voice="host",
            silence_duration=0.8,     # Longer pauses for clarity
            headline_silence=1.5,     # Even longer after headlines
            normalize_audio=True
        )
        
        # Generate podcast
        podcast_path = generate_podcast_from_script(
            script_text=script_text,
            output_path=f"podcast_{paper_id}.wav",
            **config.__dict__
        )
        
        print(f"🎉 Podcast generated successfully!")
        print(f"💾 Audio saved to: {podcast_path}")
        
    except Exception as e:
        print(f"❌ Podcast generation failed: {e}")
        return
    
    print(f"\n✅ Complete pipeline finished successfully!")
    print(f"📄 Script: {script_path}")  
    print(f"🎵 Podcast: {podcast_path}")

def example_script_to_podcast():
    """Example with a sample script (no API calls needed)"""
    
    print("🎙️ Testing Script to Podcast Conversion...")
    
    # Sample script in the expected format
    sample_script = """\\Headline: Welcome to today's research paper review
\\Text: Hello everyone, and welcome back to our channel! Today we're diving into an exciting paper about transformer architectures.
\\Headline: Let's explore the key innovations presented in this work  
\\Text: The paper introduces several breakthrough concepts that have revolutionized natural language processing. We'll break down each component step by step.
\\Text: First, let's understand the attention mechanism, which allows the model to focus on different parts of the input sequence simultaneously.
\\Headline: Now we'll examine the experimental results
\\Text: The authors conducted extensive experiments across multiple datasets, demonstrating significant improvements over previous approaches.
\\Text: Thank you for watching today's review. Don't forget to subscribe for more research paper breakdowns!"""
    
    try:
        # Generate podcast with sample script
        podcast_path = generate_podcast_from_script(
            script_text=sample_script,
            output_path="sample_podcast.wav",
            tts_engine="mixed",
            sample_rate=22050,
            silence_duration=0.5,
            headline_silence=1.0
        )
        
        print(f"✅ Sample podcast generated: {podcast_path}")
        
    except Exception as e:
        print(f"❌ Sample podcast generation failed: {e}")

def main():
    """Main entry point with options."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Example podcast generation")
    parser.add_argument("--mode", choices=["full", "sample"], default="sample", 
                       help="Run full pipeline (requires API keys) or sample conversion")
    
    args = parser.parse_args()
    
    if args.mode == "full":
        asyncio.run(example_full_pipeline())
    else:
        example_script_to_podcast()

if __name__ == "__main__":
    main()