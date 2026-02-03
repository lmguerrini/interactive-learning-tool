from typing import List, Optional
import random
from loguru import logger
from pydantic import BaseModel, Field
from src.models import Question, MCQQuestion
from src.repository import QuestionRepository
from src.llm_client import LLMClient
from src.prompts import (
    ANSWER_EVALUATION_SYSTEM_PROMPT,
    build_freeform_evaluation_user_prompt,
)


class LLMEvaluation(BaseModel):
    """Schema for AI-based answer evaluation."""

    is_correct: bool = Field(
        description="True if the user answer is correct, False otherwise"
    )
    explanation: str = Field(
        description="A brief explanation of why the answer is correct or not"
    )


class QuizManager:
    """Manages the business logic for quiz operations and question management."""

    def __init__(
        self, repository: QuestionRepository, llm_client: Optional[LLMClient] = None
    ) -> None:
        """Initialize with a repository and an optional LLM client for evaluation."""
        self.repository = repository
        self.llm_client = llm_client
        self.questions: List[Question] = self.repository.load_all()

    def find_question_by_id(self, question_id: str) -> Optional[Question]:
        """Search for a question by its unique ID."""
        for q in self.questions:
            if q.id == question_id:
                return q
        return None

    def toggle_question_status(self, question_id: str) -> bool:
        """Invert the active status of a question and return success."""
        question = self.find_question_by_id(question_id)
        if question:
            question.is_active = not question.is_active
            return True
        return False

    def get_active_questions(self) -> List[Question]:
        """Return a list of all currently enabled questions."""
        return [q for q in self.questions if q.is_active]

    def save_changes(self) -> None:
        """Persist the current state of questions to the storage."""
        self.repository.save_all(self.questions)

    def get_practice_question(self) -> Optional[Question]:
        """Select a question based on success rate (weighted random choice)."""
        active_qs = self.get_active_questions()
        if not active_qs:
            return None

        # Weights: lower success rate = higher probability of selection
        # We use (101 - success_rate) so even a 100% success rate has a small weight (1)
        weights = [(101 - q.success_rate) for q in active_qs]

        selected_list = random.choices(
            active_qs, weights=weights, k=1
        )  # One question at a time
        return selected_list[0]

    def evaluate_freeform_with_llm(
        self, question: Question, user_answer: str
    ) -> Optional[LLMEvaluation]:
        """Use the LLM to judge a freeform answer using structured output."""
        if not self.llm_client:
            logger.error("LLM client not initialized in QuizManager.")
            return None

        prompt = build_freeform_evaluation_user_prompt(
            question_text=question.text,
            reference_answer=question.correct_answer,
            user_answer=user_answer,
        )

        return self.llm_client.generate_structured_response(
            prompt, LLMEvaluation, ANSWER_EVALUATION_SYSTEM_PROMPT
        )

    @staticmethod
    def evaluate_mcq(question: MCQQuestion, user_choice: str) -> bool:
        """Directly compare the user's choice with the stored correct answer."""
        return user_choice.strip().lower() == question.correct_answer.strip().lower()

    def update_question_stats(self, question: Question, is_correct: bool) -> None:
        """Update the statistics for a specific question and persist changes."""
        question.times_shown += 1  # Every time the user answers
        if is_correct:
            question.correct_count += 1
        self.save_changes()

    def get_test_questions(self, size: int) -> List[Question]:
        """Select a random subset of active questions without repetition."""
        active_qs = self.get_active_questions()
        # Ensure we don't try to sample more than available
        sample_size = min(size, len(active_qs))
        return random.sample(active_qs, sample_size)
