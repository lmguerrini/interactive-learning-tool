from typing import Optional, List, cast, Type, TypeVar, Any
import random
import time
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

try:
    import instructor  # type: ignore

    INSTRUCTOR_AVAILABLE = True
except ImportError:
    INSTRUCTOR_AVAILABLE = False

T = TypeVar("T", bound=BaseModel)


class LLMClient:
    """Client for interacting with the OpenAI API using structured outputs."""

    def __init__(self) -> None:
        """Initialize the OpenAI client using centralized settings."""
        if not settings.openai_api_key:
            logger.error("OpenAI API Key is missing in settings.")
            raise ValueError("OpenAI API Key not found.")

        base_client = OpenAI(api_key=settings.openai_api_key)

        self.using_instructor = bool(settings.use_instructor and INSTRUCTOR_AVAILABLE)
        if settings.use_instructor and not INSTRUCTOR_AVAILABLE:
            logger.warning(
                "USE_INSTRUCTOR is enabled but 'instructor' is not installed. "
                "Falling back to OpenAI structured outputs."
            )

        self.client: Any = (
            instructor.from_openai(base_client)
            if self.using_instructor
            else base_client
        )
        self.last_latency_seconds: Optional[float] = None

    def generate_structured_response(
        self,
        prompt: str,
        response_model: Type[T],
        system_instruction: str = "You are a helpful assistant.",
    ) -> Optional[T]:
        """Send a prompt and get a response parsed into a Pydantic model."""
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

        attempts = max(1, settings.llm_max_retries + 1)

        for attempt in range(1, attempts + 1):
            start = time.perf_counter()
            try:
                if self.using_instructor:
                    parsed = self.client.chat.completions.create(
                        model=settings.llm_model,
                        messages=messages,
                        response_model=response_model,
                        temperature=settings.llm_temperature,
                        max_completion_tokens=settings.llm_max_completion_tokens,
                    )
                else:
                    completion = self.client.beta.chat.completions.parse(
                        model=settings.llm_model,
                        messages=messages,
                        response_format=response_model,
                        temperature=settings.llm_temperature,
                        max_completion_tokens=settings.llm_max_completion_tokens,
                    )
                    parsed = completion.choices[0].message.parsed

                self.last_latency_seconds = time.perf_counter() - start
                logger.info(
                    f"LLM response received in {self.last_latency_seconds:.2f}s "
                    f"(attempt {attempt}/{attempts}, instructor={self.using_instructor})"
                )
                return parsed

            except AuthenticationError:
                self.last_latency_seconds = time.perf_counter() - start
                logger.error("Authentication failed: Invalid API Key.")
                return None

            except RateLimitError as e:
                self.last_latency_seconds = time.perf_counter() - start
                if attempt >= attempts:
                    logger.warning("API rate limit reached (no more retries).")
                    return None
                self._sleep_before_retry(attempt, e)

            except (APIConnectionError, APIError) as e:
                self.last_latency_seconds = time.perf_counter() - start
                if attempt >= attempts:
                    logger.error(
                        f"OpenAI API communication error (no more retries): {e}"
                    )
                    return None
                self._sleep_before_retry(attempt, e)

            except Exception as e:
                self.last_latency_seconds = time.perf_counter() - start
                logger.exception(f"Unexpected error during structured output: {e}")
                return None

        return None

    @staticmethod
    def _sleep_before_retry(attempt: int, error: Exception) -> None:
        """Sleep using a simple exponential backoff with jitter before retrying."""
        jitter = random.random()
        backoff_seconds = min(
            settings.llm_retry_max_backoff_seconds,
            (2 ** (attempt - 1)) + jitter,
        )
        logger.warning(
            f"Transient OpenAI error. Retrying in {backoff_seconds:.2f}s. Error: {error}"
        )
        time.sleep(backoff_seconds)
