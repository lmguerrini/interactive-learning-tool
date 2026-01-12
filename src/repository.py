import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from src.models import MCQQuestion, FreeformQuestion, Question, QuestionType
from src.config import settings


class QuestionRepository:
    """Handles persistence of questions to and from a JSON file."""

    def __init__(self, file_path: Optional[str] = None) -> None:
        """Initialize the repository using settings if no path is provided."""
        self.file_path: str = file_path or settings.questions_file
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the data directory and file if they do not exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            self.save_all([])

    def save_all(self, questions: List[Question]) -> None:
        """Save all questions to the JSON file."""
        data = [q.to_dict() for q in questions]
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_all(self) -> List[Question]:
        """Load all questions from the JSON file and reconstruct objects."""
        if not os.path.exists(self.file_path):
            return []

        with open(self.file_path, "r", encoding="utf-8") as f:
            try:
                data: List[Dict[str, Any]] = json.load(f)
            except json.JSONDecodeError:
                return []

        questions: List[Question] = []
        for item in data:
            q_type = item.get("type")
            item_copy = item.copy()
            item_copy.pop("type", None)

            if q_type == QuestionType.MCQ.value:
                options = item_copy.pop("options", [])
                questions.append(MCQQuestion(
                    question_id=item_copy.pop("id"),
                    topic=item_copy.pop("topic"),
                    text=item_copy.pop("text"),
                    correct_answer=item_copy.pop("correct_answer"),
                    options=options,
                    **item_copy
                ))
            elif q_type == QuestionType.FREEFORM.value:
                questions.append(FreeformQuestion(
                    question_id=item_copy.pop("id"),
                    topic=item_copy.pop("topic"),
                    text=item_copy.pop("text"),
                    correct_answer=item_copy.pop("correct_answer"),
                    **item_copy
                ))
        return questions

    @staticmethod
    def log_test_result(score: int, total: int) -> None:
        """Append the test result with Timestamp using centralized settings."""
        log_path = settings.results_file
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Score: {score}/{total}\n"
        
        with open(log_path, "a", encoding="utf-8") as f: # Append Mode
            f.write(log_entry)