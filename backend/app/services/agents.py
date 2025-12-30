"""
Agent Service Module

This module provides a service layer for managing AI agents used in the
Christmas Decorator application. It handles client initialization, agent
creation, and lifecycle management.
"""

from dataclasses import dataclass, field
from typing import Optional
from datapizza.agents import Agent
from datapizza.clients.openai_like import OpenAILikeClient


@dataclass(frozen=True)
class ClientConfig:
    """Configuration for an OpenAI-like client."""
    model: str
    base_url: str = "http://localhost:11434/v1"
    api_key: str = ""
    system_prompt: str = "You are a helpful assistant."


@dataclass(frozen=True)
class AgentConfig:
    """Configuration for an agent."""
    name: str
    system_prompt: str


# Default configurations
DEFAULT_CLIENTS = {
    "text": ClientConfig(
        model="unsloth/gemma-3-270m-it-GGUF",
        base_url="http://localhost:8081/v1",
    ),
    "vlm": ClientConfig(
        model="unsloth/gemma-3-4b-it-GGUF",
        base_url="http://localhost:8082/v1",
    ),
    "diffusion": ClientConfig(
        model="unsloth/Qwen-Image-Edit-2511-GGUF",
        base_url="http://localhost:8083/v1",
    ),
}

DEFAULT_AGENTS = {
    "validate_image": AgentConfig(
        name="validate_image_agent",
        system_prompt=(
            "You are a helpful assistant which validates if an image is showing "
            "an indoor environment like a room, office, or living space."
        ),
    ),
    "validate_text": AgentConfig(
        name="validate_text_agent",
        system_prompt=(
            "You are a helpful assistant which validates if the user request "
            "is relevant and possible for the image properly."
        ),
    ),
    "decorator_descriptor": AgentConfig(
        name="image_decorator_descriptor_agent",
        system_prompt=(
            "You are a helpful assistant who decides which are the best "
            "Christmas decorations to add to the given image."
        ),
    ),
    "decorator": AgentConfig(
        name="image_decorator_agent",
        system_prompt=(
            "You are a helpful assistant who adds the best Christmas "
            "decorations to the given image."
        ),
    ),

}


class AgentService:
    """
    Service for managing AI agents and their clients.
    
    This service handles:
    - Lazy initialization of OpenAI-like clients
    - Creation and configuration of specialized agents
    - Agent lifecycle management
    
    Usage:
        service = AgentService()
        service.initialize()
        agent = service.get_agent("validate_image")
    """
    
    def __init__(
        self,
        client_configs: Optional[dict[str, ClientConfig]] = None,
        agent_configs: Optional[dict[str, AgentConfig]] = None,
    ):
        """
        Initialize the AgentService.
        
        Args:
            client_configs: Custom client configurations. Uses defaults if None.
            agent_configs: Custom agent configurations. Uses defaults if None.
        """
        self._client_configs = client_configs or DEFAULT_CLIENTS
        self._agent_configs = agent_configs or DEFAULT_AGENTS
        self._clients: dict[str, OpenAILikeClient] = {}
        self._agents: dict[str, Agent] = {}
        self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """Check if the service has been initialized."""
        return self._initialized
    
    def initialize(self) -> None:
        """
        Initialize all clients and agents.
        
        This method should be called once before using the service.
        Subsequent calls are no-ops.
        """
        if self._initialized:
            return
        
        self._create_clients()
        self._create_agents()
        self._initialized = True
    
    def _create_clients(self) -> None:
        """Create all configured clients."""
        for key, config in self._client_configs.items():
            self._clients[key] = OpenAILikeClient(
                api_key=config.api_key,
                model=config.model,
                system_prompt=config.system_prompt,
                base_url=config.base_url,
            )
    
    def _create_agents(self) -> None:
        """Create all configured agents."""
        self._agents["validate_image"] = self._create_agent(
            config=self._agent_configs["validate_image"],
            client=self._clients["vlm"],
        )
        self._agents["validate_text"] = self._create_agent(
            config=self._agent_configs["validate_text"],
            client=self._clients["vlm"],
        )
        self._agents["decorator_descriptor"] = self._create_agent(
            config=self._agent_configs["decorator_descriptor"],
            client=self._clients["vlm"],
        )
        self._agents["decorator"] = self._create_agent(
            config=self._agent_configs["decorator"],
            client=self._clients["diffusion"],
        )
        

    
    def _create_agent(self, config: AgentConfig, client: OpenAILikeClient) -> Agent:
        """Create a single agent with the given configuration."""
        return Agent(
            name=config.name,
            client=client,
            system_prompt=config.system_prompt,
        )
    
    def get_client(self, key: str) -> OpenAILikeClient:
        """Get a client by its key."""
        self._ensure_initialized()
        return self._clients[key]
    
    def get_agent(self, key: str) -> Agent:
        """Get an agent by its key."""
        self._ensure_initialized()
        return self._agents[key]
    
    def _ensure_initialized(self) -> None:
        """Ensure the service has been initialized."""
        if not self._initialized:
            raise RuntimeError(
                "AgentService has not been initialized. Call initialize() first."
            )
    
    def get_client(self, key: str) -> OpenAILikeClient:
        """Get a client by its key."""
        self._ensure_initialized()
        return self._clients[key]
    
    def get_agent(self, key: str) -> Agent:
        """Get an agent by its key."""
        self._ensure_initialized()
        return self._agents[key]
    
    def _ensure_initialized(self) -> None:
        """Ensure the service has been initialized."""
        if not self._initialized:
            raise RuntimeError(
                "AgentService has not been initialized. Call initialize() first."
            )
    

    @property
    def validate_image_agent(self) -> Agent:
        """Shortcut to get the validate_image agent."""
        return self.get_agent("validate_image")
    
    @property
    def validate_text_agent(self) -> Agent:
        """Shortcut to get the validate_text agent."""
        return self.get_agent("validate_text")
    
    @property
    def decorator_descriptor_agent(self) -> Agent:
        """Shortcut to get the decorator_descriptor agent."""
        return self.get_agent("decorator_descriptor")
    
    @property
    def decorator_agent(self) -> Agent:
        """Shortcut to get the decorator agent."""
        return self.get_agent("decorator")


# Singleton instance for convenience
_default_service: Optional[AgentService] = None


def get_agent_service() -> AgentService:
    """Get the default AgentService singleton."""
    global _default_service
    if _default_service is None:
        _default_service = AgentService()
        _default_service.initialize()
    return _default_service
