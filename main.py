import sys
from src.llm_client import LLMClient
from src.question_generator import QuestionGenerator
from src.repository import QuestionRepository
from src.ui_handler import UIHandler
from src.quiz_manager import QuizManager
from src.models import MCQQuestion


def main() -> None:
    """Main entry point for the Interactive Learning Tool."""

    # Initialization of core components
    llm_client = LLMClient() # Interact with OpenAI
    repository = QuestionRepository() # Save and load questions from JSON files
    quiz_manager = QuizManager(repository, llm_client) # Handle quiz logic and evaluation
    generator = QuestionGenerator(llm_client) # Generate questions via LLM
    ui = UIHandler() # Manage user input/output

    while True:
        print("\n" + "=" * 40)
        print("   INTERACTIVE LEARNING TOOL")
        print("=" * 40)
        print("1. Generate Questions (LLM)")
        print("2. Statistics Viewing")
        print("3. Practice Mode")
        print("4. Test Mode")
        print("5. Manage Questions (Enable/Disable)")
        print("6. Exit")

        choice = input("\nSelect a mode [1-6]: ").strip()

        if choice == '1':
            topic = ui.get_topic_input()
            if topic:
                raw_qs = generator.generate_questions(topic, count=3)
                accepted = ui.validate_generated_questions(raw_qs)
                if accepted:
                    quiz_manager.questions.extend(accepted)
                    quiz_manager.save_changes()

        elif choice == '2':
            ui.display_statistics(quiz_manager.questions)

        elif choice == '3':
            question = quiz_manager.get_practice_question()
            if not question:
                print("No active questions available. Please generate or enable some.")
                continue

            user_ans = ui.ask_question(question)
            
            if isinstance(question, MCQQuestion):
                is_correct = quiz_manager.evaluate_mcq(question, user_ans)
            else:
                evaluation = quiz_manager.evaluate_freeform_with_llm(question, user_ans)
                
                if evaluation:
                    print(f"\nAI Judgment: {'Correct' if evaluation.is_correct else 'Incorrect'}")
                    print(f"AI Explanation: {evaluation.explanation}")
                    is_correct = evaluation.is_correct
                else:
                    print("\nAI evaluation failed. Using manual fallback.")
                    is_correct = False

            print("Correct!" if is_correct else f"Incorrect. Reference: {question.correct_answer}")
            quiz_manager.update_question_stats(question, is_correct)

        elif choice == '4':
            active_qs = quiz_manager.get_active_questions()
            if not active_qs:
                print("No active questions available.")
                continue

            size = ui.get_test_size_input(len(active_qs))
            test_qs = quiz_manager.get_test_questions(size)
            score = 0

            for q in test_qs:
                user_ans = ui.ask_question(q)
                if isinstance(q, MCQQuestion):
                    correct = quiz_manager.evaluate_mcq(q, user_ans)
                else:
                    evaluation = quiz_manager.evaluate_freeform_with_llm(q, user_ans)
                    
                    if evaluation:
                        print(f"AI Judgment: {'Correct' if evaluation.is_correct else 'Incorrect'}")
                        print(f"AI Explanation: {evaluation.explanation}")
                        correct = evaluation.is_correct
                    else:
                        print("AI evaluation failed. Marking as incorrect.")
                        correct = False

                if correct: score += 1
                quiz_manager.update_question_stats(q, correct)

            ui.display_test_results(score, size)
            repository.log_test_result(score, size)

        elif choice == '5':
            q_id = ui.get_question_id_input()
            question = quiz_manager.find_question_by_id(q_id)
            if question and ui.confirm_status_change(question):
                quiz_manager.toggle_question_status(q_id)
                quiz_manager.save_changes()
            elif not question:
                ui.show_not_found(q_id)

        elif choice == '6':
            print("Goodbye!")
            sys.exit()


if __name__ == "__main__":
    main()