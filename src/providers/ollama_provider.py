"""Ollama LLM Provider implementation."""

import requests
from typing import Optional
from .base_provider import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
    """Ollama provider for local models."""
    
    def __init__(
        self,
        model_name: str = "qwen3:8b",
        base_url: str = "http://localhost:11434",
        **kwargs
    ):
        """Initialize Ollama provider.
        
        Args:
            model_name: Model to use (default: qwen3:8b)
            base_url: Ollama server URL
            **kwargs: Additional parameters
        """
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/generate"
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using Ollama API.
        
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
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "temperature": temperature,
            "stream": False
        }
        
        if max_tokens:
            payload["options"] = {"num_predict": max_tokens}
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=300  # Longer timeout for local inference
            )
            response.raise_for_status()
            
            data = response.json()
            return data["response"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Ollama API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Ollama server is running and model is available.
        
        Returns:
            True if Ollama is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            
            # Check if our model is available
            return any(self.model_name in model for model in models)
            
        except requests.exceptions.RequestException:
            return False
