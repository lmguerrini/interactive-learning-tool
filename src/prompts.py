"""Module containing system prompts and prompt templates for LLM interactions."""

from typing import Dict

QUESTION_GENERATION_SYSTEM_PROMPT = (
    "You are an educational assistant. Generate a list of study questions in JSON format. "
    "For each question, include: 'type' (either 'multiple_choice' or 'freeform'), "
    "'text', 'correct_answer', and 'options' (only for multiple_choice). "
    "Return ONLY the raw JSON list without any markdown formatting or code blocks."
)

ANSWER_EVALUATION_SYSTEM_PROMPT = (
    "You are a strict but fair evaluator. Compare the user's answer with the reference answer. "
    "Decide if the user's answer is correct, even if phrased differently. "
    "Return a JSON object that matches the required response schema."
)

QUESTION_GENERATION_USER_TEMPLATE = (
    "Generate {count} high-quality questions about '{topic}'. "
    "Include a mix of MCQ and freeform."
)

FREEFORM_EVALUATION_USER_TEMPLATE = (
    "Question: {question_text}\n"
    "Reference Answer: {reference_answer}\n"
    "User's Answer: {user_answer}"
)


def render_template(template: str, variables: Dict[str, str]) -> str:
    """Render a prompt template using a minimal, dependency-free approach."""
    return template.format(**variables)


def build_question_generation_user_prompt(topic: str, count: int) -> str:
    """Build the user prompt for question generation."""
    return render_template(
        QUESTION_GENERATION_USER_TEMPLATE,
        {"topic": topic, "count": str(count)},
    )


def build_freeform_evaluation_user_prompt(
    question_text: str, reference_answer: str, user_answer: str
) -> str:
    """Build the user prompt for freeform answer evaluation."""
    return render_template(
        FREEFORM_EVALUATION_USER_TEMPLATE,
        {
            "question_text": question_text,
            "reference_answer": reference_answer,
            "user_answer": user_answer,
        },
    )
