from datapizza.agents import Agent
from datapizza.clients.openai_like import OpenAILikeClient
from datapizza.core.clients.models import ClientResponse, TokenUsage
from datapizza.type.type import (
    FunctionCallBlock,
    TextBlock,
    MediaBlock,
    Media,
    Tool,
    Block,
)
from datapizza.clients.google.google_client import GoogleClient
import os
from dotenv import load_dotenv

load_dotenv()


class CustomGoogleClient(GoogleClient):
    """Custom GoogleClient to handle inline_data in response."""

    def _response_to_client_response(
        self, response, tool_map: dict[str, Tool] | None = None
    ) -> ClientResponse:
        blocks: list[Block] = []
        # Handle function calls if present
        if hasattr(response, "function_calls") and response.function_calls:
            for fc in response.function_calls:
                if not tool_map:
                    raise ValueError("Tool map is required")

                tool = tool_map.get(fc.name, None)
                if not tool:
                    raise ValueError(f"Tool {fc.name} not found in tool map")

                blocks.append(
                    FunctionCallBlock(
                        name=fc.name,
                        arguments=fc.args,
                        id=f"fc_{id(fc)}",
                        tool=tool,
                    )
                )
        else:
            if hasattr(response, "text") and response.text:
                blocks.append(TextBlock(content=response.text))

        if hasattr(response, "candidates") and response.candidates:
            for part in response.candidates[0].content.parts:
                # Handle inline_data (images)
                if hasattr(part, "inline_data") and part.inline_data:
                    mime_type = part.inline_data.mime_type
                    data = part.inline_data.data
                    blocks.append(
                        MediaBlock(
                            media=Media(
                                media_type=mime_type.split("/")[0]
                                if "/" in mime_type
                                else "image",
                                source_type="base64",
                                source=data,
                            )
                        )
                    )

                # Handle thoughts
                if hasattr(part, "thought") and part.thought and part.text:
                    blocks.append(
                        TextBlock(content=part.text)
                    )

        usage_metadata = getattr(response, "usage_metadata", None)
        return ClientResponse(
            content=blocks,
            stop_reason=(response.candidates[0].finish_reason.value.lower())
            if hasattr(response, "candidates") and response.candidates
            else None,
            usage=TokenUsage(
                prompt_tokens=(usage_metadata.prompt_token_count or 0)
                if usage_metadata
                else 0,
                completion_tokens=(usage_metadata.candidates_token_count or 0)
                if usage_metadata
                else 0,
                cached_tokens=(usage_metadata.cached_content_token_count or 0)
                if usage_metadata
                else 0,
            ),
        )


class AgentService:
    """Service for managing AI agents and their clients."""

    def __init__(self):
        self.local_client = OpenAILikeClient(
            api_key="",
            model="unsloth/gemma-3-4b-it-GGUF",
            base_url="http://localhost:8081/v1",
        )
        self.google_client = CustomGoogleClient(
            api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash-image"
        )

    def get_validate_image_agent(self) -> Agent:
        return Agent(
            name="validate_image_agent",
            client=self.local_client,
            system_prompt=(
                "You are a helpful assistant which validates if an image is showing "
                "an indoor environment like a room, office, or living space."
            ),
        )

    def get_validate_text_agent(self) -> Agent:
        return Agent(
            name="validate_text_agent",
            client=self.local_client,
            system_prompt=(
                "You are a helpful assistant which validates if the user request "
                "is relevant and possible for the image properly."
            ),
        )

    def get_decorator_agent(self) -> Agent:
        return Agent(
            name="decorator_agent",
            client=self.google_client,
            system_prompt=(
                "You are a helpful assistant which describes the best Christmas "
                "decorations to add to this room and return the resulting image."
            ),
            planning_prompt="""
            You are an helpful agent which does the following tasks:
            1. Analyze the image and understand the room's style, lighting, and available spaces.
            2. Consider the user's request (if any) and the room's characteristics.
            3. Describe the best Christmas decorations to add to this room.
            4. Edit the given image to add the Christmas decorations.
            """,
        )
