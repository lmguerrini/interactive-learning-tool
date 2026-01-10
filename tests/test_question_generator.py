import json
from src.question_generator import QuestionGenerator
from src.models import MCQQuestion, FreeformQuestion


def test_parse_llm_response_cleaning() -> None:
    """Test that the parser can clean markdown and produce correct objects."""
    # Arrange: A dirty JSON string as an LLM might provide
    dirty_json = """
    ```json
    [
        {"type": "multiple_choice", "text": "Q1", "correct_answer": "A", "options": ["A", "B"]},
        {"type": "freeform", "text": "Q2", "correct_answer": "Ans"}
    ]
    ```
    """

    # Act
    questions = QuestionGenerator._parse_llm_response(dirty_json, "TestTopic")

    # Assert
    assert len(questions) == 2
    assert isinstance(questions[0], MCQQuestion)
    assert isinstance(questions[1], FreeformQuestion)
    assert questions[0].topic == "TestTopic"