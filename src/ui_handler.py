from typing import List, Optional
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