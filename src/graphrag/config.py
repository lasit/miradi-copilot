"""
Configuration Management for Miradi Co-Pilot GraphRAG

This module handles configuration for the GraphRAG system including
API keys, model settings, and environment variables.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class Environment(Enum):
    """Environment types for configuration."""
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


@dataclass
class GraphRAGConfig:
    """Configuration settings for the GraphRAG system."""
    
    # API Keys
    anthropic_api_key: Optional[str] = None
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: Optional[str] = None
    
    # Model Configuration
    primary_model: str = "claude-3-5-sonnet-20241022"
    fallback_model: str = "claude-3-haiku-20240307"
    max_tokens: int = 4000
    temperature: float = 0.1
    
    # System Configuration
    environment: Environment = Environment.DEVELOPMENT
    log_level: str = "INFO"
    enable_caching: bool = False
    max_retries: int = 3
    
    # Performance Settings
    query_timeout: int = 30  # seconds
    max_context_tokens: int = 8000
    batch_size: int = 1000


class ConfigManager:
    """
    Manages configuration for the GraphRAG system.
    
    This class handles loading configuration from environment variables,
    .env files, and provides defaults for all settings.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Optional path to .env file
        """
        self.config_file = config_file
        self._load_env_file()
        self.config = self._load_configuration()
    
    def _load_env_file(self):
        """Load environment variables from .env file if it exists."""
        env_file = self.config_file or ".env"
        
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
            except Exception as e:
                print(f"Warning: Could not load .env file: {e}")
    
    def _load_configuration(self) -> GraphRAGConfig:
        """
        Load configuration from environment variables with defaults.
        
        Returns:
            GraphRAGConfig with loaded settings
        """
        return GraphRAGConfig(
            # API Keys
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            neo4j_uri=os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
            neo4j_user=os.getenv('NEO4J_USER', 'neo4j'),
            neo4j_password=os.getenv('NEO4J_PASSWORD'),
            
            # Model Configuration
            primary_model=os.getenv('CLAUDE_PRIMARY_MODEL', 'claude-3-5-sonnet-20241022'),
            fallback_model=os.getenv('CLAUDE_FALLBACK_MODEL', 'claude-3-haiku-20240307'),
            max_tokens=int(os.getenv('CLAUDE_MAX_TOKENS', '4000')),
            temperature=float(os.getenv('CLAUDE_TEMPERATURE', '0.1')),
            
            # System Configuration
            environment=Environment(os.getenv('ENVIRONMENT', 'development')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            enable_caching=os.getenv('ENABLE_CACHING', 'false').lower() == 'true',
            max_retries=int(os.getenv('MAX_RETRIES', '3')),
            
            # Performance Settings
            query_timeout=int(os.getenv('QUERY_TIMEOUT', '30')),
            max_context_tokens=int(os.getenv('MAX_CONTEXT_TOKENS', '8000')),
            batch_size=int(os.getenv('BATCH_SIZE', '1000'))
        )
    
    def get_config(self) -> GraphRAGConfig:
        """
        Get the current configuration.
        
        Returns:
            GraphRAGConfig object
        """
        return self.config
    
    def validate_config(self) -> Dict[str, Any]:
        """
        Validate the current configuration.
        
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check required API keys
        if not self.config.anthropic_api_key:
            issues.append("ANTHROPIC_API_KEY is required for LLM integration")
        
        if not self.config.neo4j_password:
            warnings.append("NEO4J_PASSWORD not set - may cause connection issues")
        
        # Validate model settings
        if self.config.max_tokens < 1000:
            warnings.append("MAX_TOKENS is very low - may truncate responses")
        
        if self.config.temperature < 0 or self.config.temperature > 1:
            issues.append("TEMPERATURE must be between 0 and 1")
        
        # Validate performance settings
        if self.config.query_timeout < 5:
            warnings.append("QUERY_TIMEOUT is very low - may cause timeouts")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "config": {
                "anthropic_configured": bool(self.config.anthropic_api_key),
                "neo4j_configured": bool(self.config.neo4j_password),
                "environment": self.config.environment.value,
                "primary_model": self.config.primary_model,
                "fallback_model": self.config.fallback_model
            }
        }
    
    def get_neo4j_config(self) -> Dict[str, Any]:
        """
        Get Neo4j connection configuration.
        
        Returns:
            Dictionary with Neo4j settings
        """
        return {
            "uri": self.config.neo4j_uri,
            "user": self.config.neo4j_user,
            "password": self.config.neo4j_password
        }
    
    def get_claude_config(self) -> Dict[str, Any]:
        """
        Get Claude LLM configuration.
        
        Returns:
            Dictionary with Claude settings
        """
        return {
            "api_key": self.config.anthropic_api_key,
            "primary_model": self.config.primary_model,
            "fallback_model": self.config.fallback_model,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "max_retries": self.config.max_retries
        }
    
    def create_env_template(self, output_file: str = ".env.example") -> None:
        """
        Create a template .env file with all configuration options.
        
        Args:
            output_file: Path to output template file
        """
        template = """# Miradi Co-Pilot GraphRAG Configuration

# Anthropic Claude API Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Neo4j Database Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password_here

# Claude Model Configuration
CLAUDE_PRIMARY_MODEL=claude-3-5-sonnet-20241022
CLAUDE_FALLBACK_MODEL=claude-3-haiku-20240307
CLAUDE_MAX_TOKENS=4000
CLAUDE_TEMPERATURE=0.1

# System Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_CACHING=false
MAX_RETRIES=3

# Performance Settings
QUERY_TIMEOUT=30
MAX_CONTEXT_TOKENS=8000
BATCH_SIZE=1000
"""
        
        with open(output_file, 'w') as f:
            f.write(template)
        
        print(f"Configuration template created: {output_file}")


# Global configuration instance
_config_manager = None


def get_config() -> GraphRAGConfig:
    """
    Get the global configuration instance.
    
    Returns:
        GraphRAGConfig object
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_config()


def validate_config() -> Dict[str, Any]:
    """
    Validate the global configuration.
    
    Returns:
        Validation results dictionary
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.validate_config()


def create_env_template(output_file: str = ".env.example") -> None:
    """
    Create a configuration template file.
    
    Args:
        output_file: Path to output template file
    """
    config_manager = ConfigManager()
    config_manager.create_env_template(output_file)


if __name__ == "__main__":
    # Create .env.example when run directly
    create_env_template()
    
    # Validate current configuration
    validation = validate_config()
    print("Configuration Validation:")
    print(f"Valid: {validation['valid']}")
    if validation['issues']:
        print("Issues:")
        for issue in validation['issues']:
            print(f"  - {issue}")
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
