from typing import Optional, List, cast, Type, TypeVar
from loguru import logger
from openai import (
    OpenAI,
    APIError,
    RateLimitError,
    APIConnectionError,
    AuthenticationError,
)
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel
from src.config import settings

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Client for interacting with the OpenAI API using structured outputs."""

    def __init__(self) -> None:
        """Initialize the OpenAI client using centralized settings."""
        if not settings.openai_api_key:
            logger.error("OpenAI API Key is missing in settings.")
            raise ValueError("OpenAI API Key not found.")

        self.client: OpenAI = OpenAI(api_key=settings.openai_api_key)

    def generate_structured_response(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: str = "You are a helpful assistant.",
    ) -> Optional[T]:
        """Send a prompt and get a response parsed into a Pydantic model."""
        try:
            # Explicit cast required for static typing: OpenAI message params are TypedDict unions
            messages: List[ChatCompletionMessageParam] = [
                cast(
                    ChatCompletionMessageParam,
                    cast(
                        object,
                        {
                            "role": "system",
                            "content": system_instruction,
                        },
                    ),
                ),
                cast(
                    ChatCompletionMessageParam,
                    cast(
                        object,
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ),
                ),
            ]

            completion = self.client.beta.chat.completions.parse(
                model=settings.llm_model,
                messages=messages,
                response_format=response_model,
                temperature=settings.llm_temperature,
                max_completion_tokens=settings.llm_max_completion_tokens,
            )

            return completion.choices[0].message.parsed

        except AuthenticationError:
            logger.error("Authentication failed: Invalid API Key.")
        except RateLimitError:
            logger.warning("API rate limit reached.")
        except (APIConnectionError, APIError) as e:
            logger.error(f"OpenAI API communication error: {e}")
        except Exception as e:
            # logger.exception captures the full stack trace for generic errors
            logger.exception(f"Unexpected error during structured output: {e}")

        return None
