import os
from typing import Optional, List, cast
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError, BadRequestError
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
from loguru import logger
from src.config import settings

load_dotenv()


class LLMClient:
    """Client for interacting with the OpenAI API."""

    def __init__(self) -> None:
        """Initialize the OpenAI client using centralized settings."""
        if not settings.openai_api_key:
            logger.error("OpenAI API Key is missing in settings.")
            raise ValueError("OpenAI API Key not found.")

        self.client: OpenAI = OpenAI(api_key=settings.openai_api_key)

    def generate_response(self, prompt: str, system_instruction: str = "You are a helpful assistant.") -> str:
        """Send a prompt to the LLM and return the string response."""
        try:
            # Explicit cast required for static typing: OpenAI message params are TypedDict unions
            messages: List[ChatCompletionMessageParam] = [
                cast(
                    ChatCompletionMessageParam,
                    cast(object, {
                        "role": "system",
                        "content": system_instruction,
                    }),
                ),
                cast(
                    ChatCompletionMessageParam,
                    cast(object, {
                        "role": "user",
                        "content": prompt,
                    }),
                ),
            ]

            response = self.client.chat.completions.create(
                model=settings.llm_model,  # Dynamic model selection
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content or ""

        except AuthenticationError:
            logger.error("Authentication failed: Invalid API Key.")
            return "Error: Invalid API Key."
        except RateLimitError:
            logger.warning("API rate limit exceeded.")
            return "Error: Rate limit exceeded."
        except APIConnectionError:
            logger.error("Network error: Could not connect to OpenAI.")
            return "Error: Connection failed."
        except Exception as e:
            logger.exception("An unexpected error occurred during LLM call.")
            return f"Error: {e}"