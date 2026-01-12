import os
from typing import Optional, List, cast
from openai import OpenAI, APIError, RateLimitError, APIConnectionError, AuthenticationError, BadRequestError
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class LLMClient:
    """Client for interacting with the OpenAI API."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize the OpenAI client using environment variables."""
        openai_api_key = api_key if api_key is not None else os.getenv("OPENAI_API_KEY")
        self.api_key: str = openai_api_key or ""

        if not self.api_key:
            logger.error("OpenAI API Key is missing.")
            raise ValueError("OpenAI API Key not found. Please set it in the .env file.")
        
        self.client: OpenAI = OpenAI(api_key=self.api_key)

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
                model="gpt-4o",
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