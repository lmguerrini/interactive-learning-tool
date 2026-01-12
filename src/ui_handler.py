from contextlib import contextmanager
from typing import List, Generator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich import box
from src.models import Question, MCQQuestion

console = Console()

class UIHandler:
    """Handles terminal-based user interactions using Rich for styling."""

    @staticmethod
    @contextmanager
    def loading_spacer(message: str = "Processing...") -> Generator[None, None, None]:
        """Display an animated spinner during long-running tasks."""
        with console.status(f"[bold status.info]{message}[/bold status.info]", spinner="dots"):
            yield
    
    @staticmethod
    def ask_question(question: Question) -> str:
        """Present a question in a stylized panel and capture the answer."""
        console.print(Panel.fit(
            f"[bold cyan]TOPIC:[/bold cyan] {question.topic}\n[bold white]{question.text}[/bold white]",
            title="Question"
        ))
        
        if isinstance(question, MCQQuestion):
            console.print(f"[yellow]OPTIONS:[/yellow] {', '.join(question.options)}")
            return Prompt.ask("Your Choice").strip()
        
        return Prompt.ask("Your Answer").strip()

    @staticmethod
    def display_statistics(questions: List[Question]) -> None:
        """Display a detailed and colored table of all questions."""
        if not questions:
            console.print("[bold red]No questions found in the database.[/bold red]")
            return

        table = Table(
            title="Question Statistics",
            title_style="bold white",
            header_style="bold white",
            border_style="green",
            box=box.ROUNDED
        )
        table.add_column("ID", style="dim", width=10)
        table.add_column("Status")
        table.add_column("Topic", style="cyan")
        table.add_column("Type")
        table.add_column("Shown", justify="right")
        table.add_column("Success", justify="right")
        table.add_column("Question Preview", width=40)

        for q in questions:
            status = "[green]Active[/green]" if q.is_active else "[red]Off[/red]"
            q_type = "MCQ" if isinstance(q, MCQQuestion) else "Freeform"
            color = "green" if q.success_rate > 70 else "yellow" if q.success_rate > 40 else "red"
            
            table.add_row(
                q.id, status, q.topic, q_type, str(q.times_shown),
                f"[{color}]{q.success_rate:.1f}%[/{color}]", q.text[:37] + "..."
            )
        
        console.print(table)

    @staticmethod
    def get_test_size_input(max_size: int) -> int:
        """Prompt the user for the number of questions for the test."""
        return IntPrompt.ask(
            f"How many questions for this test? [bold cyan](1-{max_size})[/bold cyan]",
            choices=[str(i) for i in range(1, max_size + 1)],
            show_choices=False
        )

    @staticmethod
    def confirm_status_change(question: Question) -> bool:
        """Show question details and ask for confirmation with fixed escaped quad brackets."""
        console.print(Panel.fit(f"ID: {question.id}\nText: {question.text}", title="Confirmation"))
        # Using double backslash to escape Rich markup for literal square brackets
        prompt_text = "Do you want to toggle status? [bold cyan]\\[y/n][/bold cyan] [bold red](n)[/bold red]"
        return Prompt.ask(
            prompt_text,
            choices=["y", "n"],
            default="n",
            show_choices=False,
            show_default=False
        ) == "y"

    @staticmethod
    def display_test_results(score: int, total: int) -> None:
        """Present the final test score in a tight stylized panel."""
        percentage = (score / total) * 100 if total > 0 else 0
        color = "green" if percentage > 70 else "yellow" if percentage > 40 else "red"
        
        # Changed to Panel.fit to limit width to content
        console.print(Panel.fit(
            f"You answered [bold]{score}[/bold] out of [bold]{total}[/bold] correctly.\n"
            f"Final Score: [bold {color}]{percentage:.1f}%[/bold {color}]",
            title="[bold]Test Completed[/bold]",
            border_style=color
        ))

    @staticmethod
    def get_topic_input() -> str:
        """Prompt the user for a study topic."""
        return Prompt.ask("\nEnter the [bold cyan]topic[/bold cyan] you want to study").strip()

    @staticmethod
    def get_question_id_input() -> str:
        """Prompt the user for a question ID to manage."""
        return Prompt.ask("\nEnter the [bold yellow]ID[/bold yellow] of the question").strip()

    @staticmethod
    def show_not_found(question_id: str) -> None:
        """Inform the user that a question ID was not found."""
        console.print(f"[bold red]Error:[/bold red] Question with ID '{question_id}' not found.")

    @staticmethod
    def validate_generated_questions(questions: List[Question]) -> List[Question]:
        """Allow the user to review generated questions with Rich styling."""
        accepted_questions: List[Question] = []
        console.print(f"\n[bold cyan]--- AI Generated {len(questions)} Questions ---[/bold cyan]")

        for i, q in enumerate(questions, 1):
            console.print(Panel.fit(f"[bold]Text:[/bold] {q.text}\n[bold]Answer:[/bold] {q.correct_answer}", title=f"Question {i}"))
            choice = Prompt.ask("Action", choices=["a", "r", "m"], default="a")
            
            if choice == 'a':
                accepted_questions.append(q)
            elif choice == 'm':
                q.text = Prompt.ask("Enter new text", default=q.text)
                q.correct_answer = Prompt.ask("Enter new answer", default=q.correct_answer)
                accepted_questions.append(q)
        return accepted_questions