from typing import List, Optional
from src.models import Question
from src.repository import QuestionRepository


class QuizManager:
    """Manages the business logic for quiz operations and question management."""

    def __init__(self, repository: QuestionRepository) -> None:
        """Initialize with a repository for data persistence."""
        self.repository = repository
        # Load questions into memory at startup
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