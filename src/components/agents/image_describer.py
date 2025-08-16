from __future__ import annotations
from typing import Literal, Union, Optional
from io import BytesIO
import os
import json
import re
import requests
from PIL import Image as PILImage
from pydantic import BaseModel, Field, ValidationError

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import MultiModalMessage
from autogen_core import CancellationToken

# Depending on your AutoGen version this import may vary:
# - Some builds expose Image as `from autogen_core import Image as AGImage`
# - Others as `from autogen_core.images import Image as AGImage`
try:
    from autogen_core import Image as AGImage  # type: ignore
except Exception:
    from autogen_core.images import Image as AGImage  # type: ignore

# ---------- Structured Output Model ----------
class ImageDescription(BaseModel):
    scene: str = Field(description="Briefly, the overall scene of the image")
    message: str = Field(description="The point that the image is trying to convey")
    style: str = Field(description="The artistic style of the image")
    orientation: Literal["portrait", "landscape", "square"] = Field(
        description="The orientation of the image"
    )


# ---------- Image Describer ----------
class ImageDescriber:
    """
    Simple multimodal image describer.
    - You pass a URL / path / bytes / PIL.Image / AGImage.
    - Returns a validated ImageDescription (scene, message, style, orientation).
    """

    SYSTEM_MESSAGE = (
        "You are an expert image describer.\n"
        "Return a structured description with fields: scene, message, style, orientation.\n"
        "Orientation must be one of: 'portrait', 'landscape', or 'square'.\n"
        "Be concise and specific."
    )

    def __init__(self, model_client, stream: bool = False):
        # Ask the agent to produce structured output directly as ImageDescription
        self.agent = AssistantAgent(
            name="description_agent",
            model_client=model_client,
            system_message=self.SYSTEM_MESSAGE,
            model_client_stream=stream,
            output_content_type=ImageDescription,  # <-- key: ask for structured output
        )

    # ---- Public API ----
    async def describe(
        self,
        image_like: Union[str, bytes, PILImage.Image, AGImage],
        prompt: str = "Describe the content of this image in detail",
    ) -> ImageDescription:
        ag_image = self._to_agimage(image_like)
        mm = MultiModalMessage(content=[prompt, ag_image], source="user")

        resp = await self.agent.on_messages([mm], cancellation_token=CancellationToken())
        content = resp.chat_message.content

        # If the agent respected output_content_type, this may already be an ImageDescription
        if isinstance(content, ImageDescription):
            return content

        # Otherwise try to coerce/validate
        try:
            if isinstance(content, dict):
                return ImageDescription.model_validate(content)
            if isinstance(content, str):
                # try to extract JSON from a string response
                json_str = self._extract_json(content)
                return ImageDescription.model_validate_json(json_str)
        except ValidationError as e:
            raise ValueError(f"Failed to validate ImageDescription: {e}") from e

        # Last resort
        return ImageDescription.model_validate(content)

    async def describe_url(
        self,
        url: str,
        prompt: str = "Describe the content of this image in detail",
        timeout: int = 25,
    ) -> ImageDescription:
        return await self.describe(url, prompt=prompt)

    # ---- Helpers ----
    def _to_agimage(self, image_like: Union[str, bytes, PILImage.Image, AGImage]) -> AGImage:
        if isinstance(image_like, AGImage):
            return image_like

        if isinstance(image_like, PILImage.Image):
            return AGImage(image_like)

        if isinstance(image_like, (bytes, bytearray)):
            return AGImage(PILImage.open(BytesIO(image_like)))

        if isinstance(image_like, str):
            # URL?
            if image_like.startswith("http://") or image_like.startswith("https://"):
                data = requests.get(image_like, timeout=25).content
                return self._to_agimage(data)
            # File path?
            if os.path.exists(image_like):
                return AGImage(PILImage.open(image_like))

        raise TypeError(
            "Unsupported image input. Provide a URL, file path, bytes, PIL.Image.Image, or AGImage."
        )

    def _extract_json(self, text: str) -> str:
        # Prefer ```json fenced blocks
        m = re.search(r"```json\s*(.*?)\s*```", text, flags=re.DOTALL | re.IGNORECASE)
        if m:
            return m.group(1)
        # Fall back to first {...}
        m = re.search(r"(\{.*\})", text, flags=re.DOTALL)
        if m:
            return m.group(1)
        # Try to parse as-is (may already be JSON)
        try:
            json.loads(text)
            return text
        except Exception:
            pass
        raise ValueError("No JSON object found in model response.")

