"""
AI Client Interface
Abstract interface for different AI backends (Mistral API, Docker/Ollama, etc.)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import aiohttp
import os
from dataclasses import dataclass


@dataclass
class AIResponse:
    """Standardized response from any AI backend"""

    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    model: Optional[str] = None


class AIClient(ABC):
    """Abstract base class for AI clients"""

    @abstractmethod
    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_choice: str = "any",
    ) -> AIResponse:
        """Complete a chat with the AI model"""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the AI service is available"""
        pass


class MistralAIClient(AIClient):
    """Mistral API client implementation"""

    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        """Lazy initialization of Mistral client"""
        if self._client is None:
            from mistralai import Mistral

            self._client = Mistral(api_key=self.api_key)
        return self._client

    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_choice: str = "any",
    ) -> AIResponse:
        """Complete chat using Mistral API"""
        client = self._get_client()

        # Mistral API call
        response = await client.chat.complete(
            messages=messages,
            model=self.model,
            tools=tools,
            tool_choice=tool_choice,
            parallel_tool_calls=False,
        )

        return AIResponse(
            content=response.choices[0].message.content,
            tool_calls=getattr(response.choices[0].message, "tool_calls", None),
            model=self.model,
        )

    async def is_available(self) -> bool:
        """Check if Mistral API is available"""
        try:
            client = self._get_client()
            # Simple test call
            response = await client.chat.complete(
                messages=[{"role": "user", "content": "test"}], model=self.model
            )
            print(response)
            return True
        except Exception:
            return False


class DockerAIClient(AIClient):
    """Docker/Ollama client implementation"""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2-reduced:latest",
    ):
        self.base_url = base_url
        self.model = model

    async def chat_complete(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_choice: str = "auto",
    ) -> AIResponse:
        """Complete chat using Docker/Ollama API with tool calling support"""

        # Convert tools to Ollama format
        ollama_tools = self._convert_tools_for_ollama(tools)

        # Prepare messages for Ollama chat API
        ollama_messages = self._convert_messages_for_ollama_chat(messages)

        payload = {
            "model": self.model,
            "messages": ollama_messages,
            "stream": False,
            "tools": ollama_tools if ollama_tools else None,
            "tool_choice": tool_choice if ollama_tools else None,
            "options": {"temperature": 0.7, "top_p": 0.9},
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    message = result.get("message", {})

                    # Parse tool calls if present
                    tool_calls = None
                    if "tool_calls" in message:
                        tool_calls = message["tool_calls"]

                    return AIResponse(
                        content=message.get("content", ""),
                        tool_calls=tool_calls,
                        model=self.model,
                    )
                else:
                    error_text = await response.text()
                    raise Exception(
                        f"Ollama API error: {response.status} - {error_text}"
                    )

    def _convert_tools_for_ollama(
        self, tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Convert MCP tools to Ollama tool format"""
        ollama_tools = []
        for tool in tools:
            ollama_tool = {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool.get("parameters", {}),
                },
            }
            ollama_tools.append(ollama_tool)
        return ollama_tools

    def _convert_messages_for_ollama_chat(
        self, messages: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Convert messages to Ollama chat API format"""
        ollama_messages = []
        for msg in messages:
            ollama_msg = {"role": msg["role"], "content": msg["content"]}
            ollama_messages.append(ollama_msg)
        return ollama_messages

    def _format_messages_for_ollama(
        self, messages: List[Dict[str, str]], tools: List[Dict[str, Any]]
    ) -> str:
        """Convert chat messages to Ollama prompt format with tool information (legacy method)"""
        formatted = []

        # Add system message with tool information
        system_content = ""
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
                break

        # Add tool information to system prompt
        if tools:
            tool_descriptions = []
            for tool in tools:
                tool_descriptions.append(f"- {tool['name']}: {tool['description']}")

            tools_text = "Available tools:\n" + "\n".join(tool_descriptions)
            if system_content:
                system_content = f"{system_content}\n\n{tools_text}"
            else:
                system_content = tools_text

        if system_content:
            formatted.append(f"System: {system_content}")

        # Add conversation history
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "user":
                formatted.append(f"Human: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")

        return "\n\n".join(formatted) + "\n\nAssistant:"

    async def is_available(self) -> bool:
        """Check if Docker/Ollama service is available"""
        try:
            # First check if the service is running
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/api/tags", timeout=3
                ) as response:
                    if response.status != 200:
                        return False

                    # Check if our model is available
                    models = await response.json()
                    available_models = [
                        model.get("name", "") for model in models.get("models", [])
                    ]
                    if self.model not in available_models:
                        print(
                            f"Model {self.model} not found. Available models: {available_models}"
                        )
                        return False

                    # Test with a simple chat
                    test_payload = {
                        "model": self.model,
                        "messages": [{"role": "user", "content": "Hello"}],
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 10},
                    }

                    async with session.post(
                        f"{self.base_url}/api/chat", json=test_payload, timeout=10
                    ) as test_response:
                        if test_response.status == 200:
                            result = await test_response.json()
                            print(result)
                            return "message" in result and "content" in result.get(
                                "message", {}
                            )
                        return False

        except Exception as e:
            print(f"Ollama API test failed: {str(e)}")
            return False


def create_ai_client() -> Optional[AIClient]:
    """Auto-detect and create appropriate AI client"""
    # Check for Mistral API key first
    if os.getenv("MISTRAL_KEY"):
        return MistralAIClient(
            api_key=os.getenv("MISTRAL_KEY"),
            model=os.getenv("MISTRAL_MODEL", "mistral-large-latest"),
        )

    # Check for Docker/Ollama
    docker_url = os.getenv("DOCKER_AI_URL", "http://localhost:11434")
    docker_model = os.getenv("DOCKER_AI_MODEL", "llama3.2-reduced:latest")
    return DockerAIClient(base_url=docker_url, model=docker_model)


async def check_ai_availability(ai_client: AIClient) -> bool:
    """Check if the AI client is available and working"""
    try:
        return await ai_client.is_available()
    except Exception:
        return False
