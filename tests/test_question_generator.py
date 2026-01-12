from src.question_generator import QuestionGenerator, LLMQuestion
from src.models import MCQQuestion, FreeformQuestion


def test_convert_to_domain_models() -> None:
    """Test that LLM Pydantic models are correctly converted to domain objects."""
    # Arrange: Create sample Pydantic models as if returned by LLMClient
    llm_qs = [
        LLMQuestion(type="multiple_choice", text="Q1", correct_answer="A", options=["A", "B"]),
        LLMQuestion(type="freeform", text="Q2", correct_answer="Ans")
    ]

    # Act
    questions = QuestionGenerator._convert_to_domain_models(llm_qs, "TestTopic")

    # Assert
    assert len(questions) == 2
    assert isinstance(questions[0], MCQQuestion)
    assert isinstance(questions[1], FreeformQuestion)
    assert questions[1].topic == "TestTopic"