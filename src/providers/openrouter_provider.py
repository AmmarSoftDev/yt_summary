"""OpenRouter LLM Provider implementation."""

import os
import requests
from typing import Optional
from .base_provider import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API provider for cloud-based models."""
    
    def __init__(
        self,
        model_name: str = "openai/gpt-oss-20b:free",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """Initialize OpenRouter provider.
        
        Args:
            model_name: Model to use (default: gemini-flash-1.5-8b:free)
            api_key: OpenRouter API key (will use env var if not provided)
            **kwargs: Additional parameters
        """
        super().__init__(model_name, **kwargs)
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/yt_summary",
            "X-Title": "YouTube Summarizer"
        }
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using OpenRouter API.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If API call fails
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenRouter API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if OpenRouter is properly configured.
        
        Returns:
            True if API key is set, False otherwise
        """
        return self.api_key is not None and len(self.api_key) > 0
