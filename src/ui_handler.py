from typing import List
from src.models import Question, MCQQuestion


class UIHandler:
    """Handles terminal-based user interactions."""

    @staticmethod
    def validate_generated_questions(questions: List[Question]) -> List[Question]:
        """Allow the user to accept, reject, or modify generated questions."""
        accepted_questions: List[Question] = []

        print(f"\n--- AI Generated {len(questions)} Questions ---")

        for i, q in enumerate(questions, 1):
            print(f"\nQuestion {i}:")
            print(f"Topic: {q.topic}")
            print(f"Text: {q.text}")
            print(f"Correct Answer: {q.correct_answer}")

            if isinstance(q, MCQQuestion):
                print(f"Options: {', '.join(q.options)}")

            choice = input("\nDo you want to (a)ccept, (r)eject, or (m)odify this question? [a/r/m]: ").lower()

            if choice == 'a':
                accepted_questions.append(q)
                print("Question accepted.")
            elif choice == 'm':
                q.text = input(f"Enter new text (leave blank to keep current): ") or q.text
                q.correct_answer = input(f"Enter new answer (leave blank to keep current): ") or q.correct_answer
                accepted_questions.append(q)
                print("Question modified and accepted.")
            else:
                print("Question rejected.")

        return accepted_questions

    @staticmethod
    def get_topic_input() -> str:
        """Prompt the user for a study topic."""
        return input("\nEnter the topic you want to study: ").strip()

    @staticmethod
    def display_statistics(questions: List[Question]) -> None:
        """Display a detailed table of all questions and their performance stats."""
        if not questions:
            print("\nNo questions found in the database.")
            return

        # Print a formatted table header using f-strings for aligned console output
        print("\n" + "="*115)
        print(f"{'ID':<10} | {'Status':<8} | {'Topic':<15} | {'Type':<10} | {'Source':<8} | {'Shown':<6} | {'Success':<8} | {'Question Text'}")
        print("-" * 115)

        for q in questions:
            status = "Active" if q.is_active else "Off"
            q_type = "MCQ" if isinstance(q, MCQQuestion) else "Freeform"
            
            # Formatting the output in a clean table row
            print(f"{q.id:<10} | {status:<8} | {q.topic[:15]:<15} | {q_type:<10} | {q.source:<8} | "
                  f"{q.times_shown:<6} | {q.success_rate:>6.1f}% | {q.text[:40]}...")
        
        print("="*115 + "\n")