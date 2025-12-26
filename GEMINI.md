# Ultimate Tic Tac Toe

## Project Overview
This project is a Python-based implementation of **Ultimate Tic Tac Toe**, a complex variation of the classic game where each cell of a 3x3 grid contains another smaller 3x3 Tic Tac Toe board. The game features single-player (vs AI) and two-player modes, a polished UI with animations, and an interactive tutorial.

## Getting Started

### Prerequisites
The project requires a Python environment (specifically the `tictactoe` conda env) with the following libraries:
- `pygame` (for graphics and sound)
- `numpy` (for AI calculations and sound generation)
- `scipy` (for advanced AI state evaluation)

### Installation
Activate the conda environment and install dependencies:
```bash
conda activate tictactoe
uv pip install pygame numpy scipy
```

### Running the Game
To start the game, run the main script:
```bash
python ultimate_tictactoe.py
```

### Generating Assets
The game uses procedural sound generation. If sound files are missing or you wish to regenerate them, run:
```bash
python generate_sounds.py
```
This will populate the `sounds/` directory with `win.wav`, `sad.wav`, `stamp.wav`, and `click.wav`.

## Project Structure

### Main Application
- **`ultimate_tictactoe.py`**: This is the monolithic entry point and source file. It contains all game classes, including:
    - **Game Logic**: `UltimateTicTacToe`, `SubBoard` (rules, state, validation).
    - **AI**: `AIPlayer` with three difficulty levels (Easy, Medium, "Big Brain" Minimax).
    - **Rendering**: `GameRenderer` (handles drawing boards, grids, and UI).
    - **UI/Screens**: `SplashScreen`, `ModeSelectScreen`, `DifficultySelectScreen`, `TutorialScreen`.
    - **Effects**: `ConfettiSystem`, `SoundManager`.

### Utilities
- **`generate_sounds.py`**: A utility script that synthetically generates sound effects using `numpy` and `wave`, avoiding the need for external asset dependencies.
- **`sounds/`**: Directory where generated `.wav` files are stored.

## Key Features & Architecture
- **State Management**: The game state is strictly separated from rendering. `UltimateTicTacToe` manages the complex rules of active boards and nested wins.
- **AI Implementation**: The "Big Brain" AI uses a Minimax algorithm with alpha-beta pruning and a custom heuristic evaluation function.
- **Tutorial System**: A dedicated `TutorialScreen` class provides an interactive, step-by-step guide with guided moves and visual cues.
- **Event Loop**: Custom event loops for each screen class (`run()` methods) allow for distinct behaviors in menus vs. gameplay.

## Development Notes
- **Coding Style**: The project follows standard Python naming conventions. Type hints are used throughout the codebase.
- **Single-File Structure**: Currently, all game logic resides in `ultimate_tictactoe.py`. Future refactoring could involve splitting this into separate modules (e.g., `game.py`, `ai.py`, `ui.py`) for better maintainability.

## Conda Env

Use this command to export the conda env:

```bash
conda env export -n tictactoe --from-history > environment.yml
```