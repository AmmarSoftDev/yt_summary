"""YouTube transcript extraction utility."""

import re
import time
import requests
from typing import Dict, List, Optional, Tuple
from youtube_transcript_api import (
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)


class YouTubeExtractor:
    """Extract transcripts and metadata from YouTube videos."""
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video ID or None if not found
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If URL is just the video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
        
        return None
    
    @staticmethod
    def get_transcript(video_id: str, languages: List[str] = None, max_retries: int = 3) -> List[Dict]:
        """Get transcript for a video with retry logic and translation support.
        
        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])
            max_retries: Maximum number of retry attempts
            
        Returns:
            List of transcript segments with text, start time, and duration
            
        Raises:
            Exception: If transcript cannot be retrieved
        """
        if languages is None:
            languages = ['en']
        
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Create API instance
                api = YouTubeTranscriptApi()
                
                # Get list of available transcripts
                transcript_list = api.list(video_id)
                
                # Try to get transcript in preferred languages
                transcript = None
                try:
                    # First try exact language match
                    transcript = transcript_list.find_transcript(languages)
                except NoTranscriptFound:
                    # Try any available language and translate if possible
                    available = list(transcript_list)
                    if available:
                        # Get first available transcript
                        first_transcript = available[0]
                        # Check if it's translatable to preferred language
                        if first_transcript.is_translatable and languages[0] in first_transcript.translation_languages:
                            transcript = first_transcript.translate(languages[0])
                        else:
                            transcript = first_transcript
                
                if transcript:
                    result = transcript.fetch()
                    if result:  # Ensure we got valid data
                        # Convert FetchedTranscriptSnippet objects to dictionaries
                        return [
                            {
                                'text': snippet.text,
                                'start': snippet.start,
                                'duration': snippet.duration
                            }
                            for snippet in result
                        ]
                    raise Exception("Transcript fetch returned empty data")
                else:
                    raise NoTranscriptFound(video_id, languages)
                
            except TranscriptsDisabled:
                raise Exception("Transcripts are disabled for this video")
            except NoTranscriptFound as e:
                raise Exception(f"No transcript found for this video. Original error: {str(e)}")
            except VideoUnavailable:
                raise Exception("Video is unavailable or private")
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                # Don't retry for certain errors
                if any(x in error_msg for x in ['disabled', 'unavailable', 'private', 'no transcript']):
                    raise e
                
                if attempt < max_retries - 1:
                    # Wait progressively longer before retrying
                    time.sleep((attempt + 1) * 2)
                    continue
                else:
                    # On last attempt, provide helpful error message
                    raise Exception(f"Failed to retrieve transcript after {max_retries} attempts: {str(last_error)}")
        
        raise Exception(f"Failed to retrieve transcript: {last_error}")
    
    @staticmethod
    def format_transcript(transcript: List[Dict]) -> str:
        """Format transcript segments into readable text.
        
        Args:
            transcript: List of transcript segments
            
        Returns:
            Formatted transcript text
        """
        formatted_parts = []
        
        for segment in transcript:
            text = segment['text'].strip()
            start_time = segment['start']
            
            # Format timestamp
            hours = int(start_time // 3600)
            minutes = int((start_time % 3600) // 60)
            seconds = int(start_time % 60)
            
            if hours > 0:
                timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                timestamp = f"{minutes:02d}:{seconds:02d}"
            
            formatted_parts.append(f"[{timestamp}] {text}")
        
        return "\n".join(formatted_parts)
    
    @staticmethod
    def get_video_metadata(video_id: str) -> Dict[str, any]:
        """Get basic metadata from video transcript.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video metadata
        """
        try:
            transcript = YouTubeExtractor.get_transcript(video_id)
            
            if transcript:
                # Calculate total duration
                last_segment = transcript[-1]
                duration = last_segment['start'] + last_segment['duration']
                
                return {
                    'video_id': video_id,
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'duration': duration,
                    'segment_count': len(transcript)
                }
            
            return {'video_id': video_id, 'url': f"https://www.youtube.com/watch?v={video_id}"}
            
        except Exception:
            return {'video_id': video_id, 'url': f"https://www.youtube.com/watch?v={video_id}"}
    
    @staticmethod
    def get_transcript_with_metadata(url: str) -> Tuple[str, Dict]:
        """Extract transcript and metadata from YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple of (formatted transcript, metadata)
            
        Raises:
            Exception: If extraction fails
        """
        video_id = YouTubeExtractor.extract_video_id(url)
        if not video_id:
            raise Exception("Invalid YouTube URL")
        
        transcript = YouTubeExtractor.get_transcript(video_id)
        formatted_transcript = YouTubeExtractor.format_transcript(transcript)
        metadata = YouTubeExtractor.get_video_metadata(video_id)
        
        return formatted_transcript, metadata
