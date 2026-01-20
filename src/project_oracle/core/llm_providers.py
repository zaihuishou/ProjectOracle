"""LLM Provider abstraction layer supporting multiple LLM backends."""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import json

from ..utils import logger


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def analyze(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Analyze project using LLM.
        
        Args:
            prompt: Analysis prompt
            max_tokens: Maximum tokens in response
        
        Returns:
            LLM response text
        """
        pass
    
    @abstractmethod
    def estimate_cost(self, input_tokens: int, output_tokens: int = 2000) -> float:
        """
        Estimate API cost.
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Estimated output tokens
        
        Returns:
            Estimated cost in USD
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name."""
        pass


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.model = model
        self.input_price_per_1k = 0.003  # $0.003 per 1K input tokens
        self.output_price_per_1k = 0.015  # $0.015 per 1K output tokens
        
        try:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
    
    def analyze(self, prompt: str, max_tokens: int = 4000) -> str:
        """Analyze using Claude."""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 2000) -> float:
        """Estimate Anthropic API cost."""
        input_cost = (input_tokens / 1000) * self.input_price_per_1k
        output_cost = (output_tokens / 1000) * self.output_price_per_1k
        return input_cost + output_cost
    
    @property
    def name(self) -> str:
        return "Anthropic Claude"


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.model = model
        self.input_price_per_1k = 0.01  # $0.01 per 1K input tokens
        self.output_price_per_1k = 0.03  # $0.03 per 1K output tokens
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
    
    def analyze(self, prompt: str, max_tokens: int = 4000) -> str:
        """Analyze using GPT-4."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 2000) -> float:
        """Estimate OpenAI API cost."""
        input_cost = (input_tokens / 1000) * self.input_price_per_1k
        output_cost = (output_tokens / 1000) * self.output_price_per_1k
        return input_cost + output_cost
    
    @property
    def name(self) -> str:
        return "OpenAI GPT-4"


class GoogleGeminiProvider(BaseLLMProvider):
    """Google Gemini provider (has free tier)."""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        self.model = model
        # Pricing varies, using estimates or free tier
        self.input_price_per_1k = 0.00  # Often free for low usage
        self.output_price_per_1k = 0.00
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.client = genai
        except ImportError:
            raise ImportError("google-generativeai package required. Install with: pip install google-generativeai")
    
    def analyze(self, prompt: str, max_tokens: int = 4000) -> str:
        """Analyze using Gemini."""
        try:
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(
                prompt,
                generation_config=self.client.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.3
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 2000) -> float:
        """Estimate Gemini cost (often free)."""
        # Simplify for now as pricing is complex/often free
        return 0.0
    
    @property
    def name(self) -> str:
        return f"Google Gemini ({self.model})"


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider (FREE)."""
    
    def __init__(self, model: str = "llama2", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host
        
        try:
            import ollama
            self.client = ollama.Client(host=host)
        except ImportError:
            raise ImportError(
                "ollama package required. Install with: pip install ollama\n"
                "Also ensure Ollama is running: ollama serve"
            )
    
    def analyze(self, prompt: str, max_tokens: int = 4000) -> str:
        """Analyze using local Ollama model."""
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                options={
                    "num_predict": max_tokens,
                    "temperature": 0.3
                }
            )
            return response['message']['content']
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            logger.info(f"Make sure Ollama is running and model '{self.model}' is pulled")
            logger.info(f"Run: ollama pull {self.model}")
            raise
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 2000) -> float:
        """Ollama is free."""
        return 0.0
    
    @property
    def name(self) -> str:
        return f"Ollama ({self.model})"


class NoLLMProvider(BaseLLMProvider):
    """No LLM provider - scan-only mode (FREE)."""
    
    def analyze(self, prompt: str, max_tokens: int = 4000) -> str:
        """No analysis performed in scan-only mode."""
        return None
    
    def estimate_cost(self, input_tokens: int, output_tokens: int = 2000) -> float:
        """Scan-only mode is free."""
        return 0.0
    
    @property
    def name(self) -> str:
        return "Scan-Only (No LLM)"


def create_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs
) -> BaseLLMProvider:
    """
    Factory function to create LLM provider.
    
    Args:
        provider_name: One of 'anthropic', 'openai', 'ollama', 'none'
        api_key: API key (required for anthropic/openai)
        model: Model name (optional, uses defaults)
        **kwargs: Additional provider-specific arguments
    
    Returns:
        Configured LLM provider
    
    Raises:
        ValueError: If provider name is invalid or required parameters missing
    """
    if not provider_name or provider_name.lower() == "auto":
        # Auto-detect from environment variables
        import os
        if os.getenv("ANTHROPIC_API_KEY"):
            provider_name = "anthropic"
            api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        elif os.getenv("OPENAI_API_KEY"):
            provider_name = "openai"
            api_key = api_key or os.getenv("OPENAI_API_KEY")
        elif os.getenv("GEMINI_API_KEY"):
            provider_name = "gemini"
            api_key = api_key or os.getenv("GEMINI_API_KEY")
        else:
            # Fallback to scan-only if no keys found
            provider_name = "none"

    provider_name = provider_name.lower()
    
    if provider_name == "anthropic":
        if not api_key:
            # Try to fetch from env if not provided
            import os
            api_key = os.getenv("ANTHROPIC_API_KEY")
            
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY required for Anthropic provider")
        return AnthropicProvider(api_key=api_key, model=model or "claude-3-5-sonnet-20241022")
    
    elif provider_name == "openai":
        if not api_key:
            raise ValueError("OPENAI_API_KEY required for OpenAI provider")
        return OpenAIProvider(api_key=api_key, model=model or "gpt-4-turbo-preview")
    
    elif provider_name == "gemini":
        if not api_key:
            raise ValueError("GEMINI_API_KEY required for Gemini provider")
        return GoogleGeminiProvider(api_key=api_key, model=model or "gemini-1.5-pro-latest")
    
    elif provider_name == "ollama":
        return OllamaProvider(
            model=model or "llama2",
            host=kwargs.get("host", "http://localhost:11434")
        )
    
    elif provider_name == "none":
        return NoLLMProvider()
    
    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Must be one of: anthropic, openai, gemini, ollama, none"
        )
