"""Main CLI application for YouTube video summarization."""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint

# Load environment variables from .env file
load_dotenv()

from .providers.openrouter_provider import OpenRouterProvider
from .providers.ollama_provider import OllamaProvider
from .agents.chunking_agent import ChunkingAgent
from .agents.summarization_agent import SummarizationAgent
from .agents.synthesis_agent import SynthesisAgent
from .utils.youtube_extractor import YouTubeExtractor
from .utils.text_processing import TextProcessor


console = Console()


class YouTubeSummarizer:
    """Main application class for YouTube video summarization."""
    
    def __init__(self, provider_type: str = "openrouter", model_name: str = None):
        """Initialize the summarizer.
        
        Args:
            provider_type: Either "openrouter" or "ollama"
            model_name: Optional model name override
        """
        self.provider_type = provider_type.lower()
        self.model_name = model_name
        self.llm_provider = None
        self.text_processor = TextProcessor()
        
    def setup_provider(self):
        """Set up the LLM provider."""
        try:
            if self.provider_type == "openrouter":
                model = self.model_name or "openai/gpt-oss-20b:free"
                self.llm_provider = OpenRouterProvider(model_name=model)
                
                if not self.llm_provider.is_available():
                    console.print("[red]❌ OpenRouter API key not found![/red]")
                    console.print("[yellow]Please set OPENROUTER_API_KEY in .env file[/yellow]")
                    sys.exit(1)
                    
                console.print(f"[green]✓[/green] Using OpenRouter with model: [cyan]{model}[/cyan]")
                
            elif self.provider_type == "ollama":
                model = self.model_name or "qwen3:8b"
                self.llm_provider = OllamaProvider(model_name=model)
                
                if not self.llm_provider.is_available():
                    console.print(f"[red]❌ Ollama server not running or model '{model}' not found![/red]")
                    console.print(f"[yellow]Please ensure Ollama is running and run: ollama pull {model}[/yellow]")
                    sys.exit(1)
                    
                console.print(f"[green]✓[/green] Using Ollama with model: [cyan]{model}[/cyan]")
                
            else:
                console.print(f"[red]❌ Unknown provider type: {self.provider_type}[/red]")
                sys.exit(1)
                
        except Exception as e:
            console.print(f"[red]❌ Failed to setup provider: {str(e)}[/red]")
            sys.exit(1)
    
    def summarize_video(self, video_url: str, output_file: str = None) -> str:
        """Summarize a YouTube video.
        
        Args:
            video_url: YouTube video URL or ID
            output_file: Optional output file path
            
        Returns:
            Final summary text
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # Step 1: Extract transcript
            task1 = progress.add_task("[cyan]Extracting transcript...", total=1)
            try:
                transcript, metadata = YouTubeExtractor.get_transcript_with_metadata(video_url)
                progress.update(task1, completed=1)
                
                duration_str = self.text_processor.format_duration(metadata.get('duration', 0))
                console.print(f"[green]✓[/green] Transcript extracted ([cyan]{duration_str}[/cyan] duration)")
                
            except Exception as e:
                progress.update(task1, completed=1)
                console.print(f"[red]❌ Failed to extract transcript: {str(e)}[/red]")
                sys.exit(1)
            
            # Step 2: Chunk transcript
            task2 = progress.add_task("[cyan]Chunking transcript...", total=1)
            chunking_agent = ChunkingAgent(max_chunk_size=4000, overlap=200)
            chunks = chunking_agent.chunk_transcript(transcript)
            chunk_stats = chunking_agent.get_chunk_summary(chunks)
            progress.update(task2, completed=1)
            
            console.print(f"[green]✓[/green] Created [cyan]{chunk_stats['total_chunks']}[/cyan] chunks")
            
            # Step 3: Summarize chunks
            task3 = progress.add_task(
                f"[cyan]Summarizing chunks...",
                total=len(chunks)
            )
            
            summarization_agent = SummarizationAgent(self.llm_provider)
            chunk_summaries = []
            
            for chunk in chunks:
                summary = summarization_agent.summarize_chunk(chunk)
                chunk_summaries.append(summary)
                progress.update(task3, advance=1)
                
                if not summary['success']:
                    console.print(f"[yellow]⚠ Warning: Chunk {chunk['chunk_id']} failed[/yellow]")
            
            successful = sum(1 for s in chunk_summaries if s['success'])
            console.print(f"[green]✓[/green] Summarized [cyan]{successful}/{len(chunks)}[/cyan] chunks")
            
            # Step 4: Synthesize final summary
            task4 = progress.add_task("[cyan]Synthesizing final summary...", total=1)
            synthesis_agent = SynthesisAgent(self.llm_provider)
            result = synthesis_agent.create_structured_summary(chunk_summaries, metadata)
            progress.update(task4, completed=1)
            
            console.print(f"[green]✓[/green] Final summary created")
        
        # Display summary
        console.print("\n" + "="*80 + "\n")
        md = Markdown(result['summary'])
        console.print(md)
        console.print("\n" + "="*80 + "\n")
        
        # Save to file if specified
        if output_file:
            self.save_summary(result['summary'], output_file, metadata)
            console.print(f"[green]✓[/green] Summary saved to: [cyan]{output_file}[/cyan]")
        
        return result['summary']
    
    def save_summary(self, summary: str, output_file: str, metadata: Dict):
        """Save summary to file.
        
        Args:
            summary: Summary text
            output_file: Output file path
            metadata: Video metadata
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# YouTube Video Summary\n\n")
            f.write(f"**Video URL:** {metadata.get('url', 'N/A')}\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Provider:** {self.provider_type} ({self.llm_provider.get_model_name()})\n\n")
            f.write("---\n\n")
            f.write(summary)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Summarize YouTube videos using AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Using OpenRouter (default)
  python -m src.main https://www.youtube.com/watch?v=VIDEO_ID
  
  # Using Ollama
  python -m src.main https://www.youtube.com/watch?v=VIDEO_ID --provider ollama
  
  # Save to file
  python -m src.main https://www.youtube.com/watch?v=VIDEO_ID -o summary.md
  
  # Use custom model
  python -m src.main https://www.youtube.com/watch?v=VIDEO_ID --model llama3.1:8b
        """
    )
    
    parser.add_argument(
        "url",
        help="YouTube video URL or video ID"
    )
    
    parser.add_argument(
        "-p", "--provider",
        choices=["openrouter", "ollama"],
        default="openrouter",
        help="LLM provider to use (default: openrouter)"
    )
    
    parser.add_argument(
        "-m", "--model",
        help="Model name (overrides default for provider)"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (optional)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    console.print(Panel.fit(
        "[bold cyan]YouTube Video Summarizer[/bold cyan]\n"
        "[dim]AI-powered comprehensive video summaries[/dim]",
        border_style="cyan"
    ))
    console.print()
    
    # Create summarizer
    summarizer = YouTubeSummarizer(
        provider_type=args.provider,
        model_name=args.model
    )
    
    # Setup provider
    summarizer.setup_provider()
    console.print()
    
    # Run summarization
    try:
        summarizer.summarize_video(args.url, args.output)
        console.print("\n[green]✓ Summarization completed successfully![/green]")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠ Summarization cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Unexpected error: {str(e)}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
