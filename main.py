import sys
from rich.console import Console
from rich.panel import Panel
from src.llm_client import LLMClient
from src.question_generator import QuestionGenerator
from src.repository import QuestionRepository
from src.ui_handler import UIHandler
from src.quiz_manager import QuizManager
from src.models import MCQQuestion

console = Console()


def main() -> None:
    """Main entry point for the Interactive Learning Tool."""
    try:
        # Instantiate core objects from their classes to set up the application
        llm_client = LLMClient()
        repository = QuestionRepository()
        quiz_manager = QuizManager(repository, llm_client)
        generator = QuestionGenerator(llm_client)
        ui = UIHandler()

        while True:
            console.print(
                Panel.fit(
                    "[bold white]1.[/bold white] Generate Questions\n"
                    "[bold white]2.[/bold white] Statistics Viewing\n"
                    "[bold white]3.[/bold white] Practice Mode\n"
                    "[bold white]4.[/bold white] Test Mode\n"
                    "[bold white]5.[/bold white] Manage Questions\n"
                    "[bold red]6. Exit[/bold red]",
                    title="[bold white]INTERACTIVE LEARNING TOOL[/bold white]",
                    border_style="green",
                )
            )

            choice = input("\nSelect a mode [1-6]: ").strip()

            if choice == "1":
                topic = ui.get_topic_input()
                if topic:
                    with ui.loading_spacer(
                        f"AI is crafting questions about '{topic}'..."
                    ):
                        raw_qs = generator.generate_questions(topic, count=3)
                    accepted = ui.validate_generated_questions(raw_qs)
                    if accepted:
                        quiz_manager.questions.extend(accepted)
                        quiz_manager.save_changes()

            elif choice == "2":
                ui.display_statistics(quiz_manager.questions)

            elif choice == "3":
                practice_q = quiz_manager.get_practice_question()
                if not practice_q:
                    console.print("[yellow]No active questions available.[/yellow]")
                    continue

                user_ans = ui.ask_question(practice_q)
                if isinstance(practice_q, MCQQuestion):
                    is_correct = quiz_manager.evaluate_mcq(practice_q, user_ans)
                else:
                    with ui.loading_spacer("AI is evaluating your answer..."):
                        evaluation = quiz_manager.evaluate_freeform_with_llm(
                            practice_q, user_ans
                        )
                    if evaluation:
                        console.print(
                            f"\n[bold]AI Judgment:[/bold] {'Correct' if evaluation.is_correct else 'Incorrect'}"
                        )
                        console.print(
                            f"[italic]AI Explanation:[/italic] {evaluation.explanation}"
                        )
                        is_correct = evaluation.is_correct
                    else:
                        is_correct = False

                console.print(
                    "[bold green]Correct![/bold green]"
                    if is_correct
                    else f"[bold red]Incorrect.[/bold red] Reference: {practice_q.correct_answer}"
                )
                quiz_manager.update_question_stats(practice_q, is_correct)

            elif choice == "4":
                active_qs = quiz_manager.get_active_questions()
                if not active_qs:
                    console.print("[yellow]No active questions available.[/yellow]")
                    continue

                size = ui.get_test_size_input(len(active_qs))
                test_qs = quiz_manager.get_test_questions(size)
                score = 0

                for q in test_qs:
                    user_ans = ui.ask_question(q)
                    if isinstance(q, MCQQuestion):
                        correct = quiz_manager.evaluate_mcq(q, user_ans)
                    else:
                        with ui.loading_spacer("AI is evaluating..."):
                            eval_obj = quiz_manager.evaluate_freeform_with_llm(
                                q, user_ans
                            )
                        if eval_obj:
                            console.print(f"AI Judgment: {eval_obj.is_correct}")
                            correct = eval_obj.is_correct
                        else:
                            correct = False
                    if correct:
                        score += 1
                    quiz_manager.update_question_stats(q, correct)

                ui.display_test_results(score, size)
                repository.log_test_result(score, size)

            elif choice == "5":
                q_id = ui.get_question_id_input()
                managed_q = quiz_manager.find_question_by_id(q_id)
                if managed_q and ui.confirm_status_change(managed_q):
                    quiz_manager.toggle_question_status(q_id)
                    quiz_manager.save_changes()
                elif not managed_q:
                    ui.show_not_found(q_id)

            elif choice == "6":
                console.print("[bold green]Goodbye![/bold green]")
                sys.exit()

    except KeyboardInterrupt:
        console.print("\n[bold red]Program interrupted. Exiting...[/bold red]")
        sys.exit(0)


if __name__ == "__main__":
    main()
