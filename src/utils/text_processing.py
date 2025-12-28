"""Text processing utilities."""

import re
from typing import List, Dict


class TextProcessor:
    """Process and manipulate text for summarization."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text.
        
        Args:
            text: Input text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove multiple newlines
        text = re.sub(r'\n\s*\n', '\n', text)
        
        return text.strip()
    
    @staticmethod
    def split_into_chunks(
        text: str,
        max_chunk_size: int = 4000,
        overlap: int = 200
    ) -> List[str]:
        """Split text into overlapping chunks.
        
        Args:
            text: Input text
            max_chunk_size: Maximum characters per chunk
            overlap: Number of overlapping characters between chunks
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chunk_size
            
            # If not the last chunk, try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within last 200 chars of chunk
                search_start = max(end - 200, start)
                sentence_end = max(
                    text.rfind('. ', search_start, end),
                    text.rfind('! ', search_start, end),
                    text.rfind('? ', search_start, end)
                )
                
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap if end < len(text) else len(text)
        
        return chunks
    
    @staticmethod
    def extract_timestamps(text: str) -> List[str]:
        """Extract timestamps from text.
        
        Args:
            text: Input text with timestamps
            
        Returns:
            List of timestamps found
        """
        # Match timestamps like [00:00], [00:00:00], (00:00), etc.
        pattern = r'[\[\(]?(\d{1,2}:\d{2}(?::\d{2})?)[\]\)]?'
        timestamps = re.findall(pattern, text)
        return timestamps
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to readable string.
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string (HH:MM:SS or MM:SS)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
