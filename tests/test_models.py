from src.models import MCQQuestion, FreeformQuestion


def test_question_success_rate_calculation() -> None:
    """Test that the success rate is calculated correctly."""
    # Arrange
    q = FreeformQuestion("1", "Python", "Text", "Answer")

    # Act & Assert 1: New question should have 0% rate
    assert q.success_rate == 0.0

    # Act & Assert 2: 2 times shown, 1 correct should be 50%
    q.times_shown = 2
    q.correct_count = 1
    assert q.success_rate == 50.0


def test_mcq_options_integrity() -> None:
    """Test that MCQ options are stored correctly."""
    options = ["A", "B", "C"]
    q = MCQQuestion("1", "Topic", "Text", "A", options=options)
    assert q.options == options
    assert len(q.options) == 3