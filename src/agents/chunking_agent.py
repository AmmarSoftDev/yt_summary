"""Chunking agent for splitting transcripts intelligently."""

from typing import List, Dict
from ..utils.text_processing import TextProcessor


class ChunkingAgent:
    """Agent responsible for chunking long transcripts."""
    
    def __init__(self, max_chunk_size: int = 4000, overlap: int = 200):
        """Initialize chunking agent.
        
        Args:
            max_chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.text_processor = TextProcessor()
    
    def chunk_transcript(self, transcript: str) -> List[Dict[str, any]]:
        """Split transcript into manageable chunks with metadata.
        
        Args:
            transcript: Full transcript text with timestamps
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        # Clean the transcript
        cleaned_text = self.text_processor.clean_text(transcript)
        
        # Split into chunks
        chunks = self.text_processor.split_into_chunks(
            cleaned_text,
            self.max_chunk_size,
            self.overlap
        )
        
        # Add metadata to each chunk
        chunk_data = []
        for idx, chunk_text in enumerate(chunks):
            # Extract timestamps from this chunk
            timestamps = self.text_processor.extract_timestamps(chunk_text)
            start_timestamp = timestamps[0] if timestamps else "00:00"
            end_timestamp = timestamps[-1] if timestamps else "00:00"
            
            chunk_data.append({
                'chunk_id': idx + 1,
                'text': chunk_text,
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'char_count': len(chunk_text)
            })
        
        return chunk_data
    
    def get_chunk_summary(self, chunks: List[Dict]) -> Dict:
        """Get summary statistics about chunks.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Summary statistics
        """
        total_chars = sum(chunk['char_count'] for chunk in chunks)
        
        return {
            'total_chunks': len(chunks),
            'total_characters': total_chars,
            'avg_chunk_size': total_chars // len(chunks) if chunks else 0,
            'first_timestamp': chunks[0]['start_timestamp'] if chunks else "00:00",
            'last_timestamp': chunks[-1]['end_timestamp'] if chunks else "00:00"
        }
