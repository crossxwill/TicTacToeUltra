# Ultimate Tic Tac Toe

A pygame-based Ultimate Tic Tac Toe game where each cell contains another tic tac toe board.

## Installation

### 1. Install Miniforge

#### Windows

1. Download the Miniforge installer from [github.com/conda-forge/miniforge/releases](https://github.com/conda-forge/miniforge/releases)
   - Choose `Miniforge3-Windows-x86_64.exe`

2. Run the installer and follow the prompts
   - Select "Add Miniforge3 to my PATH environment variable" (optional but recommended)

3. Open a new terminal (Command Prompt or PowerShell) to use conda

#### macOS

Option A - Using Homebrew:
```bash
brew install miniforge
```

Option B - Manual install:
```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-$(uname -m).sh"
bash Miniforge3-MacOSX-$(uname -m).sh
```

Follow the prompts and restart your terminal when complete.

### 2. Create the Conda Environment

```bash
conda env create -f environment.yml
```

### 3. Activate the Environment

```bash
conda activate tictactoe
```

### 4. Run the Game

```bash
python ultimate_tictactoe.py
```

## Controls

- **Click** - Place your mark
- **R** - Restart game
- **E** - Return to home screen

## Game Modes

- **1 Player** - Play against AI (Easy, Medium, or Big Brain difficulty)
- **2 Players** - Local multiplayer
