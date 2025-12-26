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
import numpy as np
from typing import Optional, Tuple, List
from enum import Enum



class GameMode(Enum):
    TWO_PLAYER = "2 Players"
    ONE_PLAYER = "1 Player"


class Difficulty(Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    BIG_BRAIN = "Big Brain"


class TutorialStep(Enum):
    """Enumeration of tutorial steps."""
    WELCOME = 0              # Welcome message
    BOARD_STRUCTURE = 1      # Explain 9 mini-boards
    WIN_CONDITION = 2        # Win 3 boards in a row
    FIRST_MOVE = 3           # Make first move (guided)
    OPPONENT_RESPONSE = 4    # Watch opponent play (auto)
    CONSTRAINT_INTRO = 5     # Explain the constraint rule
    CONSTRAINT_PRACTICE = 6  # Practice constraint (guided)
    SEE_CONSTRAINT = 7       # See effect of your move
    WIN_MINI_BOARD = 8       # Win a mini-board (guided)
    FREE_MOVE_SETUP = 9      # Explain free move scenario
    FREE_MOVE_RULE = 10      # Practice free move
    PRACTICE_MODE = 11       # Free practice
    COMPLETE = 12            # Tutorial complete


# Initialize pygame
pygame.init()
pygame.mixer.init()

# Theme Management
IS_DARK_MODE = False

# Static Colors (Constant)
MENU_BACKGROUND = (44, 62, 80)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
GREEN = (46, 204, 113)
ORANGE = (230, 126, 34)
PURPLE = (155, 89, 182)
YELLOW = (241, 196, 15)
GOLD = (241, 196, 15)
BUTTON_DEFAULT = (52, 152, 219)
BUTTON_HOVER = (41, 128, 185)
TEXT_LIGHT = (255, 255, 255)

# Dynamic Colors (will be updated by set_theme)
BACKGROUND = (245, 247, 250)
WHITE = (255, 255, 255)
BLACK = (44, 62, 80)
GRAY = (149, 165, 166)
LIGHT_GRAY = (236, 240, 241)
PLAYER_X_COLOR = (26, 188, 156)
PLAYER_O_COLOR = (255, 107, 107)
WIN_X_COLOR = (22, 160, 133)
WIN_O_COLOR = (238, 82, 83)
HIGHLIGHT_X = (26, 188, 156, 30)
HIGHLIGHT_O = (255, 107, 107, 30)
TEXT_DARK = (44, 62, 80)
CONFETTI_COLORS = []

def set_theme(dark_mode: bool):
    global IS_DARK_MODE, BACKGROUND, WHITE, BLACK, GRAY, LIGHT_GRAY
    global PLAYER_X_COLOR, PLAYER_O_COLOR, WIN_X_COLOR, WIN_O_COLOR
    global HIGHLIGHT_X, HIGHLIGHT_O, TEXT_DARK, CONFETTI_COLORS

    IS_DARK_MODE = dark_mode

    if dark_mode:
        BACKGROUND = (20, 20, 20)
        WHITE = (40, 40, 40)          # Dark grey for sub-board bg
        BLACK = (200, 200, 200)       # Light grey for grid lines
        GRAY = (100, 100, 100)
        LIGHT_GRAY = (60, 60, 60)
        PLAYER_X_COLOR = (0, 255, 255)    # Neon Cyan
        PLAYER_O_COLOR = (255, 0, 255)    # Neon Magenta
        WIN_X_COLOR = (0, 200, 200)
        WIN_O_COLOR = (200, 0, 200)
        HIGHLIGHT_X = (0, 255, 255, 40)
        HIGHLIGHT_O = (255, 0, 255, 40)
        TEXT_DARK = (220, 220, 220)   # Light text for dark mode
    else:
        BACKGROUND = (245, 247, 250)
        WHITE = (255, 255, 255)
        BLACK = (44, 62, 80)
        GRAY = (149, 165, 166)
        LIGHT_GRAY = (236, 240, 241)
        PLAYER_X_COLOR = (26, 188, 156)
        PLAYER_O_COLOR = (255, 107, 107)
        WIN_X_COLOR = (22, 160, 133)
        WIN_O_COLOR = (238, 82, 83)
        HIGHLIGHT_X = (26, 188, 156, 30)
        HIGHLIGHT_O = (255, 107, 107, 30)
        TEXT_DARK = (44, 62, 80)

    # Re-populate confetti colors with new theme
    CONFETTI_COLORS[:] = [
        PLAYER_X_COLOR,
        PLAYER_O_COLOR,
        GOLD,
        PURPLE,
        BLUE,
        GREEN,
    ]

# Initialize default theme
set_theme(False)

# Game settings (default sizes, will be recalculated on resize)
DEFAULT_WINDOW_SIZE = 630
DEFAULT_BOARD_SIZE = 600
DEFAULT_MARGIN = 15
DEFAULT_STATUS_HEIGHT = 100
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
        self.screen.fill(MENU_BACKGROUND)

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
            subtitle_surf = FONT_SUBTITLE.render(self.subtitle_text, True, TEXT_LIGHT)
            subtitle_surf.set_alpha(alpha)
            subtitle_rect = subtitle_surf.get_rect(center=(center_x, center_y + 35))
            self.screen.blit(subtitle_surf, subtitle_rect)

        # Draw "Click to continue" hint
        if self.stamp_phase >= 4:
            hint_alpha = int(128 + 127 * math.sin(pygame.time.get_ticks() / 300))
            hint_surf = FONT_SMALL.render("Click to continue", True, TEXT_LIGHT)
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
        self.enabled = True

    def set_enabled(self, enabled: bool):
        """Enable or disable the button."""
        self.enabled = enabled
        if not enabled:
            self.is_hovered = False

    def update_position(self, x: int, y: int):
        """Update button position."""
        self.rect.x = x
        self.rect.y = y

    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events. Returns True if button was clicked."""
        if not self.enabled:
            if event.type == pygame.MOUSEMOTION:
                self.is_hovered = False
            return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        """Draw the button."""
        if not self.enabled:
            color = tuple(max(0, int(c * 0.5)) for c in self.color)
            text_color = LIGHT_GRAY
            shadow_offset = 0
        else:
            color = self.hover_color if self.is_hovered else self.color
            text_color = TEXT_LIGHT
            shadow_offset = 2 if not self.is_hovered else 1

        # Draw shadow
        if self.enabled:
            shadow_rect = self.rect.copy()
            shadow_rect.y += shadow_offset
            pygame.draw.rect(screen, (0, 0, 0, 50), shadow_rect, border_radius=12)

        # Draw button background with rounded corners
        button_rect = self.rect.copy()
        if self.enabled and self.is_hovered:
            button_rect.y += 1 # Press effect
        
        pygame.draw.rect(screen, color, button_rect, border_radius=12)

        # Draw text
        text_surf = FONT_BUTTON.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=button_rect.center)
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
        spacing = 25

        center_x = width // 2
        # Adjust layout for 3 buttons
        total_height = 3 * button_height + 2 * spacing
        start_y = (height - total_height) // 2

        self.one_player_btn = MenuButton(
            center_x - button_width // 2,
            start_y,
            button_width, button_height,
            "1 Player",
            color=BLUE
        )

        self.two_player_btn = MenuButton(
            center_x - button_width // 2,
            start_y + button_height + spacing,
            button_width, button_height,
            "2 Players",
            color=RED
        )

        self.how_to_play_btn = MenuButton(
            center_x - button_width // 2,
            start_y + 2 * (button_height + spacing),
            button_width, button_height,
            "How to Play",
            color=GREEN
        )

    def run(self):
        """Run the mode selection screen. Returns selected game mode or 'TUTORIAL'."""
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
                    self.how_to_play_btn.handle_event(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.one_player_btn.handle_event(event):
                        self.sound_manager.play('click')
                        self.selected_mode = GameMode.ONE_PLAYER
                    elif self.two_player_btn.handle_event(event):
                        self.sound_manager.play('click')
                        self.selected_mode = GameMode.TWO_PLAYER
                    elif self.how_to_play_btn.handle_event(event):
                        self.sound_manager.play('click')
                        return "TUTORIAL"

            self._draw()
            self.clock.tick(60)

        return self.selected_mode

    def _draw(self):
        """Draw the mode selection screen."""
        width, height = self.screen.get_size()
        self.screen.fill(MENU_BACKGROUND)

        # Draw title
        title_surf = FONT_MENU_TITLE.render("Select Game Mode", True, GOLD)
        title_rect = title_surf.get_rect(center=(width // 2, height // 4))
        self.screen.blit(title_surf, title_rect)

        # Draw buttons
        self.one_player_btn.draw(self.screen)
        self.two_player_btn.draw(self.screen)
        self.how_to_play_btn.draw(self.screen)

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
            color=ORANGE
        )

        self.bigbrain_btn = MenuButton(
            center_x - button_width // 2,
            start_y + 2 * (button_height + spacing),
            button_width, button_height,
            "Big Brain",
            color=PURPLE
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
        self.screen.fill(MENU_BACKGROUND)

        # Draw title
        title_surf = FONT_MENU_TITLE.render("Select Difficulty", True, GOLD)
        title_rect = title_surf.get_rect(center=(width // 2, height // 4))
        self.screen.blit(title_surf, title_rect)

        # Draw subtitle
        subtitle_surf = FONT_SUBTITLE.render("You are X, AI is O", True, TEXT_LIGHT)
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, height // 4 + 40))
        self.screen.blit(subtitle_surf, subtitle_rect)

        # Draw buttons
        self.easy_btn.draw(self.screen)
        self.medium_btn.draw(self.screen)
        self.bigbrain_btn.draw(self.screen)

        pygame.display.flip()


class TutorialArrow:
    """Animated arrow for tutorial guidance."""

    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                 color: Tuple[int, int, int] = None):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.color = color or GOLD

    def draw(self, screen: pygame.Surface):
        """Draw an animated arrow from start to end position."""
        # Much slower pulsing animation (sin wave over 1 second)
        pulse = 0.8 + 0.2 * math.sin(pygame.time.get_ticks() / 500)
        
        # Calculate arrow direction
        dx = self.end_pos[0] - self.start_pos[0]
        dy = self.end_pos[1] - self.start_pos[1]
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:
            return

        # Normalize direction
        dx, dy = dx / length, dy / length

        # Animate the arrow growing/drawing over 1.5 seconds
        animation_progress = min(1.0, (pygame.time.get_ticks() % 3000) / 1500)
        if animation_progress < 0.1: return # Brief pause at start
        
        current_length = length * animation_progress
        
        # Arrow shaft end (leave room for arrowhead)
        head_size = 12
        shaft_end_x = self.start_pos[0] + dx * (current_length - head_size)
        shaft_end_y = self.start_pos[1] + dy * (current_length - head_size)
        
        # Final tip position for this frame
        current_tip_x = self.start_pos[0] + dx * current_length
        current_tip_y = self.start_pos[1] + dy * current_length

        # Draw shaft with pulsing thickness
        line_width = max(3, int(5 * pulse))
        pygame.draw.line(screen, self.color,
                        self.start_pos, (shaft_end_x, shaft_end_y), line_width)

        # Draw arrowhead
        # Perpendicular vector
        px, py = -dy, dx
        head_width = 8 * pulse

        # Three points of arrowhead
        tip = (current_tip_x, current_tip_y)
        left = (shaft_end_x + px * head_width, shaft_end_y + py * head_width)
        right = (shaft_end_x - px * head_width, shaft_end_y - py * head_width)

        pygame.draw.polygon(screen, self.color, [tip, left, right])


class TutorialBubble:
    """Speech bubble for tutorial instructions."""

    def __init__(self, text: str, anchor_pos: Tuple[int, int],
                 direction: str = 'above', width: int = 200):
        self.text = text
        self.anchor_pos = anchor_pos
        self.direction = direction  # 'above', 'below', 'left', 'right'
        self.width = width
        self.padding = 10
        self.tail_size = 10

    def draw(self, screen: pygame.Surface):
        """Draw the speech bubble with text."""
        # Render text to get dimensions
        words = self.text.split()
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surf = FONT_SMALL.render(test_line, True, BLACK)
            if test_surf.get_width() <= self.width - 2 * self.padding:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        # Calculate bubble dimensions
        line_height = FONT_SMALL.get_height()
        bubble_height = len(lines) * line_height + 2 * self.padding
        bubble_width = self.width

        # Position bubble based on direction
        if self.direction == 'above':
            bubble_x = self.anchor_pos[0] - bubble_width // 2
            bubble_y = self.anchor_pos[1] - bubble_height - self.tail_size
        elif self.direction == 'below':
            bubble_x = self.anchor_pos[0] - bubble_width // 2
            bubble_y = self.anchor_pos[1] + self.tail_size
        elif self.direction == 'left':
            bubble_x = self.anchor_pos[0] - bubble_width - self.tail_size
            bubble_y = self.anchor_pos[1] - bubble_height // 2
        else:  # right
            bubble_x = self.anchor_pos[0] + self.tail_size
            bubble_y = self.anchor_pos[1] - bubble_height // 2

        # Clamp to screen bounds
        screen_w, screen_h = screen.get_size()
        bubble_x = max(5, min(bubble_x, screen_w - bubble_width - 5))
        bubble_y = max(5, min(bubble_y, screen_h - bubble_height - 5))

        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)

        # Draw bubble background
        pygame.draw.rect(screen, WHITE, bubble_rect, border_radius=8)
        pygame.draw.rect(screen, GOLD, bubble_rect, width=2, border_radius=8)

        # Draw tail pointing to anchor
        if self.direction == 'above':
            tail_points = [
                (self.anchor_pos[0], self.anchor_pos[1]),
                (self.anchor_pos[0] - 8, bubble_y + bubble_height),
                (self.anchor_pos[0] + 8, bubble_y + bubble_height)
            ]
        elif self.direction == 'below':
            tail_points = [
                (self.anchor_pos[0], self.anchor_pos[1]),
                (self.anchor_pos[0] - 8, bubble_y),
                (self.anchor_pos[0] + 8, bubble_y)
            ]
        elif self.direction == 'left':
            tail_points = [
                (self.anchor_pos[0], self.anchor_pos[1]),
                (bubble_x + bubble_width, self.anchor_pos[1] - 8),
                (bubble_x + bubble_width, self.anchor_pos[1] + 8)
            ]
        else:  # right
            tail_points = [
                (self.anchor_pos[0], self.anchor_pos[1]),
                (bubble_x, self.anchor_pos[1] - 8),
                (bubble_x, self.anchor_pos[1] + 8)
            ]

        pygame.draw.polygon(screen, WHITE, tail_points)
        pygame.draw.lines(screen, GOLD, False, tail_points[:2], 2)
        pygame.draw.lines(screen, GOLD, False, [tail_points[0], tail_points[2]], 2)

        # Draw text
        text_y = bubble_y + self.padding
        for line in lines:
            text_surf = FONT_SMALL.render(line, True, BLACK)
            text_x = bubble_x + (bubble_width - text_surf.get_width()) // 2
            screen.blit(text_surf, (text_x, text_y))
            text_y += line_height


class TutorialScreen:
    """Interactive tutorial screen for learning Ultimate Tic Tac Toe."""

    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager):
        self.screen = screen
        self.sound_manager = sound_manager
        self.clock = pygame.time.Clock()
        self.done = False

        # Tutorial state
        self.current_step = TutorialStep.WELCOME
        self.step_substep = 0  # For multi-part steps

        # Animation and timing
        self.animation_timer = 0  # For timed events
        self.auto_advance_delay = 2500  # ms to wait before auto-advancing (increased from 1500)
        self.board_highlight_index = 0  # For BOARD_STRUCTURE animation
        self.last_move_cell: Optional[Tuple[int, int, int, int]] = None  # For constraint arrows
        self.show_constraint_arrow = False

        # Demo game board
        self.demo_game: Optional['UltimateTicTacToe'] = None
        self._setup_demo_board()

        # UI elements
        self._create_buttons()

        # Highlight state
        self.highlight_cells: List[Tuple[int, int, int, int]] = []

        # Visual guides
        self.arrows: List[TutorialArrow] = []
        self.bubbles: List[TutorialBubble] = []

        # Board rendering dimensions (calculated in _draw)
        self.demo_board_rect: Optional[pygame.Rect] = None
        self.demo_cell_size = 0
        self.demo_sub_board_size = 0

        # Confetti for completion
        self.confetti = ConfettiSystem()

    def _setup_demo_board(self):
        """Set up the demo board for the current tutorial step."""
        self.demo_game = UltimateTicTacToe()
        self.last_move_cell = None
        self.show_constraint_arrow = False
        self.animation_timer = 0

        if self.current_step == TutorialStep.BOARD_STRUCTURE:
            self.board_highlight_index = 0

        if self.current_step == TutorialStep.WIN_CONDITION:
            for col in range(3):
                self.demo_game.sub_boards[0][col].winner = 'X'
            self.demo_game.game_over = True

        elif self.current_step == TutorialStep.OPPONENT_RESPONSE:
            # Player moved in center board, top-right cell -> opponent must play top-right board
            self.demo_game.sub_boards[1][1].cells[0][2] = 'X'
            self.demo_game.sub_boards[0][2].cells[1][1] = 'O'
            self.demo_game.current_player = 'O'
            self.demo_game.active_board = (0, 2)
            self.last_move_cell = (1, 1, 0, 2)
            self.show_constraint_arrow = True

        elif self.current_step == TutorialStep.CONSTRAINT_INTRO:
            # Opponent's move now forces the next active board
            self.demo_game.sub_boards[1][1].cells[0][2] = 'X'
            self.demo_game.sub_boards[0][2].cells[1][1] = 'O'
            self.demo_game.current_player = 'X'
            self.demo_game.active_board = (1, 1)
            self.last_move_cell = (0, 2, 1, 1)
            self.show_constraint_arrow = True

        if self.current_step == TutorialStep.CONSTRAINT_PRACTICE:
            # After first move - X is in center of center board
            # O played in response, now X's turn in the board O was sent to
            self.demo_game.sub_boards[1][1].cells[1][1] = 'X'  # X's first move
            self.demo_game.sub_boards[1][1].cells[0][0] = 'O'  # O's response (sent to top-left board)
            self.demo_game.current_player = 'X'
            self.demo_game.active_board = (0, 0)  # X must play in top-left board
            self.last_move_cell = (1, 1, 0, 0)  # O's last move for arrow

        elif self.current_step == TutorialStep.SEE_CONSTRAINT:
            # After constraint practice - show result
            self.demo_game.sub_boards[1][1].cells[1][1] = 'X'
            self.demo_game.sub_boards[1][1].cells[0][0] = 'O'
            self.demo_game.sub_boards[0][0].cells[1][1] = 'X'  # User's practice move
            self.demo_game.current_player = 'O'
            self.demo_game.active_board = (1, 1)  # O sent back to center
            self.last_move_cell = (0, 0, 1, 1)  # X's last move for arrow
            self.show_constraint_arrow = True

        elif self.current_step == TutorialStep.WIN_MINI_BOARD:
            # Set up a board 1 move away from winning
            # X has two in a row in top-left board, needs one more
            self.demo_game.sub_boards[0][0].cells[0][0] = 'X'
            self.demo_game.sub_boards[0][0].cells[0][1] = 'X'
            # Add some other moves for realism
            self.demo_game.sub_boards[0][1].cells[0][0] = 'O'
            self.demo_game.sub_boards[0][2].cells[0][0] = 'O'
            self.demo_game.current_player = 'X'
            self.demo_game.active_board = (0, 0)  # Must play here to win

        elif self.current_step in (TutorialStep.FREE_MOVE_SETUP, TutorialStep.FREE_MOVE_RULE):
            # Pre-fill to demonstrate the free move rule
            # Win sub-board (1,1) for X
            self.demo_game.sub_boards[1][1].cells[0][0] = 'X'
            self.demo_game.sub_boards[1][1].cells[1][1] = 'X'
            self.demo_game.sub_boards[1][1].cells[2][2] = 'X'
            self.demo_game.sub_boards[1][1].winner = 'X'
            # Place moves that lead to being sent to the won board
            self.demo_game.sub_boards[0][0].cells[1][1] = 'O'
            self.demo_game.sub_boards[0][1].cells[0][0] = 'X'
            self.demo_game.sub_boards[0][0].cells[0][0] = 'O'
            self.demo_game.current_player = 'X'
            self.demo_game.active_board = None  # Free move (would have been sent to won board)

        elif self.current_step == TutorialStep.PRACTICE_MODE:
            # Fresh board for free practice
            self.demo_game = UltimateTicTacToe()

        self._update_highlights()

    def _update_highlights(self):
        """Update highlighted cells based on current step/substep."""
        self.highlight_cells = []
        self.arrows = []
        self.bubbles = []

        if self.current_step == TutorialStep.FIRST_MOVE:
            # Highlight a move that sends the opponent to a different board
            if self.step_substep == 0:
                self.highlight_cells = [(1, 1, 0, 2)]

        elif self.current_step == TutorialStep.CONSTRAINT_PRACTICE:
            # Highlight center cell of top-left board (where O's move sent us)
            if self.step_substep == 0:
                self.highlight_cells = [(0, 0, 1, 1)]

        elif self.current_step == TutorialStep.WIN_MINI_BOARD:
            # Highlight the winning cell (top-left board, top-right cell)
            if self.step_substep == 0:
                self.highlight_cells = [(0, 0, 0, 2)]

    def _create_buttons(self):
        """Create navigation buttons."""
        width, height = self.screen.get_size()
        button_width = 100
        button_height = 40
        margin = 20

        # Back button (bottom left)
        self.back_btn = MenuButton(
            margin,
            height - button_height - margin,
            button_width, button_height,
            "Back",
            color=GRAY
        )

        # Next button (bottom right)
        self.next_btn = MenuButton(
            width - button_width - margin,
            height - button_height - margin,
            button_width, button_height,
            "Next",
            color=GREEN
        )

        # Skip button (top right, smaller)
        skip_width = 60
        skip_height = 28
        self.skip_btn = MenuButton(
            width - skip_width - 10,
            10,
            skip_width, skip_height,
            "Skip",
            color=GRAY
        )

    def _is_interactive_step(self) -> bool:
        """Return True if the demo board should accept clicks."""
        return self.current_step in (
            TutorialStep.FIRST_MOVE,
            TutorialStep.CONSTRAINT_PRACTICE,
            TutorialStep.WIN_MINI_BOARD,
            TutorialStep.FREE_MOVE_RULE,
            TutorialStep.PRACTICE_MODE,
        )

    def _step_requires_action(self) -> bool:
        """Return True if Next should be disabled until the user acts."""
        return self.current_step in (
            TutorialStep.FIRST_MOVE,
            TutorialStep.CONSTRAINT_PRACTICE,
            TutorialStep.WIN_MINI_BOARD,
            TutorialStep.FREE_MOVE_RULE,
        )

    def _update_button_states(self):
        """Enable or disable buttons based on tutorial progress."""
        allow_next = not self._step_requires_action() or self.step_substep > 0
        self.next_btn.set_enabled(allow_next)

    def _get_demo_cell_center(self, br: int, bc: int, cr: int, cc: int,
                              offset_x: int, offset_y: int,
                              cell_size: int, sub_board_size: int) -> Tuple[int, int]:
        """Return the screen center for a demo cell."""
        x = offset_x + bc * sub_board_size + cc * cell_size + cell_size // 2
        y = offset_y + br * sub_board_size + cr * cell_size + cell_size // 2
        return x, y

    def _get_demo_board_center(self, br: int, bc: int,
                               offset_x: int, offset_y: int,
                               sub_board_size: int) -> Tuple[int, int]:
        """Return the screen center for a demo sub-board."""
        x = offset_x + bc * sub_board_size + sub_board_size // 2
        y = offset_y + br * sub_board_size + sub_board_size // 2
        return x, y

    def _draw_guides(self, offset_x: int, offset_y: int,
                     cell_size: int, sub_board_size: int):
        """Draw arrows and bubbles to guide the player."""
        if self.show_constraint_arrow and self.last_move_cell and self.demo_game:
            active_board = self.demo_game.active_board
            if active_board is not None:
                start = self._get_demo_cell_center(
                    self.last_move_cell[0],
                    self.last_move_cell[1],
                    self.last_move_cell[2],
                    self.last_move_cell[3],
                    offset_x,
                    offset_y,
                    cell_size,
                    sub_board_size,
                )
                end = self._get_demo_board_center(
                    active_board[0],
                    active_board[1],
                    offset_x,
                    offset_y,
                    sub_board_size,
                )
                TutorialArrow(start, end).draw(self.screen)

        if self.current_step in (
            TutorialStep.FIRST_MOVE,
            TutorialStep.CONSTRAINT_PRACTICE,
            TutorialStep.WIN_MINI_BOARD,
        ) and self.highlight_cells:
            br, bc, cr, cc = self.highlight_cells[0]
            anchor = self._get_demo_cell_center(
                br, bc, cr, cc, offset_x, offset_y, cell_size, sub_board_size
            )
            TutorialBubble("Click the highlighted cell.", anchor, direction='above', width=230).draw(self.screen)

        elif self.current_step == TutorialStep.FREE_MOVE_RULE:
            anchor = self._get_demo_board_center(1, 1, offset_x, offset_y, sub_board_size)
            TutorialBubble("Any board is valid. Make a move anywhere.",
                           anchor, direction='above', width=260).draw(self.screen)

    def run(self) -> str:
        """Run the tutorial. Returns 'MENU' to go back."""
        while not self.done:
            dt = self.clock.tick(60)

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
                    self.back_btn.handle_event(event)
                    self.next_btn.handle_event(event)
                    self.skip_btn.handle_event(event)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        result = self._handle_click(event)
                        if result:
                            return result

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'MENU'

            # Handle auto-advance for OPPONENT_RESPONSE step
            if self.current_step == TutorialStep.OPPONENT_RESPONSE:
                self.animation_timer += dt
                if self.animation_timer >= self.auto_advance_delay:
                    self._next_step()

            # Update BOARD_STRUCTURE animation
            if self.current_step == TutorialStep.BOARD_STRUCTURE:
                self.animation_timer += dt
                if self.animation_timer >= 800:  # Cycle boards every 800ms (increased from 400ms)
                    self.animation_timer = 0
                    self.board_highlight_index = (self.board_highlight_index + 1) % 9

            # Update confetti
            self.confetti.update()

            self._draw()

        return 'MENU'

    def _handle_click(self, event) -> Optional[str]:
        """Handle mouse click. Returns navigation result or None."""
        self.sound_manager.play('click')

        if self.skip_btn.handle_event(event):
            return 'MENU'

        if self.back_btn.handle_event(event):
            if self.current_step == TutorialStep.WELCOME:
                return 'MENU'
            else:
                self._previous_step()

        elif self.next_btn.handle_event(event):
            if self.current_step == TutorialStep.COMPLETE:
                return 'MENU'
            else:
                self._next_step()

        else:
            # Check for demo board interaction
            self._handle_demo_click(event.pos)

        return None

    def _next_step(self):
        """Advance to next tutorial step."""
        steps = list(TutorialStep)
        current_idx = steps.index(self.current_step)
        if current_idx < len(steps) - 1:
            self.current_step = steps[current_idx + 1]
            self.step_substep = 0
            self._setup_demo_board()

    def _previous_step(self):
        """Go to previous tutorial step."""
        steps = list(TutorialStep)
        current_idx = steps.index(self.current_step)
        if current_idx > 0:
            self.current_step = steps[current_idx - 1]
            self.step_substep = 0
            self._setup_demo_board()

    def _handle_demo_click(self, pos):
        """Handle click on demo board."""
        if not self._is_interactive_step():
            return
        if self._step_requires_action() and self.step_substep > 0:
            return

        coords = self._get_demo_board_coords(pos)
        if coords is None:
            return

        br, bc, cr, cc = coords

        # Check if valid move in demo
        if self.demo_game and self.demo_game.is_valid_board(br, bc):
            sub_board = self.demo_game.sub_boards[br][bc]
            if sub_board.cells[cr][cc] is None:
                # In guided steps, only allow highlighted moves
                if self.current_step in (
                    TutorialStep.FIRST_MOVE,
                    TutorialStep.CONSTRAINT_PRACTICE,
                    TutorialStep.WIN_MINI_BOARD,
                ):
                    if (br, bc, cr, cc) not in self.highlight_cells and self.highlight_cells:
                        return

                self.demo_game.make_move(br, bc, cr, cc)
                self.step_substep += 1
                self._update_highlights()

    def _get_demo_board_coords(self, pos) -> Optional[Tuple[int, int, int, int]]:
        """Convert screen position to demo board coordinates."""
        if self.demo_board_rect is None:
            return None

        x, y = pos
        if not self.demo_board_rect.collidepoint(pos):
            return None

        # Convert to local coordinates
        local_x = x - self.demo_board_rect.x
        local_y = y - self.demo_board_rect.y

        # Calculate board and cell positions
        if self.demo_sub_board_size == 0:
            return None

        board_col = local_x // self.demo_sub_board_size
        board_row = local_y // self.demo_sub_board_size

        cell_x = local_x % self.demo_sub_board_size
        cell_y = local_y % self.demo_sub_board_size

        if self.demo_cell_size == 0:
            return None

        cell_col = cell_x // self.demo_cell_size
        cell_row = cell_y // self.demo_cell_size

        # Validate bounds
        if 0 <= board_row < 3 and 0 <= board_col < 3 and 0 <= cell_row < 3 and 0 <= cell_col < 3:
            return board_row, board_col, cell_row, cell_col
        return None

    def _get_step_instructions(self) -> List[str]:
        """Get instruction text for current tutorial step."""
        instructions = {
            TutorialStep.WELCOME: [
                "Welcome to Ultimate Tic Tac Toe!",
                "",
                "This tutorial teaches the basic rules.",
                "Use Next/Back to navigate, or Skip anytime.",
            ],
            TutorialStep.BOARD_STRUCTURE: [
                "Board Structure",
                "",
                "The main board is a 3x3 grid of mini boards.",
                "Each mini board is its own Tic Tac Toe game.",
            ],
            TutorialStep.WIN_CONDITION: [
                "Win Condition",
                "",
                "Win a mini board by getting 3 in a row.",
                "Win the game by winning 3 mini boards in a row.",
            ],
            TutorialStep.FIRST_MOVE: [
                "Your First Move",
                "",
                "Click the highlighted cell to place your X.",
                "Your move decides which board your opponent must play in.",
            ],
            TutorialStep.OPPONENT_RESPONSE: [
                "Opponent Response",
                "",
                "Your opponent must play in the highlighted board.",
                "That board matches the cell you chose.",
            ],
            TutorialStep.CONSTRAINT_INTRO: [
                "The Active Board Rule",
                "",
                "Each move sends the next player to a board.",
                "The arrow shows which board is now active.",
            ],
            TutorialStep.CONSTRAINT_PRACTICE: [
                "Try the Rule",
                "",
                "Play in the highlighted board.",
                "Click the highlighted cell to continue.",
            ],
            TutorialStep.SEE_CONSTRAINT: [
                "See the Result",
                "",
                "Your move sent the opponent to a new board.",
                "That board becomes the only valid choice.",
            ],
            TutorialStep.WIN_MINI_BOARD: [
                "Win a Mini Board",
                "",
                "Get 3 in a row inside one mini board.",
                "Click the highlighted cell to win it.",
            ],
            TutorialStep.FREE_MOVE_SETUP: [
                "Free Move Setup",
                "",
                "Sometimes the required board is already won or full.",
                "In that case you may play anywhere.",
            ],
            TutorialStep.FREE_MOVE_RULE: [
                "Free Move Rule",
                "",
                "Any board is valid now.",
                "Make a move anywhere to continue.",
            ],
            TutorialStep.PRACTICE_MODE: [
                "Practice Mode",
                "",
                "Play a few turns to get comfortable.",
                "Click Next when you're ready to start a real game.",
            ],
            TutorialStep.COMPLETE: [
                "You're Ready!",
                "",
                "You now know the basic rules.",
                "Click Next to return to the menu and start playing!",
            ],
        }
        return instructions.get(self.current_step, [])

    def _draw(self):
        """Draw the tutorial screen."""
        self._update_button_states()
        width, height = self.screen.get_size()
        self.screen.fill(MENU_BACKGROUND)

        # Draw title
        title_surf = FONT_MENU_TITLE.render("How to Play", True, GOLD)
        title_rect = title_surf.get_rect(center=(width // 2, 35))
        self.screen.blit(title_surf, title_rect)

        # Draw instructions
        instructions = self._get_step_instructions()
        y_offset = 70
        for i, line in enumerate(instructions):
            if i == 0:
                surf = FONT_SUBTITLE.render(line, True, GOLD)
            else:
                surf = FONT_SMALL.render(line, True, TEXT_LIGHT)
            rect = surf.get_rect(center=(width // 2, y_offset + i * 25))
            self.screen.blit(surf, rect)

        # Draw demo board (only for steps that need it)
        if self.current_step not in (TutorialStep.WELCOME, TutorialStep.COMPLETE):
            self._draw_demo_board(width, height)

        # Draw navigation buttons
        self._draw_buttons()

        # Draw step indicator
        self._draw_step_indicator(width, height)

        pygame.display.flip()

    def _draw_demo_board(self, width: int, height: int):
        """Draw the scaled demo board."""
        if self.demo_game is None:
            return

        # Calculate board dimensions
        board_center_y = height // 2 + 40
        scale = 0.55
        base_size = min(width - 40, height - 200)
        scaled_board_size = int(base_size * scale)

        cell_size = scaled_board_size // 9
        sub_board_size = cell_size * 3
        board_size = cell_size * 9

        board_offset_x = (width - board_size) // 2
        board_offset_y = board_center_y - board_size // 2

        # Store for click detection
        self.demo_board_rect = pygame.Rect(board_offset_x, board_offset_y, board_size, board_size)
        self.demo_cell_size = cell_size
        self.demo_sub_board_size = sub_board_size

        # Draw board background
        pygame.draw.rect(self.screen, WHITE, self.demo_board_rect)

        # Draw sub-boards
        for br in range(3):
            for bc in range(3):
                self._draw_demo_sub_board(br, bc, board_offset_x, board_offset_y,
                                          cell_size, sub_board_size)

        # Draw main grid lines
        line_width = max(2, cell_size // 12)
        for i in range(4):
            x = board_offset_x + i * sub_board_size
            pygame.draw.line(self.screen, BLACK,
                           (x, board_offset_y), (x, board_offset_y + board_size), line_width)
            y = board_offset_y + i * sub_board_size
            pygame.draw.line(self.screen, BLACK,
                           (board_offset_x, y), (board_offset_x + board_size, y), line_width)

        # Draw highlights for guided moves
        self._draw_highlights(board_offset_x, board_offset_y, cell_size, sub_board_size)

        # Draw arrows and bubbles
        self._draw_guides(board_offset_x, board_offset_y, cell_size, sub_board_size)

    def _draw_demo_sub_board(self, br: int, bc: int, offset_x: int, offset_y: int,
                              cell_size: int, sub_board_size: int):
        """Draw a single sub-board in the demo."""
        if self.demo_game is None:
            return

        sub_board = self.demo_game.sub_boards[br][bc]
        base_x = offset_x + bc * sub_board_size
        base_y = offset_y + br * sub_board_size
        
        # Sub-board rect with padding
        board_rect = pygame.Rect(base_x + 4, base_y + 4, sub_board_size - 8, sub_board_size - 8)

        # Highlight active boards
        is_active = False
        if self.current_step not in (TutorialStep.BOARD_STRUCTURE, TutorialStep.WIN_CONDITION):
            if self.demo_game.is_valid_board(br, bc):
                is_active = True
                highlight_color = HIGHLIGHT_X if self.demo_game.current_player == 'X' else HIGHLIGHT_O
                
                # Draw background and highlight
                pygame.draw.rect(self.screen, WHITE, board_rect, border_radius=8)
                surf = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
                surf.fill(highlight_color)
                self.screen.blit(surf, board_rect)
                
                # Border
                border_color = PLAYER_X_COLOR if self.demo_game.current_player == 'X' else PLAYER_O_COLOR
                pygame.draw.rect(self.screen, border_color, board_rect, width=2, border_radius=8)
        
        if not is_active:
             # Inactive board background
            pygame.draw.rect(self.screen, LIGHT_GRAY, board_rect, border_radius=8)

        if self.current_step == TutorialStep.BOARD_STRUCTURE:
            highlight_index = self.board_highlight_index
            highlight_br = highlight_index // 3
            highlight_bc = highlight_index % 3
            if br == highlight_br and bc == highlight_bc:
                pulse = int(abs(math.sin(pygame.time.get_ticks() / 300)) * 2) + 3
                pygame.draw.rect(self.screen, GOLD,
                               board_rect,
                               width=pulse, border_radius=8)

        # Won board overlay
        if sub_board.winner:
            overlay_color = WIN_X_COLOR if sub_board.winner == 'X' else WIN_O_COLOR
            
            surf = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
            surf.fill((*overlay_color, 40))
            self.screen.blit(surf, board_rect)
            
            self._draw_large_symbol(sub_board.winner, base_x, base_y, sub_board_size)

        # Grid lines
        if not sub_board.winner:
            line_width = max(1, cell_size // 30)
            for i in range(1, 3):
                # Vertical
                start_x = base_x + i * cell_size
                pygame.draw.line(self.screen, GRAY,
                            (start_x, base_y + 5),
                            (start_x, base_y + sub_board_size - 5), line_width)
                # Horizontal
                start_y = base_y + i * cell_size
                pygame.draw.line(self.screen, GRAY,
                            (base_x + 5, start_y),
                            (base_x + sub_board_size - 5, start_y), line_width)

        # Draw X's and O's
        if not sub_board.winner:
            for cr in range(3):
                for cc in range(3):
                    player = sub_board.cells[cr][cc]
                    if player:
                        cell_x = base_x + cc * cell_size
                        cell_y = base_y + cr * cell_size
                        self._draw_symbol(player, cell_x, cell_y, cell_size)

    def _draw_highlights(self, offset_x: int, offset_y: int, cell_size: int, sub_board_size: int):
        """Draw highlighted cells for guided interaction."""
        # Pulse animation
        pulse = int(abs(math.sin(pygame.time.get_ticks() / 300)) * 100) + 100

        for (br, bc, cr, cc) in self.highlight_cells:
            cell_x = offset_x + bc * sub_board_size + cc * cell_size
            cell_y = offset_y + br * sub_board_size + cr * cell_size

            # Draw semi-transparent highlight
            surf = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            surf.fill((*GOLD, pulse))
            self.screen.blit(surf, (cell_x, cell_y))

            # Draw border
            pygame.draw.rect(self.screen, GOLD,
                           (cell_x, cell_y, cell_size, cell_size), 3)

    def _draw_symbol(self, player: str, x: int, y: int, size: int):
        """Draw X or O. Style depends on IS_DARK_MODE."""
        padding = int(size * 0.25)
        
        if not IS_DARK_MODE:
            # === FLAT STYLE ===
            line_width = max(4, size // 10)
            radius = line_width // 2
            
            color = PLAYER_X_COLOR if player == 'X' else PLAYER_O_COLOR
            shadow_color = (0, 0, 0, 20)

            if player == 'X':
                points = [
                    ((x + padding, y + padding), (x + size - padding, y + size - padding)),
                    ((x + size - padding, y + padding), (x + padding, y + size - padding))
                ]
                shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                for start, end in points:
                    s_start = (start[0] - x + 2, start[1] - y + 2)
                    s_end = (end[0] - x + 2, end[1] - y + 2)
                    pygame.draw.line(shadow_surf, shadow_color, s_start, s_end, line_width)
                    pygame.draw.circle(shadow_surf, shadow_color, s_start, radius)
                    pygame.draw.circle(shadow_surf, shadow_color, s_end, radius)
                self.screen.blit(shadow_surf, (x, y))

                for start, end in points:
                    pygame.draw.line(self.screen, color, start, end, line_width)
                    pygame.draw.circle(self.screen, color, start, radius)
                    pygame.draw.circle(self.screen, color, end, radius)
            else:
                center = (x + size // 2, y + size // 2)
                circle_radius = size // 2 - padding
                shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(shadow_surf, shadow_color, (size // 2 + 2, size // 2 + 2), circle_radius, line_width)
                self.screen.blit(shadow_surf, (x, y))
                pygame.draw.circle(self.screen, color, center, circle_radius, line_width)
        else:
            # === NEON STYLE ===
            base_width = max(3, size // 12)
            layers = [
                (8, 30),
                (5, 60),
                (3, 110),
                (1.5, 180)
            ]
            
            if player == 'X':
                start_pos1 = (x + padding, y + padding)
                end_pos1 = (x + size - padding, y + size - padding)
                start_pos2 = (x + size - padding, y + padding)
                end_pos2 = (x + padding, y + size - padding)
                
                glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                local_start1 = (padding, padding)
                local_end1 = (size - padding, size - padding)
                local_start2 = (size - padding, padding)
                local_end2 = (padding, size - padding)
                
                for width_mult, alpha in layers:
                    current_width = int(base_width * width_mult)
                    color = (*PLAYER_X_COLOR, alpha)
                    pygame.draw.line(glow_surf, color, local_start1, local_end1, current_width)
                    pygame.draw.line(glow_surf, color, local_start2, local_end2, current_width)
                    pygame.draw.circle(glow_surf, color, local_start1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_start2, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end2, current_width // 2)
                
                self.screen.blit(glow_surf, (x, y))
                
                core_color = (255, 255, 255)
                pygame.draw.line(self.screen, core_color, start_pos1, end_pos1, base_width // 2 + 1)
                pygame.draw.line(self.screen, core_color, start_pos2, end_pos2, base_width // 2 + 1)
                pygame.draw.circle(self.screen, core_color, start_pos1, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, end_pos1, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, start_pos2, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, end_pos2, (base_width // 2 + 1) // 2)
            else:
                center = (x + size // 2, y + size // 2)
                radius = size // 2 - padding
                local_center = (size // 2, size // 2)
                
                glow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                for width_mult, alpha in layers:
                    current_width = int(base_width * width_mult)
                    color = (*PLAYER_O_COLOR, alpha)
                    pygame.draw.circle(glow_surf, color, local_center, radius, current_width)
                
                self.screen.blit(glow_surf, (x, y))
                
                core_color = (255, 255, 255)
                pygame.draw.circle(self.screen, core_color, center, radius, base_width // 2 + 1)

    def _draw_large_symbol(self, player: str, x: int, y: int, sub_board_size: int):
        """Draw large X or O for won sub-board. Style depends on IS_DARK_MODE."""
        padding = sub_board_size // 6
        
        if not IS_DARK_MODE:
            # === FLAT STYLE ===
            line_width = max(8, sub_board_size // 12)
            radius = line_width // 2
            
            color = WIN_X_COLOR if player == 'X' else WIN_O_COLOR
            shadow_color = (0, 0, 0, 15)

            if player == 'X':
                points = [
                    ((x + padding, y + padding), (x + sub_board_size - padding, y + sub_board_size - padding)),
                    ((x + sub_board_size - padding, y + padding), (x + padding, y + sub_board_size - padding))
                ]
                shadow_surf = pygame.Surface((sub_board_size, sub_board_size), pygame.SRCALPHA)
                for start, end in points:
                    s_start = (start[0] - x + 3, start[1] - y + 3)
                    s_end = (end[0] - x + 3, end[1] - y + 3)
                    pygame.draw.line(shadow_surf, shadow_color, s_start, s_end, line_width)
                    pygame.draw.circle(shadow_surf, shadow_color, s_start, radius)
                    pygame.draw.circle(shadow_surf, shadow_color, s_end, radius)
                self.screen.blit(shadow_surf, (x, y))

                for start, end in points:
                    pygame.draw.line(self.screen, color, start, end, line_width)
                    pygame.draw.circle(self.screen, color, start, radius)
                    pygame.draw.circle(self.screen, color, end, radius)
            else:
                center = (x + sub_board_size // 2, y + sub_board_size // 2)
                circle_radius = sub_board_size // 2 - padding
                shadow_surf = pygame.Surface((sub_board_size, sub_board_size), pygame.SRCALPHA)
                pygame.draw.circle(shadow_surf, shadow_color, (sub_board_size // 2 + 3, sub_board_size // 2 + 3), circle_radius, line_width)
                self.screen.blit(shadow_surf, (x, y))
                pygame.draw.circle(self.screen, color, center, circle_radius, line_width)
        else:
            # === NEON STYLE ===
            base_width = max(6, sub_board_size // 15)
            layers = [
                (7, 30),
                (4, 70),
                (2.5, 120),
                (1.5, 180)
            ]
            
            if player == 'X':
                start_pos1 = (x + padding, y + padding)
                end_pos1 = (x + sub_board_size - padding, y + sub_board_size - padding)
                start_pos2 = (x + sub_board_size - padding, y + padding)
                end_pos2 = (x + padding, y + sub_board_size - padding)
                
                glow_surf = pygame.Surface((sub_board_size, sub_board_size), pygame.SRCALPHA)
                local_start1 = (padding, padding)
                local_end1 = (sub_board_size - padding, sub_board_size - padding)
                local_start2 = (sub_board_size - padding, padding)
                local_end2 = (padding, sub_board_size - padding)
                
                for width_mult, alpha in layers:
                    current_width = int(base_width * width_mult)
                    color = (*WIN_X_COLOR, alpha)
                    pygame.draw.line(glow_surf, color, local_start1, local_end1, current_width)
                    pygame.draw.line(glow_surf, color, local_start2, local_end2, current_width)
                    pygame.draw.circle(glow_surf, color, local_start1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_start2, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end2, current_width // 2)
                
                self.screen.blit(glow_surf, (x, y))
                
                core_color = (255, 255, 255)
                pygame.draw.line(self.screen, core_color, start_pos1, end_pos1, base_width // 2 + 1)
                pygame.draw.line(self.screen, core_color, start_pos2, end_pos2, base_width // 2 + 1)
                pygame.draw.circle(self.screen, core_color, start_pos1, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, end_pos1, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, start_pos2, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, end_pos2, (base_width // 2 + 1) // 2)
            else:
                center = (x + sub_board_size // 2, y + sub_board_size // 2)
                radius = sub_board_size // 2 - padding
                local_center = (sub_board_size // 2, sub_board_size // 2)
                
                glow_surf = pygame.Surface((sub_board_size, sub_board_size), pygame.SRCALPHA)
                for width_mult, alpha in layers:
                    current_width = int(base_width * width_mult)
                    color = (*WIN_O_COLOR, alpha)
                    pygame.draw.circle(glow_surf, color, local_center, radius, current_width)
                
                self.screen.blit(glow_surf, (x, y))
                
                core_color = (255, 255, 255)
                pygame.draw.circle(self.screen, core_color, center, radius, base_width // 2 + 1)
    def _draw_buttons(self):
        """Draw navigation buttons."""
        self.back_btn.draw(self.screen)
        self.next_btn.draw(self.screen)
        self.skip_btn.draw(self.screen)

    def _draw_step_indicator(self, width: int, height: int):
        """Draw step progress indicator (dots)."""
        steps = list(TutorialStep)
        num_steps = len(steps)
        dot_radius = 5
        dot_spacing = 20

        start_x = (width - (num_steps - 1) * dot_spacing) // 2
        y = height - 80

        for i, step in enumerate(steps):
            x = start_x + i * dot_spacing
            if step == self.current_step:
                pygame.draw.circle(self.screen, GOLD, (x, y), dot_radius)
            else:
                pygame.draw.circle(self.screen, TEXT_LIGHT, (x, y), dot_radius)


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
        self.tt = {}  # Transposition table for caching evaluations

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
        """Medium AI: Minimax with depth 2 (Optimized with Numpy)."""
        board, macro_board, active_board = self._to_numpy(game)
        
        self.tt = {} # Clear cache
        
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Fixed shallow depth for Medium
        max_depth = 2

        for br, bc, cr, cc in valid_moves:
            new_board = board.copy()
            new_macro = macro_board.copy()
            
            new_board[br*3+cr, bc*3+cc] = 1 # Self
            
            sb = new_board[br*3:(br+1)*3, bc*3:(bc+1)*3]
            if (np.abs(sb.sum(axis=0)) == 3).any() or \
               (np.abs(sb.sum(axis=1)) == 3).any() or \
               abs(sb.trace()) == 3 or \
               abs(np.fliplr(sb).trace()) == 3:
                new_macro[br, bc] = 1
            
            next_active = (cr, cc)
            target_sb = new_board[cr*3:(cr+1)*3, cc*3:(cc+1)*3]
            if new_macro[cr, cc] != 0 or np.all(target_sb != 0):
                next_active = None
            
            score = self._minimax_numpy(new_board, new_macro, next_active, max_depth - 1, alpha, beta, False)

            if score > best_score:
                best_score = score
                best_move = (br, bc, cr, cc)

            alpha = max(alpha, score)
            if beta <= alpha:
                break

        return best_move if best_move else random.choice(valid_moves)

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

    def _to_numpy(self, game: UltimateTicTacToe) -> Tuple[np.ndarray, np.ndarray, Optional[Tuple[int, int]]]:
        """Convert game state to numpy arrays for fast processing."""
        board = np.zeros((9, 9), dtype=np.int8)
        macro_board = np.zeros((3, 3), dtype=np.int8)
        
        # 1 = self, -1 = opponent
        p_val = 1
        o_val = -1
        # If player_symbol is 'O', then 'O' -> 1, 'X' -> -1
        if self.player_symbol == 'O':
            x_val = -1
            o_val = 1
        else:
            x_val = 1
            o_val = -1
            
        map_player = {'X': x_val, 'O': o_val, None: 0}
        
        for r in range(9):
            br, cr = divmod(r, 3)
            for c in range(9):
                bc, cc = divmod(c, 3)
                val = game.sub_boards[br][bc].cells[cr][cc]
                if val:
                    board[r, c] = map_player[val]
        
        for br in range(3):
            for bc in range(3):
                winner = game.sub_boards[br][bc].winner
                if winner:
                    macro_board[br, bc] = map_player[winner]
                    
        return board, macro_board, game.active_board

    def _bigbrain_move(self, game: UltimateTicTacToe,
                       valid_moves: List[Tuple[int, int, int, int]]) -> Tuple[int, int, int, int]:
        """Big Brain AI: Minimax with alpha-beta pruning (Optimized with Numpy)."""
        board, macro_board, active_board = self._to_numpy(game)
        
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        n_moves = len(valid_moves)
        max_depth = 4 if n_moves > 30 else 5 if n_moves > 10 else 6

        def move_score(m):
            br, bc, cr, cc = m
            score = 0
            if cr == 1 and cc == 1: score += 2
            elif (cr, cc) in [(0,0), (0,2), (2,0), (2,2)]: score += 1
            return score
            
        valid_moves.sort(key=move_score, reverse=True)

        for br, bc, cr, cc in valid_moves:
            new_board = board.copy()
            new_macro = macro_board.copy()
            
            new_board[br*3+cr, bc*3+cc] = 1 # Self
            
            sb = new_board[br*3:(br+1)*3, bc*3:(bc+1)*3]
            if (np.abs(sb.sum(axis=0)) == 3).any() or \
               (np.abs(sb.sum(axis=1)) == 3).any() or \
               abs(sb.trace()) == 3 or \
               abs(np.fliplr(sb).trace()) == 3:
                new_macro[br, bc] = 1
            
            next_active = (cr, cc)
            target_sb = new_board[cr*3:(cr+1)*3, cc*3:(cc+1)*3]
            if new_macro[cr, cc] != 0 or np.all(target_sb != 0):
                next_active = None
            
            score = self._minimax_numpy(new_board, new_macro, next_active, max_depth - 1, alpha, beta, False)

            if score > best_score:
                best_score = score
                best_move = (br, bc, cr, cc)

            alpha = max(alpha, score)
            if beta <= alpha:
                break

        return best_move if best_move else random.choice(valid_moves)

    def _minimax_numpy(self, board, macro_board, active_board, depth, alpha, beta, is_maximizing):
        if (np.any(np.sum(macro_board, axis=0) == 3) or 
            np.any(np.sum(macro_board, axis=1) == 3) or 
            np.trace(macro_board) == 3 or 
            np.trace(np.fliplr(macro_board)) == 3):
            return 1000 + depth
        elif (np.any(np.sum(macro_board, axis=0) == -3) or 
              np.any(np.sum(macro_board, axis=1) == -3) or 
              np.trace(macro_board) == -3 or 
              np.trace(np.fliplr(macro_board)) == -3):
            return -1000 - depth
            
        if depth <= 0:
            return self._evaluate_numpy(board, macro_board)

        moves = []
        if active_board is None:
            for br in range(3):
                for bc in range(3):
                    if macro_board[br, bc] == 0:
                        sb = board[br*3:(br+1)*3, bc*3:(bc+1)*3]
                        if not np.all(sb != 0):
                            empties = np.argwhere(sb == 0)
                            for cr, cc in empties:
                                moves.append((br, bc, cr, cc))
        else:
            abr, abc = active_board
            sb = board[abr*3:(abr+1)*3, abc*3:(abc+1)*3]
            empties = np.argwhere(sb == 0)
            for cr, cc in empties:
                moves.append((abr, abc, cr, cc))
                
        if not moves:
            return 0

        if is_maximizing:
            max_score = float('-inf')
            for br, bc, cr, cc in moves:
                nb = board.copy()
                nm = macro_board.copy()
                nb[br*3+cr, bc*3+cc] = 1
                
                sb = nb[br*3:(br+1)*3, bc*3:(bc+1)*3]
                if (np.abs(sb.sum(axis=0)) == 3).any() or (np.abs(sb.sum(axis=1)) == 3).any() or abs(sb.trace()) == 3 or abs(np.fliplr(sb).trace()) == 3:
                    nm[br, bc] = 1
                
                target_sb = nb[cr*3:(cr+1)*3, cc*3:(cc+1)*3]
                if nm[cr, cc] != 0 or np.all(target_sb != 0):
                    nxt = None
                else:
                    nxt = (cr, cc)
                    
                score = self._minimax_numpy(nb, nm, nxt, depth - 1, alpha, beta, False)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha: break
            return max_score
        else:
            min_score = float('inf')
            for br, bc, cr, cc in moves:
                nb = board.copy()
                nm = macro_board.copy()
                nb[br*3+cr, bc*3+cc] = -1
                
                sb = nb[br*3:(br+1)*3, bc*3:(bc+1)*3]
                if (np.abs(sb.sum(axis=0)) == 3).any() or (np.abs(sb.sum(axis=1)) == 3).any() or abs(sb.trace()) == 3 or abs(np.fliplr(sb).trace()) == 3:
                    nm[br, bc] = -1
                
                target_sb = nb[cr*3:(cr+1)*3, cc*3:(cc+1)*3]
                if nm[cr, cc] != 0 or np.all(target_sb != 0):
                    nxt = None
                else:
                    nxt = (cr, cc)
                    
                score = self._minimax_numpy(nb, nm, nxt, depth - 1, alpha, beta, True)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha: break
            return min_score

    def _evaluate_numpy(self, board, macro_board):
        score = 0
        score += np.sum(macro_board) * 500
        
        lines = np.concatenate([
            np.sum(macro_board, axis=1),
            np.sum(macro_board, axis=0),
            [np.trace(macro_board)],
            [np.trace(np.fliplr(macro_board))]
        ])
        score += np.sum(lines == 2) * 50
        score -= np.sum(lines == -2) * 50
        
        playable_mask = (macro_board == 0).astype(np.int8)
        full_mask = np.repeat(np.repeat(playable_mask, 3, axis=0), 3, axis=1)
        active_board = board * full_mask
        score += np.sum(active_board) * 2
        
        if macro_board[1, 1] == 1: score += 50
        
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
        self.screen.fill(BACKGROUND)

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
        
        # Sub-board rect with padding for visual separation
        board_rect = pygame.Rect(base_x + 4, base_y + 4, self.sub_board_size - 8, self.sub_board_size - 8)

        # Draw background for active/playable boards
        if game.is_valid_board(board_row, board_col):
            # Use transparent surface for highlight
            highlight_color = HIGHLIGHT_X if game.current_player == 'X' else HIGHLIGHT_O
            
            # Draw a clean background first
            pygame.draw.rect(self.screen, WHITE, board_rect, border_radius=8)
            
            # Draw the highlight tint
            surf = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
            surf.fill(highlight_color)
            self.screen.blit(surf, board_rect)
            
            # Border for active board
            border_color = PLAYER_X_COLOR if game.current_player == 'X' else PLAYER_O_COLOR
            pygame.draw.rect(self.screen, border_color, board_rect, width=2, border_radius=8)
        else:
            # Inactive board background
            pygame.draw.rect(self.screen, LIGHT_GRAY, board_rect, border_radius=8)

        # Draw won board overlay
        if sub_board.winner:
            # Slightly darker overlay for won boards
            overlay_color = WIN_X_COLOR if sub_board.winner == 'X' else WIN_O_COLOR
            # Use alpha for the overlay
            surf = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
            surf.fill((*overlay_color, 40)) # Very light tint
            self.screen.blit(surf, board_rect)
            
            # Draw large X or O
            self._draw_large_symbol(sub_board.winner, base_x, base_y)
        
        # Draw grid lines for sub-board (only if not won, or if won but we want to see grid slightly)
        # Actually, if won, we usually just show the big symbol. But seeing the grid is nice.
        if not sub_board.winner:
            line_width = max(1, self.cell_size // 30)
            for i in range(1, 3):
                # Vertical lines
                start_x = base_x + i * self.cell_size
                pygame.draw.line(self.screen, GRAY,
                            (start_x, base_y + 5),
                            (start_x, base_y + self.sub_board_size - 5), line_width)
                # Horizontal lines
                start_y = base_y + i * self.cell_size
                pygame.draw.line(self.screen, GRAY,
                            (base_x + 5, start_y),
                            (base_x + self.sub_board_size - 5, start_y), line_width)

        # Draw X's and O's in cells
        if not sub_board.winner:
            for cell_row in range(3):
                for cell_col in range(3):
                    player = sub_board.cells[cell_row][cell_col]
                    if player:
                        cell_x = base_x + cell_col * self.cell_size
                        cell_y = base_y + cell_row * self.cell_size
                        self._draw_symbol(player, cell_x, cell_y, self.cell_size)

        # Draw Hover Effect
        if game.is_valid_board(board_row, board_col) and not sub_board.winner:
            mouse_pos = pygame.mouse.get_pos()
            coords = self.get_board_and_cell(mouse_pos)
            if coords:
                m_br, m_bc, m_cr, m_cc = coords
                if m_br == board_row and m_bc == board_col:
                    if sub_board.cells[m_cr][m_cc] is None:
                        # Draw hover highlight
                        cell_x = base_x + m_cc * self.cell_size
                        cell_y = base_y + m_cr * self.cell_size
                        cell_rect = pygame.Rect(cell_x + 2, cell_y + 2, self.cell_size - 4, self.cell_size - 4)
                        
                        hover_color = (*PLAYER_X_COLOR, 50) if game.current_player == 'X' else (*PLAYER_O_COLOR, 50)
                        surf = pygame.Surface((cell_rect.width, cell_rect.height), pygame.SRCALPHA)
                        surf.fill(hover_color)
                        self.screen.blit(surf, cell_rect)

    def _draw_main_grid(self):
        """Draw the main 3x3 grid lines."""
        line_width = max(4, self.cell_size // 15)
        for i in range(4):
            # Vertical lines
            x = self.board_offset_x + i * self.sub_board_size
            # Draw with rounded caps if possible, or just standard lines
            # Adjust length slightly to match the rounded sub-boards
            start_y = self.board_offset_y
            end_y = self.board_offset_y + self.board_size
            pygame.draw.line(self.screen, BLACK, (x, start_y), (x, end_y), line_width)
            
            # Horizontal lines
            y = self.board_offset_y + i * self.sub_board_size
            start_x = self.board_offset_x
            end_x = self.board_offset_x + self.board_size
            pygame.draw.line(self.screen, BLACK, (start_x, y), (end_x, y), line_width)

    def _draw_symbol(self, player: str, x: int, y: int, size: int):
        """Draw X or O in a cell. Style depends on IS_DARK_MODE."""
        padding = int(size * 0.25)
        
        if not IS_DARK_MODE:
            # === FLAT STYLE (Light Mode) ===
            line_width = max(4, size // 10)
            radius = line_width // 2
            
            color = PLAYER_X_COLOR if player == 'X' else PLAYER_O_COLOR
            shadow_color = (0, 0, 0, 20)

            if player == 'X':
                points = [
                    ((x + padding, y + padding), (x + size - padding, y + size - padding)),
                    ((x + size - padding, y + padding), (x + padding, y + size - padding))
                ]
                # Draw shadow
                shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                for start, end in points:
                    s_start = (start[0] - x + 2, start[1] - y + 2)
                    s_end = (end[0] - x + 2, end[1] - y + 2)
                    pygame.draw.line(shadow_surf, shadow_color, s_start, s_end, line_width)
                    pygame.draw.circle(shadow_surf, shadow_color, s_start, radius)
                    pygame.draw.circle(shadow_surf, shadow_color, s_end, radius)
                self.screen.blit(shadow_surf, (x, y))

                # Draw X
                for start, end in points:
                    pygame.draw.line(self.screen, color, start, end, line_width)
                    pygame.draw.circle(self.screen, color, start, radius)
                    pygame.draw.circle(self.screen, color, end, radius)
            else:
                center = (x + size // 2, y + size // 2)
                circle_radius = size // 2 - padding
                # Draw shadow
                shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(shadow_surf, shadow_color, (size // 2 + 2, size // 2 + 2), circle_radius, line_width)
                self.screen.blit(shadow_surf, (x, y))
                # Draw O
                pygame.draw.circle(self.screen, color, center, circle_radius, line_width)
        
        else:
            # === REALISTIC NEON TUBE STYLE (Dark Mode) ===
            tube_width = max(5, size // 12)
            
            if player == 'X':
                color = PLAYER_X_COLOR
                points = [
                    ((x + padding, y + padding), (x + size - padding, y + size - padding)),
                    ((x + size - padding, y + padding), (x + padding, y + size - padding))
                ]
                
                # Create a surface for the neon effect
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # 1. Drop Shadow (Offset)
                shadow_offset = 4
                for start, end in points:
                    s_start = (start[0] - x + shadow_offset, start[1] - y + shadow_offset)
                    s_end = (end[0] - x + shadow_offset, end[1] - y + shadow_offset)
                    pygame.draw.line(surf, (0, 0, 0, 120), s_start, s_end, tube_width + 2)
                    pygame.draw.circle(surf, (0, 0, 0, 120), s_start, (tube_width + 2) // 2)
                    pygame.draw.circle(surf, (0, 0, 0, 120), s_end, (tube_width + 2) // 2)

                # 2. Outer Glow (Wide, Soft)
                glow_width = tube_width * 4
                for start, end in points:
                    l_start = (start[0] - x, start[1] - y)
                    l_end = (end[0] - x, end[1] - y)
                    pygame.draw.line(surf, (*color, 30), l_start, l_end, glow_width)
                    pygame.draw.circle(surf, (*color, 30), l_start, glow_width // 2)
                    pygame.draw.circle(surf, (*color, 30), l_end, glow_width // 2)

                # 3. Inner Glow (Brighter)
                mid_width = tube_width * 2
                for start, end in points:
                    l_start = (start[0] - x, start[1] - y)
                    l_end = (end[0] - x, end[1] - y)
                    pygame.draw.line(surf, (*color, 80), l_start, l_end, mid_width)
                    pygame.draw.circle(surf, (*color, 80), l_start, mid_width // 2)
                    pygame.draw.circle(surf, (*color, 80), l_end, mid_width // 2)

                # 4. Colored Tube Body (Solid)
                for start, end in points:
                    l_start = (start[0] - x, start[1] - y)
                    l_end = (end[0] - x, end[1] - y)
                    pygame.draw.line(surf, color, l_start, l_end, tube_width)
                    pygame.draw.circle(surf, color, l_start, tube_width // 2)
                    pygame.draw.circle(surf, color, l_end, tube_width // 2)

                # 5. White Core (Thin, Center)
                core_width = max(2, tube_width // 3)
                for start, end in points:
                    l_start = (start[0] - x, start[1] - y)
                    l_end = (end[0] - x, end[1] - y)
                    pygame.draw.line(surf, (255, 255, 255), l_start, l_end, core_width)
                    pygame.draw.circle(surf, (255, 255, 255), l_start, core_width // 2)
                    pygame.draw.circle(surf, (255, 255, 255), l_end, core_width // 2)

                self.screen.blit(surf, (x, y))

            else: # O
                color = PLAYER_O_COLOR
                center = (x + size // 2, y + size // 2)
                radius = size // 2 - padding
                local_center = (size // 2, size // 2)
                
                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                
                # 1. Shadow
                shadow_offset = 4
                s_center = (local_center[0] + shadow_offset, local_center[1] + shadow_offset)
                pygame.draw.circle(surf, (0, 0, 0, 120), s_center, radius, tube_width + 2)

                # 2. Outer Glow
                glow_width = tube_width * 4
                pygame.draw.circle(surf, (*color, 30), local_center, radius, glow_width)

                # 3. Inner Glow
                mid_width = tube_width * 2
                pygame.draw.circle(surf, (*color, 80), local_center, radius, mid_width)

                # 4. Tube Body
                pygame.draw.circle(surf, color, local_center, radius, tube_width)

                # 5. White Core
                core_width = max(2, tube_width // 3)
                pygame.draw.circle(surf, (255, 255, 255), local_center, radius, core_width)

                self.screen.blit(surf, (x, y))

    def _draw_large_symbol(self, player: str, x: int, y: int):
        """Draw a large X or O. Style depends on IS_DARK_MODE."""
        padding = self.sub_board_size // 6
        
        if not IS_DARK_MODE:
            # === FLAT STYLE ===
            line_width = max(8, self.sub_board_size // 12)
            radius = line_width // 2
            
            color = WIN_X_COLOR if player == 'X' else WIN_O_COLOR
            shadow_color = (0, 0, 0, 15)

            if player == 'X':
                points = [
                    ((x + padding, y + padding), (x + self.sub_board_size - padding, y + self.sub_board_size - padding)),
                    ((x + self.sub_board_size - padding, y + padding), (x + padding, y + self.sub_board_size - padding))
                ]
                # Draw shadow
                shadow_surf = pygame.Surface((self.sub_board_size, self.sub_board_size), pygame.SRCALPHA)
                for start, end in points:
                    s_start = (start[0] - x + 3, start[1] - y + 3)
                    s_end = (end[0] - x + 3, end[1] - y + 3)
                    pygame.draw.line(shadow_surf, shadow_color, s_start, s_end, line_width)
                    pygame.draw.circle(shadow_surf, shadow_color, s_start, radius)
                    pygame.draw.circle(shadow_surf, shadow_color, s_end, radius)
                self.screen.blit(shadow_surf, (x, y))

                # Draw X
                for start, end in points:
                    pygame.draw.line(self.screen, color, start, end, line_width)
                    pygame.draw.circle(self.screen, color, start, radius)
                    pygame.draw.circle(self.screen, color, end, radius)
            else:
                center = (x + self.sub_board_size // 2, y + self.sub_board_size // 2)
                circle_radius = self.sub_board_size // 2 - padding
                # Draw shadow
                shadow_surf = pygame.Surface((self.sub_board_size, self.sub_board_size), pygame.SRCALPHA)
                pygame.draw.circle(shadow_surf, shadow_color, (self.sub_board_size // 2 + 3, self.sub_board_size // 2 + 3), circle_radius, line_width)
                self.screen.blit(shadow_surf, (x, y))
                # Draw O
                pygame.draw.circle(self.screen, color, center, circle_radius, line_width)
                
        else:
            # === NEON STYLE ===
            base_width = max(8, self.sub_board_size // 12)
            layers = [
                (7, 30),
                (4, 70),
                (2.5, 120),
                (1.5, 180)
            ]
            
            if player == 'X':
                start_pos1 = (x + padding, y + padding)
                end_pos1 = (x + self.sub_board_size - padding, y + self.sub_board_size - padding)
                start_pos2 = (x + self.sub_board_size - padding, y + padding)
                end_pos2 = (x + padding, y + self.sub_board_size - padding)
                
                glow_surf = pygame.Surface((self.sub_board_size, self.sub_board_size), pygame.SRCALPHA)
                local_start1 = (padding, padding)
                local_end1 = (self.sub_board_size - padding, self.sub_board_size - padding)
                local_start2 = (self.sub_board_size - padding, padding)
                local_end2 = (padding, self.sub_board_size - padding)
                
                for width_mult, alpha in layers:
                    current_width = int(base_width * width_mult)
                    color = (*WIN_X_COLOR, alpha)
                    pygame.draw.line(glow_surf, color, local_start1, local_end1, current_width)
                    pygame.draw.line(glow_surf, color, local_start2, local_end2, current_width)
                    # Rounded caps for glow
                    pygame.draw.circle(glow_surf, color, local_start1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_start2, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end2, current_width // 2)
                
                self.screen.blit(glow_surf, (x, y))
                
                core_color = (255, 255, 255)
                pygame.draw.line(self.screen, core_color, start_pos1, end_pos1, base_width // 2 + 1)
                pygame.draw.line(self.screen, core_color, start_pos2, end_pos2, base_width // 2 + 1)
                # Rounded caps for core
                pygame.draw.circle(self.screen, core_color, start_pos1, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, end_pos1, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, start_pos2, (base_width // 2 + 1) // 2)
                pygame.draw.circle(self.screen, core_color, end_pos2, (base_width // 2 + 1) // 2)
            else:
                center = (x + self.sub_board_size // 2, y + self.sub_board_size // 2)
                radius = self.sub_board_size // 2 - padding
                local_center = (self.sub_board_size // 2, self.sub_board_size // 2)
                
                glow_surf = pygame.Surface((self.sub_board_size, self.sub_board_size), pygame.SRCALPHA)
                for width_mult, alpha in layers:
                    current_width = int(base_width * width_mult)
                    color = (*WIN_O_COLOR, alpha)
                    pygame.draw.circle(glow_surf, color, local_center, radius, current_width)
                
                self.screen.blit(glow_surf, (x, y))
                
                core_color = (255, 255, 255)
                pygame.draw.circle(self.screen, core_color, center, radius, base_width // 2 + 1)

    def _draw_status(self, game: UltimateTicTacToe):
        """Draw the game status at the bottom."""
        status_y = self.board_offset_y + self.board_size + 15
        
        # Draw status bar background
        # We don't fill a rect here as GameRenderer.draw already filled with BACKGROUND
        
        center_x = self.window_width // 2

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
                color = WIN_X_COLOR if game.winner == 'X' else WIN_O_COLOR
            else:
                text = "Broke Even" # Draw
                color = TEXT_DARK
        else:
            # Show whose turn it is
            if self.game_mode == GameMode.ONE_PLAYER:
                if game.current_player == 'X':
                    text = "Your turn (X)"
                else:
                    text = "AI thinking..."
            else:
                text = f"Player {game.current_player}'s turn"
            color = PLAYER_X_COLOR if game.current_player == 'X' else PLAYER_O_COLOR

        # Draw status text
        if text:
            status_surface = FONT_MEDIUM.render(text, True, color)
            status_rect = status_surface.get_rect(center=(center_x, status_y + 10))
            self.screen.blit(status_surface, status_rect)

        # Draw mode info
        if self.game_mode:
            if self.game_mode == GameMode.ONE_PLAYER and self.difficulty:
                mode_text = f"vs {self.difficulty.value} AI"
            else:
                mode_text = "2 Players"
            mode_surface = FONT_SMALL.render(mode_text, True, GRAY)
            self.screen.blit(mode_surface, (20, status_y))

        # Bottom row with home and restart hints
        button_row_y = status_y + 40

        # Prepare text surfaces
        home_text = "Press E to Return Home"
        home_color = BUTTON_HOVER if self.home_button_hovered else GRAY
        home_surface = FONT_SMALL.render(home_text, True, home_color)

        sep_surface = FONT_SMALL.render("|", True, LIGHT_GRAY)

        restart_text = "Press R to Restart"
        restart_surface = FONT_SMALL.render(restart_text, True, GRAY)

        theme_text = "Press D for Theme"
        theme_surface = FONT_SMALL.render(theme_text, True, GRAY)

        # Calculate total width and center position
        spacing = 15
        total_width = (home_surface.get_width() + spacing + 
                      sep_surface.get_width() + spacing + 
                      restart_surface.get_width() + spacing +
                      sep_surface.get_width() + spacing +
                      theme_surface.get_width())
                      
        start_x = (self.window_width - total_width) // 2

        # Draw home hint
        home_x = start_x
        self.screen.blit(home_surface, (home_x, button_row_y))

        # Update home button rect for click detection
        self.home_button_rect = pygame.Rect(
            home_x - 5, button_row_y - 5,
            home_surface.get_width() + 10, home_surface.get_height() + 10
        )

        # Draw underline when hovered
        if self.home_button_hovered:
            underline_y = button_row_y + home_surface.get_height()
            pygame.draw.line(self.screen, BUTTON_HOVER,
                           (home_x, underline_y),
                           (home_x + home_surface.get_width(), underline_y), 2)

        # Draw separator
        sep_x = home_x + home_surface.get_width() + spacing
        self.screen.blit(sep_surface, (sep_x, button_row_y))

        # Draw restart hint
        restart_x = sep_x + sep_surface.get_width() + spacing
        self.screen.blit(restart_surface, (restart_x, button_row_y))
        
        # Draw separator
        sep_x2 = restart_x + restart_surface.get_width() + spacing
        self.screen.blit(sep_surface, (sep_x2, button_row_y))
        
        # Draw theme hint
        theme_x = sep_x2 + sep_surface.get_width() + spacing
        self.screen.blit(theme_surface, (theme_x, button_row_y))

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

        # Mode selection loop (allows returning from tutorial)
        game_mode = None
        while game_mode is None:
            mode_screen = ModeSelectScreen(screen, sound_manager)
            result = mode_screen.run()
            screen = pygame.display.get_surface()

            if result == "TUTORIAL":
                # Show tutorial
                tutorial = TutorialScreen(screen, sound_manager)
                tutorial.run()
                screen = pygame.display.get_surface()
                # Loop back to mode selection
                continue
            else:
                game_mode = result

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
                    elif event.key == pygame.K_d:
                        # D key toggles theme
                        set_theme(not IS_DARK_MODE)
                        # We might need to force a redraw or update specific surfaces if they cached colors?
                        # GameRenderer draws everything every frame using the globals, so it should be fine.
                        # But menu buttons in ModeSelect/DifficultySelect are created with specific colors.
                        # We are in the game loop here, so only game renderer matters.
                        # However, if we return to home, the menus might have old colors if not re-initialized.
                        # Luckily, ModeSelectScreen is re-instantiated in the while app_running loop.
                        pass

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
