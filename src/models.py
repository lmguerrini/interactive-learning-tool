from abc import ABC
from enum import Enum
from typing import List, Dict, Any


class QuestionType(Enum):
    """Enumeration for different types of questions."""
    MCQ = "multiple_choice"
    FREEFORM = "freeform"


class Question(ABC):
    """Abstract base class representing a generic learning question."""

    def __init__(
        self,
        question_id: str,
        topic: str,
        text: str,
        correct_answer: str,
        is_active: bool = True,
        times_shown: int = 0,
        correct_count: int = 0,
        source: str = "LLM"
    ) -> None:
        """Initialize a new question instance."""
        self.id: str = question_id
        self.topic: str = topic
        self.text: str = text
        self.correct_answer: str = correct_answer
        self.is_active: bool = is_active
        self.times_shown: int = times_shown
        self.correct_count: int = correct_count
        self.source: str = source

    @property
    def success_rate(self) -> float:
        """Calculate the percentage of correct answers."""
        if self.times_shown == 0:
            return 0.0
        return (self.correct_count / self.times_shown) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert the question instance to a dictionary for JSON persistence."""
        return {
            "id": self.id,
            "topic": self.topic,
            "text": self.text,
            "correct_answer": self.correct_answer,
            "is_active": self.is_active,
            "times_shown": self.times_shown,
            "correct_count": self.correct_count,
            "source": self.source
        }


class MCQQuestion(Question):
    """Model for Multiple Choice Questions."""

    def __init__(
        self,
        question_id: str,
        topic: str,
        text: str,
        correct_answer: str,
        options: List[str],
        **kwargs: Any
    ) -> None:
        """Initialize a MCQ question with options."""
        super().__init__(question_id, topic, text, correct_answer, **kwargs)
        self.options: List[str] = options
        self.type: QuestionType = QuestionType.MCQ

    def to_dict(self) -> Dict[str, Any]:
        """Convert MCQ question to dictionary including options."""
        data = super().to_dict()
        data.update({
            "type": self.type.value,
            "options": self.options
        })
        return data


class FreeformQuestion(Question):
    """Model for Freeform Text Questions."""

    def __init__(
        self,
        question_id: str,
        topic: str,
        text: str,
        correct_answer: str,
        **kwargs: Any
    ) -> None:
        """Initialize a freeform question."""
        super().__init__(question_id, topic, text, correct_answer, **kwargs)
        self.type: QuestionType = QuestionType.FREEFORM

    def to_dict(self) -> Dict[str, Any]:
        """Convert Freeform question to dictionary."""
        data = super().to_dict()
        data.update({"type": self.type.value})
        return data