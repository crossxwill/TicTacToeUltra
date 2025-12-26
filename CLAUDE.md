# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
python ultimate_tictactoe.py
```

Requires pygame, numpy, and scipy:
```bash
uv pip install pygame numpy scipy
```

Or using conda environment:
```bash
conda env create -f environment.yml
conda activate tictactoe
```

## Regenerating Sound Effects

```bash
python generate_sounds.py
```

This creates/overwrites WAV files in the `sounds/` directory.

## Architecture

This is a pygame-based Ultimate Tic Tac Toe game (tic tac toe where each cell contains another tic tac toe board).

### Core Classes

- **UltimateTicTacToe**: Game state and logic. Tracks 9 SubBoards, active board constraint, current player, and win conditions. The `active_board` tuple determines which sub-board the next player must play in (None means any valid board).

- **SubBoard**: Individual 3x3 board with its own win state.

- **AIPlayer**: Opponent with three difficulty levels:
  - Easy: Random valid moves
  - Medium: Basic heuristics (win/block/center/corners)
  - Big Brain: Minimax with alpha-beta pruning (depth 4-6 based on move count)

- **GameRenderer**: All pygame drawing. Handles dynamic sizing, coordinate translation via `get_board_and_cell()`, and status display.

- **SplashScreen/ModeSelectScreen/DifficultySelectScreen/TutorialScreen**: Menu screens with their own event loops.

- **TutorialScreen**: Interactive tutorial with 14 steps (WELCOME through COMPLETE). Uses a demo board where players can practice moves with guided highlights.

- **ConfettiSystem/ConfettiParticle**: Particle effects for wins.

- **SoundManager**: Loads and plays WAV files from `sounds/`.

### Game Flow

`main()` runs the app loop: Splash -> Mode Select -> (Tutorial if selected) -> (Difficulty Select if 1P) -> Game Loop. Press R to restart, E to return home. The "How to Play" button on Mode Select opens the interactive tutorial.

### Key Design Patterns

- Each screen class has its own `run()` method with event loop
- Rendering is separate from game logic
- AI move has intentional delay (500ms) for UX
- Window is resizable with dynamic dimension recalculation
- Dark mode toggle via `set_theme()` updates global color constants
