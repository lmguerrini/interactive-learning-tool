# Interactive Learning Tool

An advanced educational tool that uses OpenAI's GPT models to generate study questions, guide practice sessions, and evaluate user performance through structured data validation and a modern, stylized CLI interface.

![Preview](assets/logo.png)

## Setup & Usage
**Python 3.11+ required**

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configuration**:
   - Create a `.env` file in the project root (it is ignored by Git).
   - Start from the template:
       ```bash
       cp .env.example .env
       ```
   - Edit `.env` and set at least your OpenAI API key:
       ```env
       OPENAI_API_KEY="your_actual_api_key_here"
       ```
   - **Environment Variables**

     **Required**:
     - `OPENAI_API_KEY`: Your OpenAI API key.

     **Optional (with defaults)**:
     - `LLM_MODEL` (default: `gpt-4o`)
     - `LLM_TEMPERATURE` (default: `0.2`)
     - `LLM_MAX_COMPLETION_TOKENS` (default: `800`)
     - `LLM_MAX_RETRIES` (default: `2`)  
       Number of retries for transient OpenAI errors (rate limits / connection issues).
     - `LLM_RETRY_MAX_BACKOFF_SECONDS` (default: `8.0`)  
       Maximum backoff delay between retries.
     - `USE_INSTRUCTOR` (default: `false`)  
       Enables the optional `instructor` wrapper if installed. If enabled but not installed, the app falls back to the default OpenAI structured outputs.

3. **Launch Application**:
   ```bash
   python main.py
   ```
4. **Run Automated Tests**:
   ```bash
   python3 -m pytest
   ```
5. **Type Checking**:
   ```bash
   mypy src main.py
   ```
6. **Code Formatting**:
   ```bash
   black .
   ```

## Project Structure
```text
interactive-learning-tool/
├── assets/                   # Visual documentation (App screenshots)
├── data/                     # Persistent storage (JSON questions, TXT results)
├── src/                      # Source code
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Pydantic Settings & Environment management
│   ├── llm_client.py         # OpenAI Structured Output integration
│   ├── models.py             # OOP Domain models (Inheritance)
│   ├── prompts.py            # Prompt templates and helpers
│   ├── question_generator.py # AI generation logic
│   ├── quiz_manager.py       # Core business logic & Algorithms
│   ├── repository.py         # Data access layer (Repository Pattern)
│   └── ui_handler.py         # Advanced CLI Presentation (Rich library)
├── tests/                    # Automated Pytest suite
│   ├── __init__.py           # Test package initialization
│   ├── test_models.py
│   ├── test_question_generator.py
│   ├── test_quiz_manager.py
│   └── test_repository.py
├── main.py                   # Application entry point
├── .env                      # API Credentials (ignored by Git)
├── .env.example              # Environment variables template
├── .gitignore                # Git exclusion rules
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```


## Preview
![Preview](assets/menu.png)

## Feature Coverage

### Official Requirements
- [x] **Generate Questions Mode**: Intelligent topic-based creation of MCQ and Freeform questions via LLM.
- [x] **Validation UI**: Interactive review loop allowing users to accept, reject, or manually modify generated questions.
- [x] **Practice Mode**: Smart question selection using a weighted random algorithm based on historical user performance.
- [x] **Test Mode**: Randomized assessment sessions with automatic score calculation and persistent logging.
- [x] **Manage Questions**: Comprehensive control system to list and toggle question status (Active/Disabled).
- [x] **Statistics Viewing**: Detailed tabular presentation of success rates, source information, and usage frequency.
- [x] **Data Persistence**: Full storage of questions, statistics, and results using JSON and flat-file systems.

### Technical Extra Improvements
- **Structured Outputs**: Integration with OpenAI structured outputs to ensure schema-validated LLM responses.
- **Prompt Modularization**: Prompt templates and builder helpers improve maintainability and reduce duplication.
- **Reliability & Speed Awareness**: Added retry with backoff for transient API errors and latency tracking for each LLM call.
- **Modern CLI Experience**: Leveraged the `Rich` library to provide stylized panels and professional-grade tables.
- **Type-Safe Configuration**: Centralized settings via `pydantic-settings`.
- **Professional Logging**: Integrated `loguru` for robust diagnostics and error tracking.

## Testing Strategy
The project maintains a high-quality test suite using `pytest` and `unittest.mock`:
- **Isolation**: Business logic is tested independently of the OpenAI API and the file system.
- **Coverage**: Includes validation for weighted selection algorithms, JSON serialization integrity, and Pydantic model transformations.