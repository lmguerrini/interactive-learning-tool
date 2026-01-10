from typing import List, Dict, Any
from src.llm_client import LLMClient
from src.models import Question


class QuestionGenerator:
    """Handles the generation of questions using an LLM."""

    def __init__(self, llm_client: LLMClient) -> None:
        """Initialize with an LLM client."""
        self.llm_client = llm_client

    def generate_questions(self, topic: str, count: int = 5) -> List[Question]:
        """Generate a set of questions for a given topic using structured prompts."""
        system_instruction = (
            "You are an educational assistant. Generate a list of study questions in JSON format. "
            "For each question, include: 'type' (either 'multiple_choice' or 'freeform'), "
            "'text', 'correct_answer', and 'options' (only for multiple_choice). "
            "Return ONLY the raw JSON list without any markdown formatting or code blocks."
        )

        prompt = f"Generate {count} high-quality questions about '{topic}'. Include a mix of MCQ and freeform."

        # Logic for parsing will be implemented in the next subtasks
        _ = self.llm_client.generate_response(prompt, system_instruction)
        return []