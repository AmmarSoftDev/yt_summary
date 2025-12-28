"""Base LLM Provider abstract class."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, model_name: str, **kwargs):
        """Initialize the provider.
        
        Args:
            model_name: Name of the model to use
            **kwargs: Additional provider-specific parameters
        """
        self.model_name = model_name
        self.kwargs = kwargs
    
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """Generate a response from the LLM.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and properly configured.
        
        Returns:
            True if provider is ready to use, False otherwise
        """
        pass
    
    def get_model_name(self) -> str:
        """Get the current model name.
        
        Returns:
            Model name string
        """
        return self.model_name
