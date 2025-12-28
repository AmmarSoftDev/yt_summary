"""Synthesis agent for creating final comprehensive summary."""

from typing import List, Dict
from ..providers.base_provider import BaseLLMProvider


class SynthesisAgent:
    """Agent responsible for synthesizing chunk summaries into final summary."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """Initialize synthesis agent.
        
        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider
        self.system_prompt = """You are an expert at creating comprehensive video summaries.
Your task is to synthesize multiple chunk summaries into a well-structured, hierarchical summary.

Create a summary with the following structure:

# Video Summary

## Overview
[2-3 paragraph narrative overview of the entire video]

## Key Topics
[Organize content into main topics with hierarchical structure]

### Topic 1: [Topic Name] (HH:MM:SS - HH:MM:SS)
- Key point 1
- Key point 2
- Key point 3

[1-2 paragraph narrative explanation of this topic]

### Topic 2: [Topic Name] (HH:MM:SS - HH:MM:SS)
...

## Key Takeaways
- Main takeaway 1
- Main takeaway 2
- Main takeaway 3

Use clear headings, bullet points, and narrative paragraphs for comprehensive coverage."""
    
    def synthesize(
        self,
        chunk_summaries: List[Dict],
        video_metadata: Dict
    ) -> str:
        """Create final comprehensive summary from chunk summaries.
        
        Args:
            chunk_summaries: List of chunk summary dictionaries
            video_metadata: Video metadata
            
        Returns:
            Final formatted summary as markdown
        """
        # Prepare chunk summaries text
        summaries_text = []
        for summary in chunk_summaries:
            if summary['success']:
                summaries_text.append(
                    f"[{summary['start_timestamp']} - {summary['end_timestamp']}]\n"
                    f"{summary['summary']}\n"
                )
        
        combined_summaries = "\n".join(summaries_text)
        
        user_prompt = f"""Here are summaries of different parts of a YouTube video:

Video URL: {video_metadata.get('url', 'N/A')}
Duration: {video_metadata.get('duration', 'N/A')} seconds

Chunk Summaries:
{combined_summaries}

Create a comprehensive, hierarchical summary of this entire video following the structure specified in the system prompt. 
Organize the content logically by topics, include timestamps, use both bullet points and narrative paragraphs."""

        try:
            final_summary = self.llm_provider.generate(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                temperature=0.4,
                max_tokens=2000
            )
            
            return final_summary.strip()
            
        except Exception as e:
            # Fallback: return combined summaries if synthesis fails
            fallback = f"# Video Summary\n\n## Error\nFailed to synthesize final summary: {str(e)}\n\n"
            fallback += "## Chunk Summaries\n\n" + combined_summaries
            return fallback
    
    def create_structured_summary(
        self,
        chunk_summaries: List[Dict],
        video_metadata: Dict
    ) -> Dict:
        """Create structured summary with metadata.
        
        Args:
            chunk_summaries: List of chunk summary dictionaries
            video_metadata: Video metadata
            
        Returns:
            Dictionary with summary and metadata
        """
        final_summary = self.synthesize(chunk_summaries, video_metadata)
        
        return {
            'video_url': video_metadata.get('url', 'N/A'),
            'video_id': video_metadata.get('video_id', 'N/A'),
            'duration': video_metadata.get('duration', 0),
            'summary': final_summary,
            'chunk_count': len(chunk_summaries),
            'successful_chunks': sum(1 for s in chunk_summaries if s['success'])
        }
