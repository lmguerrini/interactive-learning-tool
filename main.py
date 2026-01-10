from src.llm_client import LLMClient
from src.question_generator import QuestionGenerator
from src.repository import QuestionRepository
from src.ui_handler import UIHandler


def main() -> None:
    """Main entry point for the question generation flow."""

    # Instantiate core objects from their classes to set up the application
    llm_client = LLMClient() # Interact with OpenAI
    generator = QuestionGenerator(llm_client) # Generate questions via LLM
    repository = QuestionRepository() # Save and load questions from JSON files
    ui = UIHandler() # Manage user input/output

    # Flow
    topic = ui.get_topic_input()
    if not topic:
        print("Topic cannot be empty.")
        return

    print(f"Generating questions for: {topic}...")
    raw_questions = generator.generate_questions(topic, count=3)

    if not raw_questions:
        print("Failed to generate questions. Please check your API key or connection.")
        return

    accepted = ui.validate_generated_questions(raw_questions)

    if accepted:
        current_questions = repository.load_all()
        current_questions.extend(accepted) # Add new questions without overwriting existing ones
        repository.save_all(current_questions)
        print(f"\nSuccessfully saved {len(accepted)} questions to data/questions.json")
    else:
        print("\nNo questions were saved.")


if __name__ == "__main__":
    main()