"""
Ultimate Tic Tac Toe Game
A tic tac toe game where each square contains another tic tac toe game.

Rules:
- The board is a 3x3 grid of 3x3 tic tac toe sub-boards
- Players take turns placing X and O
- When you play in a cell, your opponent must play in the corresponding sub-board
- If the required sub-board is already won or full, the opponent can play anywhere
- Win a sub-board by getting 3 in a row
- Win the game by winning 3 sub-boards in a row
"""

import pygame
import sys
import os
import random
import math
import copy
from typing import Optional, Tuple, List
from enum import Enum


class GameMode(Enum):
    TWO_PLAYER = "2 Players"
    ONE_PLAYER = "1 Player"


class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    BIG_BRAIN = "Big Brain"

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
RED = (220, 50, 50)
BLUE = (50, 50, 220)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 150)
LIGHT_BLUE = (200, 220, 255)
LIGHT_RED = (255, 200, 200)
DARK_BLUE = (20, 20, 80)
GOLD = (255, 215, 0)

# Confetti colors
CONFETTI_COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (255, 0, 255),  # Magenta
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (255, 192, 203),# Pink
    (148, 0, 211),  # Purple
    (0, 255, 127),  # Spring Green
]

# Game settings (default sizes, will be recalculated on resize)
DEFAULT_WINDOW_SIZE = 630
DEFAULT_BOARD_SIZE = 600
DEFAULT_MARGIN = 15
DEFAULT_STATUS_HEIGHT = 40
MIN_WINDOW_SIZE = 400

# Get the directory where the script is located
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()
SOUNDS_DIR = os.path.join(SCRIPT_DIR, 'sounds')

# Fonts
pygame.font.init()
FONT_LARGE = pygame.font.SysFont('Arial', 48, bold=True)
FONT_MEDIUM = pygame.font.SysFont('Arial', 24)
FONT_SMALL = pygame.font.SysFont('Arial', 18)
FONT_TITLE = pygame.font.SysFont('Arial', 42, bold=True)
FONT_SUBTITLE = pygame.font.SysFont('Arial', 22)
FONT_BROKE_EVEN = pygame.font.SysFont('Arial', 56, bold=True)
FONT_BUTTON = pygame.font.SysFont('Arial', 28, bold=True)
FONT_MENU_TITLE = pygame.font.SysFont('Arial', 36, bold=True)


class SoundManager:
    """Manages all game sounds."""

    def __init__(self):
        self.sounds = {}
        self._load_sounds()

    def _load_sounds(self):
        """Load all sound files."""
        sound_files = {
            'win': 'win.wav',
            'sad': 'sad.wav',
            'stamp': 'stamp.wav',
            'click': 'click.wav'
        }

        for name, filename in sound_files.items():
            path = os.path.join(SOUNDS_DIR, filename)
            try:
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"Could not load sound {filename}: {e}")

    def play(self, name: str):
        """Play a sound by name."""
        if name in self.sounds:
            self.sounds[name].play()


class ConfettiParticle:
    """A single confetti particle."""

    def __init__(self, x: float, y: float, max_y: int):
        self.x = x
        self.y = y
        self.max_y = max_y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-12, -6)
        self.color = random.choice(CONFETTI_COLORS)
        self.size = random.randint(6, 12)
        self.rotation = random.uniform(0, 360)
        self.rotation_speed = random.uniform(-10, 10)
        self.gravity = 0.3
        self.lifetime = 1.0
        self.decay = random.uniform(0.005, 0.015)

    def update(self):
        """Update particle position and state."""
        self.x += self.vx
        self.vy += self.gravity
        self.y += self.vy
        self.vx *= 0.99  # Air resistance
        self.rotation += self.rotation_speed
        self.lifetime -= self.decay

    def draw(self, screen: pygame.Surface):
        """Draw the confetti particle."""
        if self.lifetime <= 0:
            return

        alpha = int(255 * self.lifetime)
        # Create a surface for the confetti piece
        surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        color_with_alpha = (*self.color, alpha)
        pygame.draw.rect(surf, color_with_alpha, (0, 0, self.size, self.size // 2))

        # Rotate the surface
        rotated = pygame.transform.rotate(surf, self.rotation)
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated, rect)

    def is_alive(self) -> bool:
        """Check if particle is still visible."""
        return self.lifetime > 0 and self.y < self.max_y + 50


class ConfettiSystem:
    """Manages confetti particle effects."""

    def __init__(self):
        self.particles: List[ConfettiParticle] = []
        self.active = False

    def trigger(self, window_width: int, window_height: int):
        """Trigger a confetti explosion."""
        self.active = True
        # Create particles from multiple points across the top
        for _ in range(150):
            x = random.randint(0, window_width)
            y = random.randint(-50, 50)
            self.particles.append(ConfettiParticle(x, y, window_height))

        # Add some from the sides
        for _ in range(50):
            x = random.choice([0, window_width])
            y = random.randint(0, window_height // 2)
            p = ConfettiParticle(x, y, window_height)
            if x == 0:
                p.vx = abs(p.vx)
            else:
                p.vx = -abs(p.vx)
            self.particles.append(p)

    def update(self):
        """Update all particles."""
        for particle in self.particles:
            particle.update()
        # Remove dead particles
        self.particles = [p for p in self.particles if p.is_alive()]
        if not self.particles:
            self.active = False

    def draw(self, screen: pygame.Surface):
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen)


class SplashScreen:
    """Animated splash screen with stamp effect."""

    SPLASH_DURATION = 5000  # 5 seconds in milliseconds

    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.done = False
        self.clock = pygame.time.Clock()

        # Animation state
        self.stamp_scale = 3.0  # Start large
        self.stamp_alpha = 0
        self.stamp_rotation = -15
        self.stamp_phase = 0  # 0: scaling down, 1: impact, 2: settling, 3: fade in text, 4: wait
        self.phase_timer = 0
        self.shake_offset = (0, 0)

        # Text surfaces
        self.title_text = "TicTacToe Ultimate"
        self.subtitle_text = "by DaughterNFather Games"

    def run(self):
        """Run the splash screen animation."""
        start_time = pygame.time.get_ticks()
        stamp_played = False

        while not self.done:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds
            current_time = pygame.time.get_ticks() - start_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Skip splash screen on click only (after stamp lands)
                    if self.stamp_phase >= 2:
                        self.sound_manager.play('click')
                        self.done = True
                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize during splash
                    self.screen = pygame.display.set_mode(
                        (event.w, event.h), pygame.RESIZABLE
                    )

            # Update animation
            self.phase_timer += dt

            if self.stamp_phase == 0:  # Scaling down
                self.stamp_scale = max(1.0, 3.0 - self.phase_timer * 8)
                self.stamp_alpha = min(255, int(self.phase_timer * 600))
                if self.stamp_scale <= 1.0:
                    self.stamp_phase = 1
                    self.phase_timer = 0
                    if not stamp_played:
                        self.sound_manager.play('stamp')
                        stamp_played = True

            elif self.stamp_phase == 1:  # Impact shake
                shake_intensity = max(0, 10 - self.phase_timer * 50)
                self.shake_offset = (
                    random.uniform(-shake_intensity, shake_intensity),
                    random.uniform(-shake_intensity, shake_intensity)
                )
                if self.phase_timer > 0.2:
                    self.stamp_phase = 2
                    self.phase_timer = 0
                    self.shake_offset = (0, 0)

            elif self.stamp_phase == 2:  # Settling
                if self.phase_timer > 0.3:
                    self.stamp_phase = 3
                    self.phase_timer = 0

            elif self.stamp_phase == 3:  # Show subtitle
                if self.phase_timer > 0.5:
                    self.stamp_phase = 4
                    self.phase_timer = 0

            elif self.stamp_phase == 4:  # Wait for timeout or click
                pass  # Just wait for 5 second timeout or click

            # Draw
            self._draw()

            # Exit after 5 seconds
            if current_time >= self.SPLASH_DURATION:
                self.done = True

    def _draw(self):
        """Draw the splash screen."""
        width, height = self.screen.get_size()

        # Dark blue background
        self.screen.fill(DARK_BLUE)

        # Calculate center position with shake
        center_x = width // 2 + self.shake_offset[0]
        center_y = height // 2 - 30 + self.shake_offset[1]

        # Draw stamp frame/border
        if self.stamp_phase >= 1:
            frame_width = min(400, width - 40)
            frame_height = 150
            frame_rect = pygame.Rect(
                center_x - frame_width // 2,
                center_y - frame_height // 2,
                frame_width,
                frame_height
            )
            pygame.draw.rect(self.screen, GOLD, frame_rect, 4)
            # Inner frame
            inner_rect = frame_rect.inflate(-16, -16)
            pygame.draw.rect(self.screen, GOLD, inner_rect, 2)

        # Draw title text with stamp effect
        title_surf = FONT_TITLE.render(self.title_text, True, GOLD)

        if self.stamp_scale > 1.0:
            # Scale the text
            scaled_width = int(title_surf.get_width() * self.stamp_scale)
            scaled_height = int(title_surf.get_height() * self.stamp_scale)
            title_surf = pygame.transform.scale(title_surf, (scaled_width, scaled_height))

        # Apply alpha
        title_surf.set_alpha(self.stamp_alpha)

        # Rotate slightly for stamp effect
        if self.stamp_phase < 2:
            title_surf = pygame.transform.rotate(title_surf, self.stamp_rotation * (self.stamp_scale - 1))

        title_rect = title_surf.get_rect(center=(center_x, center_y - 15))
        self.screen.blit(title_surf, title_rect)

        # Draw subtitle after stamp lands
        if self.stamp_phase >= 3:
            alpha = min(255, int(self.phase_timer * 500))
            subtitle_surf = FONT_SUBTITLE.render(self.subtitle_text, True, WHITE)
            subtitle_surf.set_alpha(alpha)
            subtitle_rect = subtitle_surf.get_rect(center=(center_x, center_y + 35))
            self.screen.blit(subtitle_surf, subtitle_rect)

        # Draw "Click to continue" hint
        if self.stamp_phase >= 4:
            hint_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 300))
            hint_surf = FONT_SMALL.render("Click to continue", True, LIGHT_GRAY)
            hint_surf.set_alpha(hint_alpha)
            hint_rect = hint_surf.get_rect(center=(width // 2, height - 50))
            self.screen.blit(hint_surf, hint_rect)

        pygame.display.flip()


class MenuButton:
    """A clickable button for menus."""

    def __init__(self, x: int, y: int, width: int, height: int, text: str,
                 color: Tuple[int, int, int] = BLUE, hover_color: Tuple[int, int, int] = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or tuple(min(c + 40, 255) for c in color)
        self.is_hovered = False

    def update_position(self, x: int, y: int):
        """Update button position."""
        self.rect.x = x
        self.rect.y = y

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        color = self.hover_color if self.is_hovered else self.color

        # Draw button background with rounded corners
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        # Draw border
        border_color = tuple(max(c - 40, 0) for c in color)
        pygame.draw.rect(screen, border_color, self.rect, width=3, border_radius=10)

        # Draw text
        text_surf = FONT_BUTTON.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


class ModeSelectScreen:
    """Screen for selecting 1 Player or 2 Players mode."""

    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.clock = pygame.time.Clock()
        self.selected_mode: Optional[GameMode] = None

        # Create buttons
        self._create_buttons()

    def _create_buttons(self):
        """Create the mode selection buttons."""
        width, height = self.screen.get_size()
        button_width = 200
        button_height = 60
        spacing = 30

        center_x = width // 2
        center_y = height // 2

        self.one_player_btn = MenuButton(
            center_x - button_width // 2,
            center_y - button_height - spacing // 2,
            button_width, button_height,
            "1 Player",
            color=BLUE
        )

        self.two_player_btn = MenuButton(
            center_x - button_width // 2,
            center_y + spacing // 2,
            button_width, button_height,
            "2 Players",
            color=RED
        )

    def run(self) -> GameMode:
        """Run the mode selection screen. Returns selected game mode."""
        while self.selected_mode is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (max(MIN_WINDOW_SIZE, event.w), max(MIN_WINDOW_SIZE, event.h)),
                        pygame.RESIZABLE
                    )
                    self._create_buttons()

                elif event.type == pygame.MOUSEMOTION:
                    self.one_player_btn.handle_event(event)
                    self.two_player_btn.handle_event(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.one_player_btn.handle_event(event):
                        self.sound_manager.play('click')
                        self.selected_mode = GameMode.ONE_PLAYER
                    elif self.two_player_btn.handle_event(event):
                        self.sound_manager.play('click')
                        self.selected_mode = GameMode.TWO_PLAYER

            self._draw()
            self.clock.tick(60)

        return self.selected_mode

    def _draw(self):
        """Draw the mode selection screen."""
        width, height = self.screen.get_size()
        self.screen.fill(DARK_BLUE)

        # Draw title
        title_surf = FONT_MENU_TITLE.render("Select Game Mode", True, GOLD)
        title_rect = title_surf.get_rect(center=(width // 2, height // 3))
        self.screen.blit(title_surf, title_rect)

        # Draw buttons
        self.one_player_btn.draw(self.screen)
        self.two_player_btn.draw(self.screen)

        pygame.display.flip()


class DifficultySelectScreen:
    """Screen for selecting AI difficulty."""

    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.clock = pygame.time.Clock()
        self.selected_difficulty: Optional[Difficulty] = None

        # Create buttons
        self._create_buttons()

    def _create_buttons(self):
        """Create the difficulty selection buttons."""
        width, height = self.screen.get_size()
        button_width = 200
        button_height = 60
        spacing = 20

        center_x = width // 2
        start_y = height // 2 - button_height - spacing

        self.easy_btn = MenuButton(
            center_x - button_width // 2,
            start_y,
            button_width, button_height,
            "Easy",
            color=GREEN
        )

        self.medium_btn = MenuButton(
            center_x - button_width // 2,
            start_y + button_height + spacing,
            button_width, button_height,
            "Medium",
            color=(255, 165, 0)  # Orange
        )

        self.bigbrain_btn = MenuButton(
            center_x - button_width // 2,
            start_y + 2 * (button_height + spacing),
            button_width, button_height,
            "Big Brain",
            color=(148, 0, 211)  # Purple
        )

    def run(self) -> Difficulty:
        """Run the difficulty selection screen. Returns selected difficulty."""
        while self.selected_difficulty is None:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (max(MIN_WINDOW_SIZE, event.w), max(MIN_WINDOW_SIZE, event.h)),
                        pygame.RESIZABLE
                    )
                    self._create_buttons()

                elif event.type == pygame.MOUSEMOTION:
                    self.easy_btn.handle_event(event)
                    self.medium_btn.handle_event(event)
                    self.bigbrain_btn.handle_event(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.easy_btn.handle_event(event):
                        self.sound_manager.play('click')
                        self.selected_difficulty = Difficulty.EASY
                    elif self.medium_btn.handle_event(event):
                        self.sound_manager.play('click')
                        self.selected_difficulty = Difficulty.MEDIUM
                    elif self.bigbrain_btn.handle_event(event):
                        self.sound_manager.play('click')
                        self.selected_difficulty = Difficulty.BIG_BRAIN

            self._draw()
            self.clock.tick(60)

        return self.selected_difficulty

    def _draw(self):
        """Draw the difficulty selection screen."""
        width, height = self.screen.get_size()
        self.screen.fill(DARK_BLUE)

        # Draw title
        title_surf = FONT_MENU_TITLE.render("Select Difficulty", True, GOLD)
        title_rect = title_surf.get_rect(center=(width // 2, height // 4))
        self.screen.blit(title_surf, title_rect)

        # Draw subtitle
        subtitle_surf = FONT_SUBTITLE.render("You are X, AI is O", True, WHITE)
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, height // 4 + 40))
        self.screen.blit(subtitle_surf, subtitle_rect)

        # Draw buttons
        self.easy_btn.draw(self.screen)
        self.medium_btn.draw(self.screen)
        self.bigbrain_btn.draw(self.screen)

        pygame.display.flip()


class SubBoard:
    """Represents a single 3x3 tic tac toe board."""

    def __init__(self):
        self.cells: List[List[Optional[str]]] = [[None for _ in range(3)] for _ in range(3)]
        self.winner: Optional[str] = None

    def make_move(self, row: int, col: int, player: str) -> bool:
        """Make a move on the sub-board. Returns True if successful."""
        if self.cells[row][col] is None and self.winner is None:
            self.cells[row][col] = player
            self._check_winner()
            return True
        return False

    def _check_winner(self):
        """Check if there's a winner on this sub-board."""
        # Check rows
        for row in range(3):
            if self.cells[row][0] and self.cells[row][0] == self.cells[row][1] == self.cells[row][2]:
                self.winner = self.cells[row][0]
                return

        # Check columns
        for col in range(3):
            if self.cells[0][col] and self.cells[0][col] == self.cells[1][col] == self.cells[2][col]:
                self.winner = self.cells[0][col]
                return

        # Check diagonals
        if self.cells[1][1]:
            if self.cells[0][0] == self.cells[1][1] == self.cells[2][2]:
                self.winner = self.cells[1][1]
                return
            if self.cells[0][2] == self.cells[1][1] == self.cells[2][0]:
                self.winner = self.cells[1][1]
                return

    def is_full(self) -> bool:
        """Check if all cells are filled."""
        return all(self.cells[row][col] is not None for row in range(3) for col in range(3))

    def is_playable(self) -> bool:
        """Check if moves can still be made on this sub-board."""
        return self.winner is None and not self.is_full()


class UltimateTicTacToe:
    """Main game class for Ultimate Tic Tac Toe."""

    def __init__(self):
        self.sub_boards: List[List[SubBoard]] = [[SubBoard() for _ in range(3)] for _ in range(3)]
        self.current_player: str = 'X'
        self.active_board: Optional[Tuple[int, int]] = None  # None means any board is valid
        self.winner: Optional[str] = None
        self.game_over: bool = False
        self.just_ended: bool = False  # Flag to trigger end game effects

    def make_move(self, board_row: int, board_col: int, cell_row: int, cell_col: int) -> bool:
        """
        Make a move on the specified sub-board and cell.
        Returns True if the move was successful.
        """
        if self.game_over:
            return False

        # Check if this board is the active one (or if any board is valid)
        if self.active_board is not None:
            if (board_row, board_col) != self.active_board:
                return False

        sub_board = self.sub_boards[board_row][board_col]

        # Check if the sub-board is still playable
        if not sub_board.is_playable():
            return False

        # Try to make the move
        if sub_board.make_move(cell_row, cell_col, self.current_player):
            # Check for game winner
            was_over = self.game_over
            self._check_winner()

            if self.game_over and not was_over:
                self.just_ended = True

            if not self.game_over:
                # Determine next active board
                next_board = self.sub_boards[cell_row][cell_col]
                if next_board.is_playable():
                    self.active_board = (cell_row, cell_col)
                else:
                    self.active_board = None  # Any playable board is valid

                # Switch player
                self.current_player = 'O' if self.current_player == 'X' else 'X'

            return True

        return False

    def _check_winner(self):
        """Check if there's a winner of the entire game."""
        # Create a grid of sub-board winners
        winners = [[self.sub_boards[r][c].winner for c in range(3)] for r in range(3)]

        # Check rows
        for row in range(3):
            if winners[row][0] and winners[row][0] == winners[row][1] == winners[row][2]:
                self.winner = winners[row][0]
                self.game_over = True
                return

        # Check columns
        for col in range(3):
            if winners[0][col] and winners[0][col] == winners[1][col] == winners[2][col]:
                self.winner = winners[0][col]
                self.game_over = True
                return

        # Check diagonals
        if winners[1][1]:
            if winners[0][0] == winners[1][1] == winners[2][2]:
                self.winner = winners[1][1]
                self.game_over = True
                return
            if winners[0][2] == winners[1][1] == winners[2][0]:
                self.winner = winners[1][1]
                self.game_over = True
                return

        # Check for draw (all sub-boards won or full)
        if all(not self.sub_boards[r][c].is_playable() for r in range(3) for c in range(3)):
            self.game_over = True

    def is_valid_board(self, board_row: int, board_col: int) -> bool:
        """Check if moves can be made on this sub-board."""
        if self.game_over:
            return False

        sub_board = self.sub_boards[board_row][board_col]
        if not sub_board.is_playable():
            return False

        if self.active_board is None:
            return True

        return (board_row, board_col) == self.active_board

    def is_draw(self) -> bool:
        """Check if the game ended in a draw."""
        return self.game_over and self.winner is None

    def get_valid_moves(self) -> List[Tuple[int, int, int, int]]:
        """Get all valid moves as (board_row, board_col, cell_row, cell_col) tuples."""
        moves = []
        for br in range(3):
            for bc in range(3):
                if self.is_valid_board(br, bc):
                    sub_board = self.sub_boards[br][bc]
                    for cr in range(3):
                        for cc in range(3):
                            if sub_board.cells[cr][cc] is None:
                                moves.append((br, bc, cr, cc))
        return moves

    def clone(self) -> 'UltimateTicTacToe':
        """Create a deep copy of the game state."""
        new_game = UltimateTicTacToe()
        new_game.current_player = self.current_player
        new_game.active_board = self.active_board
        new_game.winner = self.winner
        new_game.game_over = self.game_over
        new_game.just_ended = self.just_ended

        for br in range(3):
            for bc in range(3):
                for cr in range(3):
                    for cc in range(3):
                        new_game.sub_boards[br][bc].cells[cr][cc] = self.sub_boards[br][bc].cells[cr][cc]
                new_game.sub_boards[br][bc].winner = self.sub_boards[br][bc].winner

        return new_game


class AIPlayer:
    """AI opponent with different difficulty levels."""

    def __init__(self, difficulty: Difficulty, player_symbol: str = 'O'):
        self.difficulty = difficulty
        self.player_symbol = player_symbol
        self.opponent_symbol = 'X' if player_symbol == 'O' else 'O'

    def get_move(self, game: UltimateTicTacToe) -> Optional[Tuple[int, int, int, int]]:
        """Get the AI's next move based on difficulty."""
        if game.game_over or game.current_player != self.player_symbol:
            return None

        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return None

        if self.difficulty == Difficulty.EASY:
            return self._easy_move(valid_moves)
        elif self.difficulty == Difficulty.MEDIUM:
            return self._medium_move(game, valid_moves)
        else:  # BIG_BRAIN
            return self._bigbrain_move(game, valid_moves)

    def _easy_move(self, valid_moves: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        """Easy AI: Random valid move."""
        return random.choice(valid_moves)

    def _medium_move(self, game: UltimateTicTacToe,
                     valid_moves: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        """Medium AI: Basic strategy - win, block, prefer center/corners."""

        # Group moves by sub-board
        moves_by_board = {}
        for move in valid_moves:
            br, bc = move[0], move[1]
            if (br, bc) not in moves_by_board:
                moves_by_board[(br, bc)] = []
            moves_by_board[(br, bc)].append(move)

        # Priority 1: Win a sub-board
        for (br, bc), moves in moves_by_board.items():
            winning_move = self._find_winning_move(game.sub_boards[br][bc], moves, self.player_symbol)
            if winning_move:
                return winning_move

        # Priority 2: Block opponent from winning a sub-board
        for (br, bc), moves in moves_by_board.items():
            blocking_move = self._find_winning_move(game.sub_boards[br][bc], moves, self.opponent_symbol)
            if blocking_move:
                return blocking_move

        # Priority 3: Take center of a sub-board
        for move in valid_moves:
            if move[2] == 1 and move[3] == 1:  # Center cell
                return move

        # Priority 4: Take corners
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        corner_moves = [m for m in valid_moves if (m[2], m[3]) in corners]
        if corner_moves:
            return random.choice(corner_moves)

        # Priority 5: Random move
        return random.choice(valid_moves)

    def _find_winning_move(self, sub_board: 'SubBoard', moves: List[Tuple[int, int, int, int]],
                           player: str) -> Optional[Tuple[int, int, int, int]]:
        """Find a move that would win the sub-board for the given player."""
        for move in moves:
            cr, cc = move[2], move[3]
            # Simulate the move
            original = sub_board.cells[cr][cc]
            sub_board.cells[cr][cc] = player

            # Check if this wins
            if self._check_sub_board_win(sub_board, player):
                sub_board.cells[cr][cc] = original
                return move

            sub_board.cells[cr][cc] = original
        return None

    def _check_sub_board_win(self, sub_board: 'SubBoard', player: str) -> bool:
        """Check if the player has won this sub-board."""
        cells = sub_board.cells

        # Check rows
        for row in range(3):
            if cells[row][0] == cells[row][1] == cells[row][2] == player:
                return True

        # Check columns
        for col in range(3):
            if cells[0][col] == cells[1][col] == cells[2][col] == player:
                return True

        # Check diagonals
        if cells[0][0] == cells[1][1] == cells[2][2] == player:
            return True
        if cells[0][2] == cells[1][1] == cells[2][0] == player:
            return True

        return False

    def _bigbrain_move(self, game: UltimateTicTacToe,
                       valid_moves: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        """Big Brain AI: Minimax with alpha-beta pruning."""
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        # Limit search depth based on number of valid moves
        max_depth = 4 if len(valid_moves) > 20 else 5 if len(valid_moves) > 10 else 6

        for move in valid_moves:
            game_copy = game.clone()
            game_copy.make_move(*move)

            score = self._minimax(game_copy, max_depth - 1, alpha, beta, False)

            if score > best_score:
                best_score = score
                best_move = move

            alpha = max(alpha, score)

        return best_move if best_move else random.choice(valid_moves)

    def _minimax(self, game: UltimateTicTacToe, depth: int, alpha: float, beta: float,
                 is_maximizing: bool) -> float:
        """Minimax algorithm with alpha-beta pruning."""
        # Terminal conditions
        if game.game_over:
            if game.winner == self.player_symbol:
                return 1000 + depth  # Prefer faster wins
            elif game.winner == self.opponent_symbol:
                return -1000 - depth  # Avoid faster losses
            else:
                return 0  # Draw

        if depth <= 0:
            return self._evaluate_position(game)

        valid_moves = game.get_valid_moves()
        if not valid_moves:
            return 0

        if is_maximizing:
            max_score = float('-inf')
            for move in valid_moves:
                game_copy = game.clone()
                game_copy.make_move(*move)
                score = self._minimax(game_copy, depth - 1, alpha, beta, False)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break
            return max_score
        else:
            min_score = float('inf')
            for move in valid_moves:
                game_copy = game.clone()
                game_copy.make_move(*move)
                score = self._minimax(game_copy, depth - 1, alpha, beta, True)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score

    def _evaluate_position(self, game: UltimateTicTacToe) -> float:
        """Evaluate the current game position for the AI."""
        score = 0.0

        # Evaluate meta-board (which sub-boards are won)
        meta_board = [[game.sub_boards[r][c].winner for c in range(3)] for r in range(3)]

        # Count won sub-boards
        ai_boards = sum(1 for r in range(3) for c in range(3) if meta_board[r][c] == self.player_symbol)
        opp_boards = sum(1 for r in range(3) for c in range(3) if meta_board[r][c] == self.opponent_symbol)
        score += (ai_boards - opp_boards) * 50

        # Evaluate lines on meta-board (potential wins)
        score += self._evaluate_lines(meta_board, self.player_symbol) * 20
        score -= self._evaluate_lines(meta_board, self.opponent_symbol) * 20

        # Evaluate control of center sub-board
        if meta_board[1][1] == self.player_symbol:
            score += 30
        elif meta_board[1][1] == self.opponent_symbol:
            score -= 30

        # Evaluate corner control
        corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
        for r, c in corners:
            if meta_board[r][c] == self.player_symbol:
                score += 15
            elif meta_board[r][c] == self.opponent_symbol:
                score -= 15

        # Evaluate individual sub-boards that are still in play
        for br in range(3):
            for bc in range(3):
                if game.sub_boards[br][bc].is_playable():
                    sub_score = self._evaluate_sub_board(game.sub_boards[br][bc])
                    # Weight sub-boards by strategic importance
                    weight = 3 if (br, bc) == (1, 1) else 2 if (br, bc) in corners else 1
                    score += sub_score * weight

        return score

    def _evaluate_lines(self, board: List[List[Optional[str]]], player: str) -> int:
        """Count the number of potential winning lines for a player."""
        count = 0
        opponent = self.opponent_symbol if player == self.player_symbol else self.player_symbol

        lines = [
            # Rows
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            # Columns
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            # Diagonals
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]

        for line in lines:
            values = [board[r][c] for r, c in line]
            player_count = values.count(player)
            opponent_count = values.count(opponent)

            if opponent_count == 0:
                if player_count == 2:
                    count += 3  # One away from winning
                elif player_count == 1:
                    count += 1

        return count

    def _evaluate_sub_board(self, sub_board: 'SubBoard') -> float:
        """Evaluate a single sub-board position."""
        score = 0.0
        cells = sub_board.cells

        # Evaluate lines
        lines = [
            [(0, 0), (0, 1), (0, 2)],
            [(1, 0), (1, 1), (1, 2)],
            [(2, 0), (2, 1), (2, 2)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 1), (1, 1), (2, 1)],
            [(0, 2), (1, 2), (2, 2)],
            [(0, 0), (1, 1), (2, 2)],
            [(0, 2), (1, 1), (2, 0)],
        ]

        for line in lines:
            values = [cells[r][c] for r, c in line]
            ai_count = values.count(self.player_symbol)
            opp_count = values.count(self.opponent_symbol)

            if opp_count == 0 and ai_count > 0:
                score += ai_count * 2
            elif ai_count == 0 and opp_count > 0:
                score -= opp_count * 2

        # Center control
        if cells[1][1] == self.player_symbol:
            score += 3
        elif cells[1][1] == self.opponent_symbol:
            score -= 3

        return score


class GameRenderer:
    """Handles all rendering for the game."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.broke_even_alpha = 0
        self.broke_even_scale = 0.5
        self.game_mode: Optional[GameMode] = None
        self.difficulty: Optional[Difficulty] = None
        self.home_button_hovered = False
        self._update_dimensions()
        self._create_home_button()

    def set_game_info(self, game_mode: GameMode, difficulty: Optional[Difficulty]):
        """Set the game mode and difficulty for display."""
        self.game_mode = game_mode
        self.difficulty = difficulty

    def _create_home_button(self):
        """Create the home button (will be positioned in _draw_status)."""
        # Initial placeholder rect - will be updated in _draw_status
        self.home_button_rect = pygame.Rect(0, 0, 150, 24)

    def check_home_button_click(self, pos: Tuple[int, int]) -> bool:
        """Check if the home button was clicked."""
        return self.home_button_rect.collidepoint(pos)

    def check_home_button_hover(self, pos: Tuple[int, int]):
        """Check if mouse is hovering over home button."""
        self.home_button_hovered = self.home_button_rect.collidepoint(pos)

    def _update_dimensions(self):
        """Calculate dimensions based on current screen size."""
        width, height = self.screen.get_size()
        self.window_width = width
        self.window_height = height

        # Calculate board size to fit in window (leave room for status bar)
        status_height = DEFAULT_STATUS_HEIGHT
        available_size = min(width, height - status_height)

        self.margin = max(10, available_size // 42)  # Scale margin with size
        self.board_size = available_size - (2 * self.margin)
        self.cell_size = self.board_size // 9
        self.sub_board_size = self.cell_size * 3

        # Recalculate board_size to be exact multiple of 9
        self.board_size = self.cell_size * 9

        # Center the board horizontally
        self.board_offset_x = (width - self.board_size) // 2
        self.board_offset_y = self.margin

    def update_screen(self, screen: pygame.Surface):
        """Update screen reference and recalculate dimensions."""
        self.screen = screen
        self._update_dimensions()

    def draw(self, game: UltimateTicTacToe, confetti: ConfettiSystem):
        """Draw the entire game state."""
        self.screen.fill(WHITE)

        # Draw sub-boards
        for board_row in range(3):
            for board_col in range(3):
                self._draw_sub_board(game, board_row, board_col)

        # Draw main grid lines (thicker)
        self._draw_main_grid()

        # Draw game status (includes home button)
        self._draw_status(game)

        # Draw confetti on top
        confetti.draw(self.screen)

        # Draw "Broke Even" text for draws
        if game.is_draw():
            self._draw_broke_even()

    def _draw_broke_even(self):
        """Draw the 'Broke Even' text for draws."""
        # Animate alpha and scale
        self.broke_even_alpha = min(255, self.broke_even_alpha + 8)
        self.broke_even_scale = min(1.0, self.broke_even_scale + 0.03)

        # Create text surface
        text_surf = FONT_BROKE_EVEN.render("BROKE EVEN", True, GRAY)

        # Scale if needed
        if self.broke_even_scale < 1.0:
            new_width = int(text_surf.get_width() * self.broke_even_scale)
            new_height = int(text_surf.get_height() * self.broke_even_scale)
            text_surf = pygame.transform.scale(text_surf, (new_width, new_height))

        text_surf.set_alpha(self.broke_even_alpha)

        # Draw semi-transparent background
        bg_rect = pygame.Rect(0, self.window_height // 2 - 50, self.window_width, 100)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        bg_surf.fill((255, 255, 255, int(200 * (self.broke_even_alpha / 255))))
        self.screen.blit(bg_surf, bg_rect)

        # Draw text centered
        text_rect = text_surf.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.screen.blit(text_surf, text_rect)

    def reset_animations(self):
        """Reset animation states."""
        self.broke_even_alpha = 0
        self.broke_even_scale = 0.5

    def _draw_sub_board(self, game: UltimateTicTacToe, board_row: int, board_col: int):
        """Draw a single sub-board."""
        sub_board = game.sub_boards[board_row][board_col]
        base_x = self.board_offset_x + board_col * self.sub_board_size
        base_y = self.board_offset_y + board_row * self.sub_board_size

        # Draw background for active/playable boards
        if game.is_valid_board(board_row, board_col):
            highlight_color = LIGHT_BLUE if game.current_player == 'X' else LIGHT_RED
            pygame.draw.rect(self.screen, highlight_color,
                           (base_x, base_y, self.sub_board_size, self.sub_board_size))

        # Draw won board overlay
        if sub_board.winner:
            overlay_color = LIGHT_BLUE if sub_board.winner == 'X' else LIGHT_RED
            pygame.draw.rect(self.screen, overlay_color,
                           (base_x, base_y, self.sub_board_size, self.sub_board_size))
            # Draw large X or O
            self._draw_large_symbol(sub_board.winner, base_x, base_y)

        # Draw grid lines for sub-board
        line_width = max(1, self.cell_size // 30)
        for i in range(1, 3):
            # Vertical lines
            pygame.draw.line(self.screen, GRAY,
                           (base_x + i * self.cell_size, base_y),
                           (base_x + i * self.cell_size, base_y + self.sub_board_size), line_width)
            # Horizontal lines
            pygame.draw.line(self.screen, GRAY,
                           (base_x, base_y + i * self.cell_size),
                           (base_x + self.sub_board_size, base_y + i * self.cell_size), line_width)

        # Draw X's and O's in cells
        if not sub_board.winner:
            for cell_row in range(3):
                for cell_col in range(3):
                    player = sub_board.cells[cell_row][cell_col]
                    if player:
                        cell_x = base_x + cell_col * self.cell_size
                        cell_y = base_y + cell_row * self.cell_size
                        self._draw_symbol(player, cell_x, cell_y, self.cell_size)

    def _draw_main_grid(self):
        """Draw the main 3x3 grid lines."""
        line_width = max(2, self.cell_size // 20)
        for i in range(4):
            # Vertical lines
            x = self.board_offset_x + i * self.sub_board_size
            pygame.draw.line(self.screen, BLACK,
                           (x, self.board_offset_y), (x, self.board_offset_y + self.board_size), line_width)
            # Horizontal lines
            y = self.board_offset_y + i * self.sub_board_size
            pygame.draw.line(self.screen, BLACK,
                           (self.board_offset_x, y), (self.board_offset_x + self.board_size, y), line_width)

    def _draw_symbol(self, player: str, x: int, y: int, size: int):
        """Draw X or O in a cell."""
        padding = size // 5
        line_width = max(2, size // 20)
        if player == 'X':
            pygame.draw.line(self.screen, BLUE,
                           (x + padding, y + padding),
                           (x + size - padding, y + size - padding), line_width)
            pygame.draw.line(self.screen, BLUE,
                           (x + size - padding, y + padding),
                           (x + padding, y + size - padding), line_width)
        else:  # O
            center = (x + size // 2, y + size // 2)
            radius = size // 2 - padding
            pygame.draw.circle(self.screen, RED, center, radius, line_width)

    def _draw_large_symbol(self, player: str, x: int, y: int):
        """Draw a large X or O for a won sub-board."""
        padding = self.sub_board_size // 6
        line_width = max(4, self.sub_board_size // 25)
        if player == 'X':
            pygame.draw.line(self.screen, BLUE,
                           (x + padding, y + padding),
                           (x + self.sub_board_size - padding, y + self.sub_board_size - padding), line_width)
            pygame.draw.line(self.screen, BLUE,
                           (x + self.sub_board_size - padding, y + padding),
                           (x + padding, y + self.sub_board_size - padding), line_width)
        else:  # O
            center = (x + self.sub_board_size // 2, y + self.sub_board_size // 2)
            radius = self.sub_board_size // 2 - padding
            pygame.draw.circle(self.screen, RED, center, radius, line_width)

    def _draw_status(self, game: UltimateTicTacToe):
        """Draw the game status at the bottom."""
        status_y = self.board_offset_y + self.board_size + 5

        if game.game_over:
            if game.winner:
                # In 1 player mode, show "You win!" or "AI wins!"
                if self.game_mode == GameMode.ONE_PLAYER:
                    if game.winner == 'X':
                        text = "You win!"
                    else:
                        text = f"AI ({self.difficulty.value}) wins!"
                else:
                    text = f"Player {game.winner} wins!"
                color = BLUE if game.winner == 'X' else RED
            else:
                text = ""  # We show "Broke Even" instead
                color = BLACK
        else:
            # Show whose turn it is
            if self.game_mode == GameMode.ONE_PLAYER:
                if game.current_player == 'X':
                    text = "Your turn (X)"
                else:
                    text = "AI thinking..."
            else:
                text = f"Player {game.current_player}'s turn"
            color = BLUE if game.current_player == 'X' else RED

        # Draw status text
        if text:
            status_surface = FONT_MEDIUM.render(text, True, color)
            self.screen.blit(status_surface, (self.board_offset_x, status_y))

        # Draw mode info on the right (above the button row)
        if self.game_mode:
            if self.game_mode == GameMode.ONE_PLAYER and self.difficulty:
                mode_text = f"vs {self.difficulty.value} AI"
            else:
                mode_text = "2 Players"
            mode_surface = FONT_SMALL.render(mode_text, True, GRAY)
            mode_x = self.board_offset_x + self.board_size - mode_surface.get_width()
            self.screen.blit(mode_surface, (mode_x, status_y - 2))

        # Bottom row with home and restart hints - centered
        button_row_y = status_y + 18

        # Prepare text surfaces
        home_text = "Press E to Return Home"
        home_color = DARK_BLUE if self.home_button_hovered else GRAY
        home_surface = FONT_SMALL.render(home_text, True, home_color)

        sep_surface = FONT_SMALL.render("|", True, LIGHT_GRAY)

        restart_text = "Press R to Restart"
        restart_surface = FONT_SMALL.render(restart_text, True, GRAY)

        # Calculate total width and center position
        spacing = 15
        total_width = home_surface.get_width() + spacing + sep_surface.get_width() + spacing + restart_surface.get_width()
        screen_width = self.screen.get_width()
        start_x = (screen_width - total_width) // 2

        # Draw home hint
        home_x = start_x
        self.screen.blit(home_surface, (home_x, button_row_y))

        # Update home button rect for click detection
        self.home_button_rect = pygame.Rect(
            home_x - 2, button_row_y - 2,
            home_surface.get_width() + 4, home_surface.get_height() + 4
        )

        # Draw underline when hovered
        if self.home_button_hovered:
            underline_y = button_row_y + home_surface.get_height()
            pygame.draw.line(self.screen, DARK_BLUE,
                           (home_x, underline_y),
                           (home_x + home_surface.get_width(), underline_y), 1)

        # Draw separator
        sep_x = home_x + home_surface.get_width() + spacing
        self.screen.blit(sep_surface, (sep_x, button_row_y))

        # Draw restart hint
        restart_x = sep_x + sep_surface.get_width() + spacing
        self.screen.blit(restart_surface, (restart_x, button_row_y))

    def get_board_and_cell(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int, int, int]]:
        """Convert screen position to board and cell coordinates."""
        x, y = pos
        x -= self.board_offset_x
        y -= self.board_offset_y

        if x < 0 or y < 0 or x >= self.board_size or y >= self.board_size:
            return None

        board_col = x // self.sub_board_size
        board_row = y // self.sub_board_size

        local_x = x % self.sub_board_size
        local_y = y % self.sub_board_size

        cell_col = local_x // self.cell_size
        cell_row = local_y // self.cell_size

        return board_row, board_col, cell_row, cell_col


def main():
    """Main game loop."""
    # Create resizable window
    screen = pygame.display.set_mode(
        (DEFAULT_WINDOW_SIZE, DEFAULT_WINDOW_SIZE + DEFAULT_STATUS_HEIGHT),
        pygame.RESIZABLE
    )
    pygame.display.set_caption("Ultimate Tic Tac Toe")

    # Initialize sound manager
    sound_manager = SoundManager()
    clock = pygame.time.Clock()

    app_running = True
    while app_running:
        # Show splash screen
        splash = SplashScreen(screen, sound_manager)
        splash.run()

        # Get the current screen (may have been resized during splash)
        screen = pygame.display.get_surface()

        # Show mode selection screen
        mode_screen = ModeSelectScreen(screen, sound_manager)
        game_mode = mode_screen.run()

        # Get screen again after mode selection
        screen = pygame.display.get_surface()

        # If 1 player mode, show difficulty selection
        ai_player = None
        difficulty = None
        if game_mode == GameMode.ONE_PLAYER:
            diff_screen = DifficultySelectScreen(screen, sound_manager)
            difficulty = diff_screen.run()
            ai_player = AIPlayer(difficulty, 'O')  # AI plays as O
            screen = pygame.display.get_surface()

        # Initialize game
        game = UltimateTicTacToe()
        renderer = GameRenderer(screen)
        renderer.set_game_info(game_mode, difficulty)
        confetti = ConfettiSystem()

        # AI move timing
        ai_move_delay = 500  # milliseconds delay before AI moves
        ai_move_timer = 0
        ai_waiting = False

        # Game loop
        game_running = True
        return_to_home = False

        while game_running:
            dt = clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
                    app_running = False

                elif event.type == pygame.VIDEORESIZE:
                    # Handle window resize
                    new_width = max(MIN_WINDOW_SIZE, event.w)
                    new_height = max(MIN_WINDOW_SIZE, event.h)
                    screen = pygame.display.set_mode((new_width, new_height), pygame.RESIZABLE)
                    renderer.update_screen(screen)

                elif event.type == pygame.MOUSEMOTION:
                    # Check home button hover
                    renderer.check_home_button_hover(event.pos)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Play click sound on every click
                        sound_manager.play('click')

                        # Check if home button was clicked
                        if renderer.check_home_button_click(event.pos):
                            game_running = False
                            return_to_home = True
                            continue

                        # Only allow player moves when it's their turn
                        if ai_player is None or game.current_player == 'X':
                            coords = renderer.get_board_and_cell(event.pos)
                            if coords:
                                board_row, board_col, cell_row, cell_col = coords
                                if game.make_move(board_row, board_col, cell_row, cell_col):
                                    # If 1 player mode and game not over, trigger AI turn
                                    if ai_player and not game.game_over:
                                        ai_waiting = True
                                        ai_move_timer = 0

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = UltimateTicTacToe()
                        confetti = ConfettiSystem()
                        renderer.reset_animations()
                        ai_waiting = False
                        ai_move_timer = 0
                    elif event.key == pygame.K_ESCAPE:
                        game_running = False
                        app_running = False
                    elif event.key == pygame.K_e:
                        # E key returns to home
                        game_running = False
                        return_to_home = True

            # Handle AI move with delay
            if ai_player and ai_waiting and not game.game_over:
                ai_move_timer += dt
                if ai_move_timer >= ai_move_delay:
                    ai_move = ai_player.get_move(game)
                    if ai_move:
                        game.make_move(*ai_move)
                        sound_manager.play('click')
                    ai_waiting = False
                    ai_move_timer = 0

            # Check for game end triggers
            if game.just_ended:
                game.just_ended = False
                if game.winner:
                    width, height = screen.get_size()
                    confetti.trigger(width, height)
                    sound_manager.play('win')
                else:
                    sound_manager.play('sad')

            # Update confetti
            confetti.update()

            # Draw everything
            renderer.draw(game, confetti)
            pygame.display.flip()

        # If not returning to home, exit the app
        if not return_to_home:
            app_running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
