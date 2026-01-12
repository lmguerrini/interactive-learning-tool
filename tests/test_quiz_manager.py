import pytest
from unittest.mock import MagicMock
from src.quiz_manager import QuizManager
from src.models import FreeformQuestion, MCQQuestion


def test_get_active_questions_filtering() -> None:
    """Test that only active questions are returned."""
    # Arrange
    mock_repo = MagicMock()
    q1 = FreeformQuestion("1", "T", "Q", "A", is_active=True)
    q2 = FreeformQuestion("2", "T", "Q", "A", is_active=False)
    mock_repo.load_all.return_value = [q1, q2]

    manager = QuizManager(mock_repo)

    # Act
    active = manager.get_active_questions()

    # Assert
    assert len(active) == 1
    assert active[0].id == "1"


def test_get_test_questions_no_repetition() -> None:
    """Test that test questions are unique and the correct size."""
    # Arrange
    mock_repo = MagicMock()
    questions = [FreeformQuestion(str(i), "T", "Q", "A") for i in range(10)]
    mock_repo.load_all.return_value = questions
    manager = QuizManager(mock_repo)

    # Act
    test_qs = manager.get_test_questions(5)

    # Assert
    assert len(test_qs) == 5
    # Check for uniqueness by comparing length with set of IDs
    assert len(set(q.id for q in test_qs)) == 5


def test_evaluate_mcq_logic() -> None:
    """Test that MCQ evaluation is case-insensitive and robust."""
    q = MCQQuestion("1", "T", "Q", "Paris", options=["Paris", "London"])
    manager = QuizManager(MagicMock())

    assert manager.evaluate_mcq(q, "paris ") is True
    assert manager.evaluate_mcq(q, "London") is False
