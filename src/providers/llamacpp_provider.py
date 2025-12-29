"""Llama.cpp LLM Provider implementation."""

import requests
from typing import Optional
from .base_provider import BaseLLMProvider


class LlamaCppProvider(BaseLLMProvider):
    """Llama.cpp provider for local models via llama-server."""
    
    def __init__(
        self,
        model_name: str = "Qwen3-8B-Q4_K_M.gguf",
        base_url: str = "http://localhost:8080",
        **kwargs
    ):
        """Initialize Llama.cpp provider.
        
        Args:
            model_name: Model to use (must match loaded model in llama-server)
            base_url: Llama-server URL
            **kwargs: Additional parameters
        """
        super().__init__(model_name, **kwargs)
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/v1/completions"
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response using Llama.cpp API.
        
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
        # Combine system prompt and user prompt if provided
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        payload = {
            "prompt": full_prompt,
            "temperature": temperature,
            "stream": False
        }
        
        # Set max_tokens if provided, otherwise use reasonable default
        if max_tokens:
            payload["max_tokens"] = max_tokens
        else:
            payload["max_tokens"] = 2048
        
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=300  # Longer timeout for local inference
            )
            response.raise_for_status()
            
            data = response.json()
            # Extract the generated text from the response
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["text"].strip()
            else:
                raise Exception("Unexpected response format from llama.cpp server")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Llama.cpp API error: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if llama-server is running and model is available.
        
        Returns:
            True if llama-server is accessible, False otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            models = data.get("models", [])
            
            # Check if any model is loaded (llama-server typically has one model)
            if models:
                # If user didn't specify a model, accept any loaded model
                if not self.model_name:
                    return True
                # Check if the specified model matches
                return any(
                    self.model_name in model.get("name", "") or 
                    model.get("model", "") == self.model_name
                    for model in models
                )
            
            return False
            
        except requests.exceptions.RequestException:
            return False
