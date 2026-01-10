import json
import uuid
from typing import List, Dict, Any, cast
from src.llm_client import LLMClient
from src.models import MCQQuestion, FreeformQuestion, Question, QuestionType


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

        response_text = self.llm_client.generate_response(prompt, system_instruction)
        return self._parse_llm_response(response_text, topic)

    @staticmethod  # Independent utility method, no access to self or cls
    def _parse_llm_response(response_text: str, topic: str) -> List[Question]:
        """Parse the raw LLM string and handle MCQ and Freeform object creation."""
        try:
            # Cleaning potential Markdown code blocks
            clean_json = response_text.strip().replace("```json", "").replace("```", "")
            data: List[Dict[str, Any]] = json.loads(clean_json)

            questions: List[Question] = []
            for item in data:
                question_id = str(uuid.uuid4())[:8] # UUID v4
                q_type = item.get("type")

                if q_type == QuestionType.MCQ.value:
                    questions.append(MCQQuestion(
                        question_id=question_id,
                        topic=topic,
                        text=str(item.get("text", "")),
                        correct_answer=str(item.get("correct_answer", "")),
                        options=cast(List[str], item.get("options", []))
                    ))
                elif q_type == QuestionType.FREEFORM.value:
                    questions.append(FreeformQuestion(
                        question_id=question_id,
                        topic=topic,
                        text=str(item.get("text", "")),
                        correct_answer=str(item.get("correct_answer", ""))
                    ))
            return questions
        except (json.JSONDecodeError, TypeError, AttributeError):
            return []