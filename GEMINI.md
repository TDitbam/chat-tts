# Project Rules & AI Instructions (Chat-TTS)

This project is a multi-platform Chat-to-Speech system. To maintain a clean and scalable codebase, all AI assistants must follow these rules.

## 1. Directory Structure
*   **Root:** Entry point scripts (`start_cli.py`, `start_gui.py`) and configuration files (`config.ini`).
*   **`core/`:** Core engine and logic (`tts_engine.py`, `app_logger.py`).
*   **`core/collectors/`:** Platform-specific chat collectors (YouTube, Twitch, TikTok).
*   **`packaging/`:** Build scripts (`build.cmd`) and installer configurations (`setup.iss`).
*   **`docs/`:** Documentation and release notes (`release_notes/`).
*   **`logs/`:** Log files.
*   **`msg_queue/` / `temp_audio/`:** Transient data directories.

## 2. Coding Standards
*   **Keep it Modular:** Separate logic from presentation. Core engine should not know about GUI details.
*   **Clean Loop Handling:** Use `try-except` with timeouts for queue operations instead of `.empty()` checks.
*   **Standardized Logging:** Use the centralized `app_logger.py` for all logging.
*   **Exponential Backoff:** All network-related collectors must implement exponential backoff for reconnections.
*   **Audio Safety:** When using `pygame.mixer`, always `unload()` audio files before attempting to delete them (mandatory for Windows).

## 3. Adding New Features
*   **New Collectors:** Create a new file in `core/` (e.g., `core/new_chat.py`) and integrate it into `ChatTTSEngine.start()`.
*   **Logic Changes:** Modify `core/tts_engine.py`. Keep the `generator_task` and `player_loop` focused and concise.

## 4. Refactoring Guidelines
*   **No "Messy" Code:** Avoid deeply nested loops. Extract complex logic into well-named private methods.
*   **Imports:** Keep imports organized. Standard library first, then third-party, then local modules.
*   **Type Hinting:** Use type hints for method signatures to improve readability and AI understanding.

---
*Note: This file is a foundational mandate for all AI interactions in this repository.*
