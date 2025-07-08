"""
LLM Integration for Miradi Co-Pilot GraphRAG

This module provides integration with Anthropic Claude models for natural language
conservation planning responses. It focuses on Claude Sonnet 3.5 as the primary model
with Haiku as a fallback option.
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

try:
    import anthropic
except ImportError:
    anthropic = None


class ModelType(Enum):
    """Available Claude model types."""
    SONNET_35 = "claude-3-5-sonnet-20241022"
    HAIKU_3 = "claude-3-haiku-20240307"
    OPUS_3 = "claude-3-opus-20240229"


@dataclass
class LLMResponse:
    """Container for LLM response data."""
    content: str
    model_used: str
    tokens_used: int
    response_time: float
    cost_estimate: float
    success: bool
    error_message: Optional[str] = None


class ClaudeLLMProvider:
    """
    Anthropic Claude integration for conservation planning queries.
    
    This class handles communication with Claude models, focusing on
    natural language conservation responses with domain expertise.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Claude LLM provider.
        
        Args:
            api_key: Anthropic API key. If None, reads from environment.
        """
        self.logger = logging.getLogger(__name__)
        
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set as environment variable")
        
        # Check if anthropic library is available
        if anthropic is None:
            raise ImportError("anthropic library not installed. Run: pip install anthropic")
        
        # Initialize client with proper error handling
        try:
            # Try basic initialization first
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except Exception as e:
            self.logger.error(f"Failed to initialize Anthropic client: {e}")
            raise ValueError(f"Could not initialize Anthropic client. Please check your API key and anthropic library version. Error: {e}")
        
        # Model configuration
        self.primary_model = ModelType.SONNET_35.value
        self.fallback_model = ModelType.HAIKU_3.value
        self.max_tokens = 4000
        self.temperature = 0.1  # Low temperature for consistent conservation advice
        
        # Cost estimates (per 1K tokens) - approximate as of 2024
        self.cost_per_1k_tokens = {
            ModelType.SONNET_35.value: {"input": 0.003, "output": 0.015},
            ModelType.HAIKU_3.value: {"input": 0.00025, "output": 0.00125},
            ModelType.OPUS_3.value: {"input": 0.015, "output": 0.075}
        }
        
        self.logger.info(f"Claude LLM provider initialized with primary model: {self.primary_model}")
    
    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
        max_retries: int = 3
    ) -> LLMResponse:
        """
        Generate a conservation planning response using Claude.
        
        Args:
            system_prompt: System prompt with conservation expertise
            user_prompt: User query with graph context
            model: Specific model to use (defaults to primary_model)
            max_retries: Number of retry attempts
            
        Returns:
            LLMResponse containing the generated conservation advice
        """
        model_to_use = model or self.primary_model
        start_time = time.time()
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Generating response with {model_to_use} (attempt {attempt + 1})")
                
                # Create message for Claude
                message = self.client.messages.create(
                    model=model_to_use,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    system=system_prompt,
                    messages=[
                        {
                            "role": "user",
                            "content": user_prompt
                        }
                    ]
                )
                
                # Extract response content - handle anthropic response format
                response_content = ""
                if message.content:
                    for content_block in message.content:
                        # Handle different content block types from anthropic library
                        try:
                            # Try to get text attribute (works for TextBlock)
                            response_content += getattr(content_block, 'text', str(content_block))
                        except Exception:
                            # Fallback to string representation
                            response_content += str(content_block)
                
                # Calculate metrics
                response_time = time.time() - start_time
                input_tokens = message.usage.input_tokens
                output_tokens = message.usage.output_tokens
                total_tokens = input_tokens + output_tokens
                
                # Estimate cost
                cost_estimate = self._calculate_cost(model_to_use, input_tokens, output_tokens)
                
                self.logger.info(f"Response generated successfully: {total_tokens} tokens, ${cost_estimate:.4f}")
                
                return LLMResponse(
                    content=response_content,
                    model_used=model_to_use,
                    tokens_used=total_tokens,
                    response_time=response_time,
                    cost_estimate=cost_estimate,
                    success=True
                )
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Handle rate limit errors
                if "rate limit" in error_str or "429" in error_str:
                    self.logger.warning(f"Rate limit hit on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        wait_time = 2 ** attempt  # Exponential backoff
                        self.logger.info(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        return self._create_error_response(f"Rate limit exceeded: {e}", start_time)
                
                # Handle API errors
                elif "api" in error_str or "400" in error_str or "401" in error_str or "403" in error_str:
                    self.logger.error(f"API error on attempt {attempt + 1}: {e}")
                    if attempt < max_retries - 1:
                        # Try fallback model on API errors
                        if model_to_use == self.primary_model:
                            model_to_use = self.fallback_model
                            self.logger.info(f"Switching to fallback model: {model_to_use}")
                            continue
                    return self._create_error_response(f"API error: {e}", start_time)
                
                # Handle other errors
                else:
                    self.logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                    if attempt == max_retries - 1:
                        return self._create_error_response(f"Unexpected error: {e}", start_time)
            
        
        return self._create_error_response("All retry attempts failed", start_time)
    
    def generate_conservation_response(
        self,
        system_prompt: str,
        user_prompt: str,
        query_category: str = "general"
    ) -> LLMResponse:
        """
        Generate a conservation-specific response with optimized prompting.
        
        Args:
            system_prompt: Conservation domain system prompt
            user_prompt: User query with conservation context
            query_category: Type of conservation query for optimization
            
        Returns:
            LLMResponse with conservation planning advice
        """
        # Enhance system prompt with conservation-specific instructions
        enhanced_system_prompt = self._enhance_conservation_prompt(system_prompt, query_category)
        
        # Generate response
        return self.generate_response(enhanced_system_prompt, user_prompt)
    
    def _enhance_conservation_prompt(self, system_prompt: str, query_category: str) -> str:
        """
        Enhance system prompt with conservation-specific instructions.
        
        Args:
            system_prompt: Base system prompt
            query_category: Conservation query category
            
        Returns:
            Enhanced system prompt with conservation focus
        """
        conservation_enhancement = f"""

CONSERVATION RESPONSE GUIDELINES:
- Provide clear, actionable conservation recommendations
- Use proper conservation planning terminology
- Structure responses with clear priorities and next steps
- Include specific evidence from the graph data provided
- Maintain focus on practical conservation outcomes
- Consider implementation feasibility and resource constraints

QUERY CATEGORY: {query_category.upper()}
- Tailor your response to this specific type of conservation analysis
- Emphasize the most relevant conservation planning aspects
- Provide category-specific insights and recommendations

RESPONSE FORMAT:
- Start with a clear summary of key findings
- Provide detailed analysis with specific examples from the data
- End with actionable recommendations prioritized by importance
- Use conservation planning language that practitioners understand
"""
        
        return system_prompt + conservation_enhancement
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate estimated cost for the API call.
        
        Args:
            model: Model used for the call
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Estimated cost in USD
        """
        if model not in self.cost_per_1k_tokens:
            return 0.0
        
        costs = self.cost_per_1k_tokens[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def _create_error_response(self, error_message: str, start_time: float) -> LLMResponse:
        """
        Create an error response object.
        
        Args:
            error_message: Description of the error
            start_time: When the request started
            
        Returns:
            LLMResponse indicating failure
        """
        return LLMResponse(
            content="I apologize, but I'm unable to process your conservation query at the moment due to a technical issue. Please try again later.",
            model_used="none",
            tokens_used=0,
            response_time=time.time() - start_time,
            cost_estimate=0.0,
            success=False,
            error_message=error_message
        )
    
    def test_connection(self) -> bool:
        """
        Test the connection to Claude API.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            test_response = self.generate_response(
                system_prompt="You are a helpful assistant.",
                user_prompt="Say 'Connection test successful' if you can read this.",
                model=self.fallback_model  # Use cheaper model for testing
            )
            return test_response.success
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available Claude models.
        
        Returns:
            List of model identifiers
        """
        return [model.value for model in ModelType]
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about current model configuration.
        
        Returns:
            Dictionary with model configuration details
        """
        return {
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "available_models": self.get_available_models(),
            "cost_estimates": self.cost_per_1k_tokens
        }


class LLMManager:
    """
    High-level manager for LLM operations in conservation planning.
    
    This class provides a simplified interface for conservation queries
    while handling provider management and error recovery.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the LLM manager.
        
        Args:
            api_key: Anthropic API key
        """
        self.logger = logging.getLogger(__name__)
        self.claude_provider = ClaudeLLMProvider(api_key)
        
        # Test connection on initialization
        if not self.claude_provider.test_connection():
            self.logger.warning("Claude API connection test failed - responses may not work")
    
    def query_conservation_data(
        self,
        system_prompt: str,
        user_prompt: str,
        query_category: str = "general"
    ) -> LLMResponse:
        """
        Query conservation data with natural language response.
        
        Args:
            system_prompt: Conservation expertise system prompt
            user_prompt: User query with graph context
            query_category: Type of conservation analysis
            
        Returns:
            LLMResponse with conservation insights
        """
        return self.claude_provider.generate_conservation_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            query_category=query_category
        )
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about the LLM integration.
        
        Returns:
            Status dictionary with connection and configuration info
        """
        connection_ok = self.claude_provider.test_connection()
        model_info = self.claude_provider.get_model_info()
        
        return {
            "connection_status": "connected" if connection_ok else "disconnected",
            "provider": "anthropic_claude",
            "model_info": model_info,
            "ready": connection_ok
        }
