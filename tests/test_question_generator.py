from src.question_generator import QuestionGenerator, LLMQuestion
from src.models import MCQQuestion, FreeformQuestion


def test_convert_to_domain_models() -> None:
    """Test that LLM models are correctly converted to domain objects."""
    llm_qs = [
        LLMQuestion(type="multiple_choice", text="Q1", correct_answer="A", options=["A", "B"]),
        LLMQuestion(type="freeform", text="Q2", correct_answer="Ans")
    ]
    
    questions = QuestionGenerator._convert_to_domain_models(llm_qs, "TestTopic")
    
    assert len(questions) == 2
    mcq_q = questions[0]
    assert isinstance(mcq_q, MCQQuestion)
    assert mcq_q.options == ["A", "B"]
    
    free_q = questions[1]
    assert isinstance(free_q, FreeformQuestion)
    assert free_q.topic == "TestTopic"