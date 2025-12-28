"""Summarization agent for processing individual chunks."""

from typing import Dict, List
from ..providers.base_provider import BaseLLMProvider


class SummarizationAgent:
    """Agent responsible for summarizing individual transcript chunks."""
    
    def __init__(self, llm_provider: BaseLLMProvider):
        """Initialize summarization agent.
        
        Args:
            llm_provider: LLM provider instance
        """
        self.llm_provider = llm_provider
        self.system_prompt = """You are an expert at summarizing video content. 
Your task is to create a concise but comprehensive summary of the video transcript chunk provided.

Instructions:
- Extract the main topics and key points discussed
- Maintain chronological order
- Preserve important details and context
- Use clear, professional language
- If timestamps are present, note the time range covered"""
    
    def summarize_chunk(self, chunk: Dict) -> Dict:
        """Summarize a single transcript chunk.
        
        Args:
            chunk: Chunk dictionary with text and metadata
            
        Returns:
            Dictionary with chunk summary and metadata
        """
        user_prompt = f"""Summarize this video transcript chunk:

Time Range: {chunk['start_timestamp']} - {chunk['end_timestamp']}

Transcript:
{chunk['text']}

Provide a clear summary highlighting the main topics and key points."""

        try:
            summary = self.llm_provider.generate(
                prompt=user_prompt,
                system_prompt=self.system_prompt,
                temperature=0.3,
                max_tokens=500
            )
            
            return {
                'chunk_id': chunk['chunk_id'],
                'start_timestamp': chunk['start_timestamp'],
                'end_timestamp': chunk['end_timestamp'],
                'summary': summary.strip(),
                'success': True
            }
            
        except Exception as e:
            return {
                'chunk_id': chunk['chunk_id'],
                'start_timestamp': chunk['start_timestamp'],
                'end_timestamp': chunk['end_timestamp'],
                'summary': f"Error: {str(e)}",
                'success': False
            }
    
    def summarize_all_chunks(self, chunks: List[Dict]) -> List[Dict]:
        """Summarize all chunks sequentially.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            List of chunk summaries
        """
        summaries = []
        
        for chunk in chunks:
            summary = self.summarize_chunk(chunk)
            summaries.append(summary)
        
        return summaries
