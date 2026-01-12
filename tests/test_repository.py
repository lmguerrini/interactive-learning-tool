import os
from src.models import MCQQuestion, FreeformQuestion
from src.repository import QuestionRepository


def test_save_and_load_questions(tmp_path) -> None:
    """Test that questions are correctly persisted and reloaded from JSON."""
    # Setup: create a temporary file path using pytest's tmp_path fixture
    test_file = tmp_path / "test_questions.json"
    repo = QuestionRepository(file_path=str(test_file))

    # Create sample questions
    mcq = MCQQuestion(
        question_id="1",
        topic="Python",
        text="What is a list?",
        correct_answer="A sequence",
        options=["A sequence", "A number"],
    )
    freeform = FreeformQuestion(
        question_id="2",
        topic="Python",
        text="Explain PEP 8",
        correct_answer="Style guide",
    )

    # Action: Save and then Load
    repo.save_all([mcq, freeform])
    loaded_questions = repo.load_all()

    # Assertions
    assert len(loaded_questions) == 2
    assert loaded_questions[0].id == "1"
    assert isinstance(loaded_questions[0], MCQQuestion)
    assert loaded_questions[1].id == "2"
    assert isinstance(loaded_questions[1], FreeformQuestion)
    assert loaded_questions[1].correct_answer == "Style guide"
