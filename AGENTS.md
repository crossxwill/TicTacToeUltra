# Repository Guidelines

## Project Structure & Module Organization
- `ultimate_tictactoe.py` is the main game (UI, rules, AI, tutorial, and rendering).
- `sounds/` holds WAV assets used by the game (`win.wav`, `sad.wav`, `stamp.wav`, `click.wav`).
- `generate_sounds.py` regenerates those assets using NumPy.
- `TicTacToeUltra.code-workspace` is a VS Code workspace file.

## Build, Test, and Development Commands
```bash
# Run the game
python ultimate_tictactoe.py

# (Optional) Regenerate sound assets
python generate_sounds.py
```
Dependencies are Python + `pygame` to run the game; `numpy` is required only for `generate_sounds.py`.

## Coding Style & Naming Conventions
- Indentation: 4 spaces; keep long blocks readable with blank lines.
- Naming: `PascalCase` for classes, `snake_case` for functions/variables, `UPPER_CASE` for constants.
- Type hints are used in places; follow existing patterns when extending logic.
- No formatter or linter is configured—match the style in `ultimate_tictactoe.py`.

## Testing Guidelines
- No automated test suite is present yet.
- For new tests, create a `tests/` folder and use `test_*.py` naming.
- Manual validation is expected: launch the game and verify move constraints, wins, sounds, and resize behavior.

## Commit & Pull Request Guidelines
- Git history is minimal; the existing commit uses a short, descriptive message (e.g., `init - working prototype`).
- Keep commit messages concise and specific; include the main intent in the first line.
- PRs should describe the change, note gameplay impact, and include screenshots or short clips for UI changes.

## Assets & Configuration Notes
- If you change audio files, keep the `.wav` format and place them in `sounds/`.
- Avoid committing generated artifacts outside `sounds/` unless they are required at runtime.
