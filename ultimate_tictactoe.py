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
import threading
import numpy as np
import ctypes
import platform
from typing import Optional, Tuple, List
from enum import Enum


def get_display_scale_factor() -> float:
    """Get the display scale factor for DPI awareness."""
    if platform.system() == 'Windows':
        try:
            # Enable DPI awareness on Windows
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except (AttributeError, OSError):
                pass

        try:
            # Get the scale factor
            scaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
            return scaleFactor
        except (AttributeError, OSError):
            pass

    return 1.0


# Get display scale factor before pygame init
DISPLAY_SCALE = get_display_scale_factor()


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
    OPPONENT_MOVED = 5       # Show where O played
    CONSTRAINT_RESULT = 6    # Show where O's move sent X
    CONSTRAINT_PRACTICE = 7  # Practice constraint (guided)
    SEE_CONSTRAINT = 8       # See effect of your move
    WIN_MINI_BOARD = 9       # Win a mini-board (guided)
    FREE_MOVE_SETUP = 10     # Explain free move scenario
    FREE_MOVE_RULE = 11      # Practice free move
    PRACTICE_MODE = 12       # Free practice
    COMPLETE = 13            # Tutorial complete


# Initialize pygame
pygame.init()
pygame.mixer.init()

# Theme Management
IS_DARK_MODE = False

# Static Colors (Constant) - Premium PS5-style palette
MENU_BACKGROUND = (15, 23, 42)        # Modern Slate Dark (matches Dark Mode)
RED = (231, 76, 60)
BLUE = (66, 135, 245)                 # Refined blue
GREEN = (46, 204, 113)
ORANGE = (230, 126, 34)
PURPLE = (155, 89, 182)
YELLOW = (241, 196, 15)
GOLD = (255, 203, 71)                 # Warmer gold
BUTTON_DEFAULT = (55, 90, 145)        # Sophisticated steel blue
BUTTON_HOVER = (75, 115, 175)         # Lighter on hover
TEXT_LIGHT = (245, 245, 250)          # Soft white

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
        BACKGROUND = (15, 23, 42)     # Deep midnight blue/slate (Modern Dark)
        WHITE = (30, 41, 59)          # Dark slate for sub-board bg
        BLACK = (148, 163, 184)       # Blue-gray for grid lines (Slate-400)
        GRAY = (203, 213, 225)        # Light slate for text
        LIGHT_GRAY = (51, 65, 85)     # Slate-700 for separators
        
        # Neon/Vibrant accents for dark mode
        PLAYER_X_COLOR = (34, 211, 238)   # Cyan-400
        PLAYER_O_COLOR = (244, 114, 182)  # Pink-400
        WIN_X_COLOR = (8, 145, 178)       # Darker cyan
        WIN_O_COLOR = (219, 39, 119)      # Darker pink
        
        # Brighter highlights
        HIGHLIGHT_X = (34, 211, 238, 50)
        HIGHLIGHT_O = (244, 114, 182, 50)
        TEXT_DARK = (241, 245, 249)   # Near white
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

# Game settings (default sizes, adjusted for display scaling)
# Scale down window size for high DPI displays to prevent overflow
_BASE_WINDOW_SIZE = 630
_BASE_STATUS_HEIGHT = 100
_BASE_MIN_SIZE = 400

DEFAULT_WINDOW_SIZE = int(_BASE_WINDOW_SIZE / DISPLAY_SCALE) if DISPLAY_SCALE > 1.0 else _BASE_WINDOW_SIZE
DEFAULT_BOARD_SIZE = int(DEFAULT_WINDOW_SIZE * 0.95)
DEFAULT_MARGIN = 15
DEFAULT_STATUS_HEIGHT = int(_BASE_STATUS_HEIGHT / DISPLAY_SCALE) if DISPLAY_SCALE > 1.0 else _BASE_STATUS_HEIGHT
MIN_WINDOW_SIZE = int(_BASE_MIN_SIZE / DISPLAY_SCALE) if DISPLAY_SCALE > 1.0 else _BASE_MIN_SIZE

# Get the directory where the script is located
try:
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    SCRIPT_DIR = os.getcwd()
SOUNDS_DIR = os.path.join(SCRIPT_DIR, 'sounds')

# Fonts - Premium PS5-style typography
pygame.font.init()

def scale_font_size(base_size: int) -> int:
    """Scale font size based on display DPI to prevent text overflow."""
    if DISPLAY_SCALE > 1.0:
        return int(base_size / DISPLAY_SCALE)
    return base_size

def get_font(size: int, bold: bool = False, light: bool = False) -> pygame.font.Font:
    """Get a premium font with cross-platform fallbacks."""
    # Scale font size for high DPI displays
    scaled_size = scale_font_size(size)

    # Premium font stack: modern, clean sans-serif fonts
    font_stack = [
        'Segoe UI',           # Windows modern UI
        'SF Pro Display',     # macOS system font
        'Helvetica Neue',     # macOS classic
        'Century Gothic',     # Geometric, premium feel
        'Calibri',            # Windows fallback
        'Arial',              # Universal fallback
    ]

    for font_name in font_stack:
        try:
            font = pygame.font.SysFont(font_name, scaled_size, bold=bold)
            # Verify the font loaded (not default)
            if font.get_height() > 0:
                return font
        except:
            continue

    return pygame.font.SysFont(None, scaled_size, bold=bold)

FONT_LARGE = get_font(52, bold=True)
FONT_MEDIUM = get_font(24)
FONT_SMALL = get_font(18)
FONT_TITLE = get_font(48, bold=True)
FONT_SUBTITLE = get_font(22)
FONT_BROKE_EVEN = get_font(64, bold=True)
FONT_BUTTON = get_font(26, bold=True)
FONT_MENU_TITLE = get_font(40, bold=True)


def draw_premium_background(screen: pygame.Surface):
    """Draw a premium PS5-style background with vignette effect."""
    width, height = screen.get_size()
    screen.fill(MENU_BACKGROUND)

    # Subtle vignette effect
    vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    for i in range(40):
        alpha = int(i * 0.6)
        pygame.draw.rect(vignette, (0, 0, 0, alpha),
                        (i, i, width - 2*i, height - 2*i), 1)
    screen.blit(vignette, (0, 0))


def draw_title_with_glow(screen: pygame.Surface, text: str, center_pos: tuple,
                         font: pygame.font.Font = None, color: tuple = None):
    """Draw title text with a subtle glow effect."""
    if font is None:
        font = FONT_MENU_TITLE
    if color is None:
        color = GOLD

    # Draw glow
    glow_surf = font.render(text, True, color)
    glow_surf.set_alpha(50)
    for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2), (0, 3), (0, -3)]:
        glow_rect = glow_surf.get_rect(center=(center_pos[0] + offset[0], center_pos[1] + offset[1]))
        screen.blit(glow_surf, glow_rect)

    # Draw main text
    title_surf = font.render(text, True, color)
    title_rect = title_surf.get_rect(center=center_pos)
    screen.blit(title_surf, title_rect)


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

    def play(self, name: str, pan: float = 0.0, volume_var: bool = False):
        """
        Play a sound by name with optional panning and volume variation.
        pan: -1.0 (left) to 1.0 (right)
        volume_var: if True, slightly randomize volume
        """
        if name in self.sounds:
            sound = self.sounds[name]
            
            # Calculate volume (base 1.0 with optional variation)
            vol = 1.0
            if volume_var:
                vol = random.uniform(0.9, 1.0)
            
            sound.set_volume(vol)
            
            # Play and get channel
            channel = sound.play()
            if channel:
                # enhanced stereo panning
                # pan is -1.0 to 1.0
                # left volume: 1.0 when pan <= 0, decreases to 0 as pan -> 1
                # right volume: 1.0 when pan >= 0, decreases to 0 as pan -> -1
                
                # Simple linear panning
                right = (pan + 1) / 2
                left = 1 - right
                
                # Clamp
                left = max(0.0, min(1.0, left))
                right = max(0.0, min(1.0, right))
                
                channel.set_volume(left, right)





class ParticleType(Enum):
    CONFETTI = 0
    SPARK = 1
    OFFSET_SMOKE = 2

class Particle:
    """A generic particle for visual effects."""
    
    def __init__(self, x: float, y: float, p_type: ParticleType, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.type = p_type
        self.color = color
        self.lifetime = 1.0
        
        if p_type == ParticleType.CONFETTI:
            self.vx = random.uniform(-5, 5)
            self.vy = random.uniform(-12, -6)
            self.size = random.randint(6, 12)
            self.gravity = 0.3
            self.decay = random.uniform(0.005, 0.015)
            self.rotation = random.uniform(0, 360)
            self.rotation_speed = random.uniform(-10, 10)
        elif p_type == ParticleType.SPARK:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.size = random.randint(2, 5)
            self.gravity = 0.1
            self.decay = random.uniform(0.02, 0.05)
            # Add slight random drag
            self.drag = 0.9
            self.rotation = 0
            self.rotation_speed = 0
        elif p_type == ParticleType.OFFSET_SMOKE:
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.5, 2)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.size = random.randint(4, 8)
            self.gravity = -0.05 # Float up
            self.decay = random.uniform(0.01, 0.03)
            self.rotation = random.uniform(0, 360)
            self.rotation_speed = random.uniform(-2, 2)

    def update(self):
        """Update particle state."""
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        
        if self.type == ParticleType.CONFETTI:
            self.vx *= 0.99
        elif self.type == ParticleType.SPARK:
            self.vx *= self.drag
            self.vy *= self.drag
            
        self.rotation += self.rotation_speed
        self.lifetime -= self.decay

    def draw(self, screen: pygame.Surface):
        """Draw the particle."""
        if self.lifetime <= 0:
            return

        alpha = int(255 * self.lifetime)
        
        if self.type == ParticleType.SPARK:
            # Add glow
            surf = pygame.Surface((self.size * 4, self.size * 4), pygame.SRCALPHA)
            # Draw glow
            pygame.draw.circle(surf, (*self.color, alpha // 3), (self.size*2, self.size*2), self.size*2)
            # Draw core
            pygame.draw.circle(surf, (*self.color, alpha), (self.size*2, self.size*2), self.size)
            screen.blit(surf, (int(self.x - self.size*2), int(self.y - self.size*2)))
        else:
            # Standard rect particle
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            if len(self.color) == 4:
                # Handle color with alpha already
                c = self.color
                color_with_alpha = (c[0], c[1], c[2], min(c[3], alpha))
            else:
                color_with_alpha = (*self.color, alpha)
                
            pygame.draw.rect(surf, color_with_alpha, (0, 0, self.size, self.size))
            rotated = pygame.transform.rotate(surf, self.rotation)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated, rect)

    def is_alive(self) -> bool:
        return self.lifetime > 0

class ParticleSystem:
    """Manages all particle effects."""

    def __init__(self):
        self.particles: List[Particle] = []

    def trigger_confetti(self, window_width: int, window_height: int):
        """Trigger a confetti explosion."""
        for _ in range(150):
            x = random.randint(0, window_width)
            y = random.randint(-50, 50)
            self.particles.append(Particle(x, y, ParticleType.CONFETTI, random.choice(CONFETTI_COLORS)))
            
        for _ in range(50):
             x = random.choice([0, window_width])
             y = random.randint(0, window_height // 2)
             p = Particle(x, y, ParticleType.CONFETTI, random.choice(CONFETTI_COLORS))
             if x == 0: p.vx = abs(p.vx)
             else: p.vx = -abs(p.vx)
             self.particles.append(p)

    # Alias for backward compatibility if needed, but we'll update calls
    def trigger(self, window_width: int, window_height: int):
        self.trigger_confetti(window_width, window_height)

    def trigger_move_effect(self, x: int, y: int, color: Tuple[int, int, int]):
        """Trigger effect for a move."""
        # Sparks
        for _ in range(12):
            self.particles.append(Particle(x, y, ParticleType.SPARK, color))
        # Smoke/Dust
        for _ in range(5):
             self.particles.append(Particle(x, y, ParticleType.OFFSET_SMOKE, (200, 200, 200)))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.is_alive()]

    def draw(self, screen: pygame.Surface):
        for p in self.particles:
            p.draw(screen)


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
        
        # Dynamic fonts and layout
        self.title_font = FONT_TITLE
        self.subtitle_font = FONT_SUBTITLE
        self.frame_rect = pygame.Rect(0, 0, 100, 100)
        self._update_layout()

    def _update_layout(self):
        """Recalculate layout and font sizes based on screen size."""
        width, height = self.screen.get_size()
        
        # Calculate frame dimensions
        frame_width = min(420, width - 40)
        # Ensure minimum width to avoid crash
        frame_width = max(100, frame_width) 
        frame_height = 160
        
        center_x = width // 2
        center_y = height // 2 - 30
        
        self.frame_rect = pygame.Rect(
            center_x - frame_width // 2,
            center_y - frame_height // 2,
            frame_width,
            frame_height
        )
        
        # Helper to find fitting font
        def get_fitting_font(text, base_size, max_width, bold=True):
            size = base_size
            font = get_font(size, bold=bold)
            while font.size(text)[0] > max_width and size > 10:
                size -= 2
                font = get_font(size, bold=bold)
            return font
            
        # Fit title (allow 20px padding)
        self.title_font = get_fitting_font(self.title_text, 48, frame_width - 20, bold=True)
        # Fit subtitle
        self.subtitle_font = get_fitting_font(self.subtitle_text, 22, frame_width - 20, bold=False)

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
                    self._update_layout()

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
        """Draw the splash screen with premium aesthetics."""
        width, height = self.screen.get_size()

        # Deep charcoal background with subtle gradient effect
        self.screen.fill(MENU_BACKGROUND)

        # Draw subtle vignette effect
        vignette = pygame.Surface((width, height), pygame.SRCALPHA)
        for i in range(50):
            alpha = int(i * 0.8)
            pygame.draw.rect(vignette, (0, 0, 0, alpha),
                           (i, i, width - 2*i, height - 2*i), 1)
        self.screen.blit(vignette, (0, 0))

        # Calculate center position with shake
        center_x = width // 2 + self.shake_offset[0]
        center_y = height // 2 - 30 + self.shake_offset[1]

        # Draw stamp frame/border with glow
        if self.stamp_phase >= 1:
            frame_rect = self.frame_rect.copy()
            # Apply shake
            frame_rect.x += self.shake_offset[0]
            frame_rect.y += self.shake_offset[1]
            
            frame_width = frame_rect.width
            frame_height = frame_rect.height

            # Outer glow
            glow_surf = pygame.Surface((frame_width + 20, frame_height + 20), pygame.SRCALPHA)
            glow_color = (*GOLD, 40)
            pygame.draw.rect(glow_surf, glow_color, (0, 0, frame_width + 20, frame_height + 20),
                           border_radius=8)
            self.screen.blit(glow_surf, (frame_rect.x - 10, frame_rect.y - 10))

            pygame.draw.rect(self.screen, GOLD, frame_rect, 3, border_radius=4)
            # Inner frame
            inner_rect = frame_rect.inflate(-16, -16)
            pygame.draw.rect(self.screen, GOLD, inner_rect, 1, border_radius=2)
            
            center_x, center_y = frame_rect.center

        # Draw title text with stamp effect and glow
        title_surf = self.title_font.render(self.title_text, True, GOLD)

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

        # Draw text glow when stamp has landed
        if self.stamp_phase >= 2:
            glow_surf = self.title_font.render(self.title_text, True, (*GOLD[:3],))
            glow_surf.set_alpha(60)
            for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
                glow_rect = glow_surf.get_rect(center=(center_x + offset[0], center_y - 15 + offset[1]))
                self.screen.blit(glow_surf, glow_rect)

        self.screen.blit(title_surf, title_rect)

        # Draw subtitle after stamp lands
        if self.stamp_phase >= 3:
            alpha = min(255, int(self.phase_timer * 500))
            subtitle_surf = self.subtitle_font.render(self.subtitle_text, True, TEXT_LIGHT)
            subtitle_surf.set_alpha(alpha)
            subtitle_rect = subtitle_surf.get_rect(center=(center_x, center_y + 40))
            self.screen.blit(subtitle_surf, subtitle_rect)

        # Draw "Click to continue" hint with smooth pulse
        if self.stamp_phase >= 4:
            pulse = (math.sin(pygame.time.get_ticks() / 400) + 1) / 2
            hint_alpha = int(100 + 155 * pulse)
            hint_surf = FONT_SMALL.render("Click to continue", True, TEXT_LIGHT)
            hint_surf.set_alpha(hint_alpha)
            hint_rect = hint_surf.get_rect(center=(width // 2, height - 60))
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
        self.highlight = False  # Gold outline when True

    def set_enabled(self, enabled: bool):
        """Enable or disable the button."""
        self.enabled = enabled
        if not enabled:
            self.is_hovered = False
            self.highlight = False

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
        """Draw the button with premium PS5-style aesthetics."""
        if not self.enabled:
            base_color = tuple(max(0, int(c * 0.4)) for c in self.color)
            text_color = GRAY
            shadow_offset = 0
        else:
            base_color = self.hover_color if self.is_hovered else self.color
            text_color = TEXT_LIGHT
            shadow_offset = 4 if not self.is_hovered else 2

        button_rect = self.rect.copy()
        border_radius = 16

        # Draw soft shadow (multiple layers for depth)
        if self.enabled:
            for i in range(3):
                shadow_rect = button_rect.copy()
                shadow_rect.y += shadow_offset + i
                shadow_alpha = 30 - i * 10
                shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(shadow_surf, (0, 0, 0, shadow_alpha),
                               (0, 0, shadow_rect.width, shadow_rect.height), border_radius=border_radius)
                screen.blit(shadow_surf, shadow_rect.topleft)

        # Hover press effect
        if self.enabled and self.is_hovered:
            button_rect.y += 2

        # Draw main button body
        pygame.draw.rect(screen, base_color, button_rect, border_radius=border_radius)

        # Draw subtle top highlight (gradient effect)
        if self.enabled:
            highlight_rect = pygame.Rect(button_rect.x + 2, button_rect.y + 2,
                                        button_rect.width - 4, button_rect.height // 3)
            highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            highlight_color = (255, 255, 255, 35 if self.is_hovered else 25)
            pygame.draw.rect(highlight_surf, highlight_color,
                           (0, 0, highlight_rect.width, highlight_rect.height),
                           border_radius=border_radius)
            screen.blit(highlight_surf, highlight_rect.topleft)

        # Draw border - gold highlight or subtle default
        if self.highlight and self.enabled:
            # Gold outline with glow effect
            glow_rect = button_rect.inflate(4, 4)
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*GOLD, 60), (0, 0, glow_rect.width, glow_rect.height),
                           border_radius=border_radius + 2)
            screen.blit(glow_surf, glow_rect.topleft)
            pygame.draw.rect(screen, GOLD, button_rect, width=3, border_radius=border_radius)
        else:
            border_color = tuple(min(c + 30, 255) for c in base_color) if self.enabled else GRAY
            pygame.draw.rect(screen, border_color, button_rect, width=1, border_radius=border_radius)

        # Draw text with subtle shadow
        if self.enabled:
            text_shadow = FONT_BUTTON.render(self.text, True, (0, 0, 0, 80))
            shadow_rect = text_shadow.get_rect(center=(button_rect.centerx + 1, button_rect.centery + 1))
            screen.blit(text_shadow, shadow_rect)

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
        """Draw the mode selection screen with premium aesthetics."""
        width, height = self.screen.get_size()
        draw_premium_background(self.screen)

        # Draw title with glow
        draw_title_with_glow(self.screen, "Select Game Mode", (width // 2, height // 4))

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
        """Draw the difficulty selection screen with premium aesthetics."""
        width, height = self.screen.get_size()
        draw_premium_background(self.screen)

        # Draw title with glow
        draw_title_with_glow(self.screen, "Select Difficulty", (width // 2, height // 4))

        # Draw subtitle
        subtitle_surf = FONT_SUBTITLE.render("You are X, AI is O", True, TEXT_LIGHT)
        subtitle_rect = subtitle_surf.get_rect(center=(width // 2, height // 4 + 45))
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

        # Board state history for going back
        self.board_history: dict = {}  # step -> saved board state
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
        # Particles for completion
        self.particle_system = ParticleSystem()

    def _needs_fresh_board(self, step: TutorialStep) -> bool:
        """Check if this step needs a fresh board setup (not preserved from previous)."""
        # Only these early demo steps need a fresh board
        # All others preserve and build on the game state
        return step in (
            TutorialStep.WELCOME,
            TutorialStep.BOARD_STRUCTURE,
            TutorialStep.WIN_CONDITION,
            TutorialStep.FIRST_MOVE,
            TutorialStep.PRACTICE_MODE,  # Fresh board for free practice
        )

    def _setup_demo_board(self, force_reset: bool = False):
        """Set up the demo board for the current tutorial step."""
        # Only create fresh board for steps that need specific setups
        needs_fresh = force_reset or self._needs_fresh_board(self.current_step)

        if needs_fresh:
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
            # Board preserved from FIRST_MOVE - just update state for O's turn
            if self.demo_game:
                self.demo_game.current_player = 'O'
                # Find where X played and set active board accordingly
                for br in range(3):
                    for bc in range(3):
                        for cr in range(3):
                            for cc in range(3):
                                if self.demo_game.sub_boards[br][bc].cells[cr][cc] == 'X':
                                    self.demo_game.active_board = (cr, cc)
                                    self.last_move_cell = (br, bc, cr, cc)
                                    self.show_constraint_arrow = True
                                    break

        elif self.current_step == TutorialStep.OPPONENT_MOVED:
            # Board preserved - O plays their move
            if self.demo_game and self.demo_game.active_board:
                obr, obc = self.demo_game.active_board
                # O plays top-left cell, which sends X back to board (0,0)!
                self.demo_game.sub_boards[obr][obc].cells[0][0] = 'O'
                self.demo_game.current_player = 'X'
                self.demo_game.active_board = (0, 0)  # Back to top-left board!
                self.last_move_cell = None
                self.show_constraint_arrow = False

        elif self.current_step == TutorialStep.CONSTRAINT_RESULT:
            # Board preserved - show arrow from O's move to where X must play
            if self.demo_game:
                # O played at (0,2,0,0), which sends X to board (0,0)
                self.last_move_cell = (0, 2, 0, 0)
                self.show_constraint_arrow = True
                self.demo_game.active_board = (0, 0)

        elif self.current_step == TutorialStep.CONSTRAINT_PRACTICE:
            # Board preserved - X plays in top-left board (sent back by O's move)
            if self.demo_game:
                self.demo_game.current_player = 'X'
                self.demo_game.active_board = (0, 0)  # Top-left board
                self.last_move_cell = None
                self.show_constraint_arrow = False

        elif self.current_step == TutorialStep.SEE_CONSTRAINT:
            # Board preserved - show arrow from X's move at (0,0,0,1) to board (0,1)
            if self.demo_game:
                # X played top-center cell (0,1) of top-left board -> O goes to top-center board (0,1)
                self.last_move_cell = (0, 0, 0, 1)
                self.show_constraint_arrow = True
                self.demo_game.current_player = 'O'
                self.demo_game.active_board = (0, 1)  # Top-center board

        elif self.current_step == TutorialStep.WIN_MINI_BOARD:
            # Board preserved - X already has (0,0,0,2) and (0,0,0,1) = TWO IN A ROW!
            # Just add O's response move, then X can complete the win
            if self.demo_game:
                # O plays in top-center board (where X sent them), cell (0,0) sends X back
                self.demo_game.sub_boards[0][1].cells[0][0] = 'O'
                self.demo_game.current_player = 'X'
                self.demo_game.active_board = (0, 0)  # X plays in top-left to win!
                self.last_move_cell = None
                self.show_constraint_arrow = False

        elif self.current_step == TutorialStep.FREE_MOVE_SETUP:
            # Board preserved - X just won board (0,0) with top row!
            # X's winning cell (0,0) would send O to board (0,0), but it's WON
            # So O gets a free move. O plays at cell (0,0) in another board...
            if self.demo_game:
                # Mark the top-left board as won (should already be from player's click)
                self.demo_game.sub_boards[0][0].winner = 'X'
                # O takes their free move at (1,0,0,0) - sends X to (0,0) which is won!
                self.demo_game.sub_boards[1][0].cells[0][0] = 'O'
                self.demo_game.current_player = 'X'
                self.demo_game.active_board = None  # X has FREE MOVE!
                self.last_move_cell = (1, 0, 0, 0)  # O's move that sends to won board
                self.show_constraint_arrow = True

        elif self.current_step == TutorialStep.FREE_MOVE_RULE:
            # Same state as FREE_MOVE_SETUP, just update for interaction
            if self.demo_game:
                self.last_move_cell = None
                self.show_constraint_arrow = False

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
            # Highlight top-right cell of top-left board
            if self.step_substep == 0:
                self.highlight_cells = [(0, 0, 0, 2)]

        elif self.current_step == TutorialStep.CONSTRAINT_PRACTICE:
            # Highlight top-center cell of top-left board (builds toward win!)
            if self.step_substep == 0:
                self.highlight_cells = [(0, 0, 0, 1)]

        elif self.current_step == TutorialStep.WIN_MINI_BOARD:
            # Highlight the winning cell (top-left board, top-left cell to complete row)
            if self.step_substep == 0:
                self.highlight_cells = [(0, 0, 0, 0)]

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
        # Gold highlight when ready to proceed
        self.next_btn.highlight = allow_next

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

        if self.current_step == TutorialStep.FIRST_MOVE and self.highlight_cells:
            br, bc, cr, cc = self.highlight_cells[0]
            anchor = self._get_demo_cell_center(
                br, bc, cr, cc, offset_x, offset_y, cell_size, sub_board_size
            )
            TutorialBubble("Click here (top-right cell)", anchor, direction='above', width=200).draw(self.screen)

        elif self.current_step == TutorialStep.CONSTRAINT_PRACTICE and self.highlight_cells:
            br, bc, cr, cc = self.highlight_cells[0]
            anchor = self._get_demo_cell_center(
                br, bc, cr, cc, offset_x, offset_y, cell_size, sub_board_size
            )
            TutorialBubble("Click here", anchor, direction='above', width=120).draw(self.screen)

        elif self.current_step == TutorialStep.WIN_MINI_BOARD and self.highlight_cells:
            br, bc, cr, cc = self.highlight_cells[0]
            anchor = self._get_demo_cell_center(
                br, bc, cr, cc, offset_x, offset_y, cell_size, sub_board_size
            )
            TutorialBubble("Win! Click here", anchor, direction='above', width=140).draw(self.screen)

        elif self.current_step == TutorialStep.FREE_MOVE_RULE:
            # Point to center board (a valid option since top-left is won)
            anchor = self._get_demo_board_center(1, 1, offset_x, offset_y, sub_board_size)
            TutorialBubble("Pick any valid board",
                           anchor, direction='above', width=180).draw(self.screen)

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

            # Update BOARD_STRUCTURE animation
            if self.current_step == TutorialStep.BOARD_STRUCTURE:
                self.animation_timer += dt
                if self.animation_timer >= 800:  # Cycle boards every 800ms (increased from 400ms)
                    self.animation_timer = 0
                    self.board_highlight_index = (self.board_highlight_index + 1) % 9

            # Update particles
            self.particle_system.update()

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

    def _save_board_state(self):
        """Save current board state for this step."""
        if self.demo_game is None:
            return
        # Deep copy the board state
        state = {
            'cells': [[
                [cell for cell in row]
                for row in self.demo_game.sub_boards[br][bc].cells
            ] for br in range(3) for bc in range(3)],
            'winners': [
                self.demo_game.sub_boards[br][bc].winner
                for br in range(3) for bc in range(3)
            ],
            'current_player': self.demo_game.current_player,
            'active_board': self.demo_game.active_board,
            'game_over': self.demo_game.game_over,
            'winner': self.demo_game.winner,
            'last_move_cell': self.last_move_cell,
            'show_constraint_arrow': self.show_constraint_arrow,
            'step_substep': self.step_substep,
        }
        self.board_history[self.current_step] = state

    def _restore_board_state(self, step: TutorialStep) -> bool:
        """Restore board state for a step. Returns True if successful."""
        if step not in self.board_history:
            return False
        state = self.board_history[step]
        if self.demo_game is None:
            self.demo_game = UltimateTicTacToe()
        # Restore cells and winners
        idx = 0
        for br in range(3):
            for bc in range(3):
                for r in range(3):
                    for c in range(3):
                        self.demo_game.sub_boards[br][bc].cells[r][c] = state['cells'][idx][r][c]
                self.demo_game.sub_boards[br][bc].winner = state['winners'][idx]
                idx += 1
        self.demo_game.current_player = state['current_player']
        self.demo_game.active_board = state['active_board']
        self.demo_game.game_over = state['game_over']
        self.demo_game.winner = state['winner']
        self.last_move_cell = state['last_move_cell']
        self.show_constraint_arrow = state['show_constraint_arrow']
        self.step_substep = state['step_substep']
        self._update_highlights()
        return True

    def _next_step(self):
        """Advance to next tutorial step."""
        # Save current state before advancing
        self._save_board_state()

        steps = list(TutorialStep)
        current_idx = steps.index(self.current_step)
        if current_idx < len(steps) - 1:
            self.current_step = steps[current_idx + 1]
            self.step_substep = 0
            # _setup_demo_board handles whether to preserve or reset
            self._setup_demo_board()
            self._update_highlights()

    def _previous_step(self):
        """Go to previous tutorial step."""
        steps = list(TutorialStep)
        current_idx = steps.index(self.current_step)
        if current_idx > 0:
            prev_step = steps[current_idx - 1]
            # Try to restore saved state
            if self._restore_board_state(prev_step):
                self.current_step = prev_step
            else:
                # Fallback to setup
                self.current_step = prev_step
                self.step_substep = 0
                self._setup_demo_board(force_reset=True)
            self._update_highlights()

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
                "The game is a 3x3 grid of mini Tic Tac Toe boards.",
                "Each of the 9 mini boards is highlighted in turn.",
            ],
            TutorialStep.WIN_CONDITION: [
                "How to Win",
                "",
                "Win a mini board by getting 3 in a row inside it.",
                "Win the GAME by winning 3 mini boards in a row!",
            ],
            TutorialStep.FIRST_MOVE: [
                "The Key Rule",
                "",
                "Click the TOP-RIGHT cell of the top-left board.",
                "Watch: your cell position decides the NEXT active board.",
            ],
            TutorialStep.OPPONENT_RESPONSE: [
                "See What Happened",
                "",
                "You played in the TOP-RIGHT CELL of the top-left board.",
                "So O must play in the TOP-RIGHT BOARD (gold outline).",
            ],
            TutorialStep.OPPONENT_MOVED: [
                "O Takes Their Turn",
                "",
                "O played in the TOP-LEFT cell of the top-right board.",
                "Now the same rule applies to you...",
            ],
            TutorialStep.CONSTRAINT_RESULT: [
                "Where You Must Play",
                "",
                "O's TOP-LEFT cell sends you back to the TOP-LEFT board!",
                "Follow the arrow. The gold outline shows your only option.",
            ],
            TutorialStep.CONSTRAINT_PRACTICE: [
                "Your Turn Again",
                "",
                "You're back in the top-left board (gold outline).",
                "Click the highlighted cell to build toward a win!",
            ],
            TutorialStep.SEE_CONSTRAINT: [
                "Building a Win",
                "",
                "You played the TOP-CENTER cell → O goes to TOP-CENTER board.",
                "Notice: you now have TWO in a row in the top-left board!",
            ],
            TutorialStep.WIN_MINI_BOARD: [
                "Win a Mini Board",
                "",
                "O played, and you're back in the top-left board.",
                "Click the highlighted cell to complete the row and WIN!",
            ],
            TutorialStep.FREE_MOVE_SETUP: [
                "Exception: Free Move",
                "",
                "You won the top-left board! O's move sends you there...",
                "But you can't play in a won board. So you get a FREE MOVE!",
            ],
            TutorialStep.FREE_MOVE_RULE: [
                "Free Move - Try It",
                "",
                "All boards with gold outlines are valid.",
                "Pick any open cell in any available board.",
            ],
            TutorialStep.PRACTICE_MODE: [
                "Free Practice",
                "",
                "Experiment freely. Notice how each move sets the next board.",
                "Click Next when ready to play a real game!",
            ],
            TutorialStep.COMPLETE: [
                "You're Ready!",
                "",
                "Remember: cell position = next board.",
                "Good luck!",
            ],
        }
        return instructions.get(self.current_step, [])

    def _draw(self):
        """Draw the tutorial screen with premium aesthetics."""
        self._update_button_states()
        width, height = self.screen.get_size()
        draw_premium_background(self.screen)

        # Draw title with glow
        draw_title_with_glow(self.screen, "How to Play", (width // 2, 35))

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

        # Draw particles (confetti)
        if self.current_step == TutorialStep.COMPLETE:
            self.particle_system.draw(self.screen)

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
                
                # Gold border for active board
                pygame.draw.rect(self.screen, GOLD, board_rect, width=3, border_radius=8)
        
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

    def get_move(self, game: UltimateTicTacToe, callback=None) -> Optional[Tuple[int, int, int, int]]:
        """Get the AI's next move based on difficulty.
        
        Args:
            game: The game state
            callback: Optional function(move_tuple) called when evaluating a top-level move (for visualization)
        """
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
            return self._bigbrain_move(game, valid_moves, callback)

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
                       valid_moves: List[Tuple[int, int, int, int]],
                       callback=None) -> Tuple[int, int, int, int]:
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
            # Visualization callback
            if callback:
                callback((br, bc, cr, cc))
                import time
                time.sleep(0.1)  # Short delay to make thinking visible

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
        self.move_animations = {}  # (br, bc, cr, cc) -> start_time
        
        # Glass Brain visualization state
        self.thinking_move = None  # (br, bc, cr, cc)
        
        self._update_dimensions()
        self._create_home_button()

    def notify_move(self, br: int, bc: int, cr: int, cc: int):
        """Notify renderer of a new move to trigger animation."""
        self.move_animations[(br, bc, cr, cc)] = pygame.time.get_ticks()

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
        self.status_height = DEFAULT_STATUS_HEIGHT
        available_size = min(width, height - self.status_height)

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

    def draw(self, game: UltimateTicTacToe, particle_system: ParticleSystem):
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

        # Draw particles on top
        particle_system.draw(self.screen)

        # Draw "Broke Even" text for draws
        if game.is_draw():
            self._draw_broke_even()

    def _draw_broke_even(self):
        """Draw the 'Broke Even' text for draws."""
        # Animate alpha and scale
        self.broke_even_alpha = min(255, self.broke_even_alpha + 8)
        self.broke_even_scale = min(1.0, self.broke_even_scale + 0.03)

    # Create text surface
        text_surf = FONT_BROKE_EVEN.render("BROKE EVEN", True, TEXT_DARK)

        # Scale if needed
        if self.broke_even_scale < 1.0:
            new_width = int(text_surf.get_width() * self.broke_even_scale)
            new_height = int(text_surf.get_height() * self.broke_even_scale)
            text_surf = pygame.transform.scale(text_surf, (new_width, new_height))

        text_surf.set_alpha(self.broke_even_alpha)

        # Draw semi-transparent background
        bg_rect = pygame.Rect(0, self.window_height // 2 - 50, self.window_width, 100)
        bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
        # Use theme-aware background color
        bg_color = (*BACKGROUND, int(230 * (self.broke_even_alpha / 255)))
        bg_surf.fill(bg_color)
        self.screen.blit(bg_surf, bg_rect)

        # Draw text centered
        text_rect = text_surf.get_rect(center=(self.window_width // 2, self.window_height // 2))
        self.screen.blit(text_surf, text_rect)

    def reset_animations(self):
        """Reset animation states."""
        self.broke_even_alpha = 0
        self.broke_even_scale = 0.5
        self.move_animations.clear()

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
            
            # Gold border for active board with pulse
            pulse = int(abs(math.sin(pygame.time.get_ticks() / 300)) * 2) + 1
            pygame.draw.rect(self.screen, GOLD, board_rect, width=3 + pulse, border_radius=8)
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
                        cell_y = base_y + cell_row * self.cell_size
                        self._draw_symbol(player, cell_x, cell_y, self.cell_size, coords=(board_row, board_col, cell_row, cell_col))

        # Draw Glass Brain thinking highlight
        if self.thinking_move:
            t_br, t_bc, t_cr, t_cc = self.thinking_move
            if t_br == board_row and t_bc == board_col:
                cell_x = base_x + t_cc * self.cell_size
                cell_y = base_y + t_cr * self.cell_size
                
                # Pulse alpha
                alpha = int(100 + 50 * math.sin(pygame.time.get_ticks() / 100))
                s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
                s.fill((*RED, alpha))  # Red tint for thinking
                self.screen.blit(s, (cell_x, cell_y))

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

    def _draw_symbol(self, player: str, x: int, y: int, size: int, coords: Tuple[int, int, int, int] = None):
        """Draw X or O in a cell. Style depends on IS_DARK_MODE."""
        
        # Handle animation
        scale = 1.0
        if coords in self.move_animations:
            elapsed = pygame.time.get_ticks() - self.move_animations[coords]
            duration = 400  # ms
            if elapsed < duration:
                t = elapsed / duration
                # Elastic out easing
                scale = math.sin(-13 * (t + 1) * math.pi / 2) * math.pow(2, -10 * t) + 1
            else:
                del self.move_animations[coords]
        
        # Apply scale if needed
        draw_size = int(size * scale)
        # Center adjustment
        offset = (size - draw_size) // 2
        x += offset
        y += offset
        size = draw_size

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
            # === POLISHED STYLE (Dark Mode) - Subtle glow ===
            tube_width = max(5, size // 12)

            if player == 'X':
                color = PLAYER_X_COLOR
                points = [
                    ((x + padding, y + padding), (x + size - padding, y + size - padding)),
                    ((x + size - padding, y + padding), (x + padding, y + size - padding))
                ]

                surf = pygame.Surface((size, size), pygame.SRCALPHA)

                # 1. Subtle shadow
                shadow_offset = 2
                for start, end in points:
                    s_start = (start[0] - x + shadow_offset, start[1] - y + shadow_offset)
                    s_end = (end[0] - x + shadow_offset, end[1] - y + shadow_offset)
                    pygame.draw.line(surf, (0, 0, 0, 60), s_start, s_end, tube_width)

                # 2. Subtle outer glow
                glow_width = int(tube_width * 1.8)
                for start, end in points:
                    l_start = (start[0] - x, start[1] - y)
                    l_end = (end[0] - x, end[1] - y)
                    pygame.draw.line(surf, (*color, 40), l_start, l_end, glow_width)
                    pygame.draw.circle(surf, (*color, 40), l_start, glow_width // 2)
                    pygame.draw.circle(surf, (*color, 40), l_end, glow_width // 2)

                # 3. Solid colored line
                for start, end in points:
                    l_start = (start[0] - x, start[1] - y)
                    l_end = (end[0] - x, end[1] - y)
                    pygame.draw.line(surf, color, l_start, l_end, tube_width)
                    pygame.draw.circle(surf, color, l_start, tube_width // 2)
                    pygame.draw.circle(surf, color, l_end, tube_width // 2)

                self.screen.blit(surf, (x, y))

            else: # O
                color = PLAYER_O_COLOR
                center = (x + size // 2, y + size // 2)
                radius = size // 2 - padding
                local_center = (size // 2, size // 2)

                surf = pygame.Surface((size, size), pygame.SRCALPHA)

                # 1. Subtle shadow
                shadow_offset = 2
                s_center = (local_center[0] + shadow_offset, local_center[1] + shadow_offset)
                pygame.draw.circle(surf, (0, 0, 0, 60), s_center, radius, tube_width)

                # 2. Subtle outer glow
                glow_width = int(tube_width * 1.8)
                pygame.draw.circle(surf, (*color, 40), local_center, radius, glow_width)

                # 3. Solid colored circle
                pygame.draw.circle(surf, color, local_center, radius, tube_width)

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
            # === POLISHED STYLE (Dark Mode) - Subtle glow ===
            base_width = max(8, self.sub_board_size // 12)
            # Reduced glow: fewer layers, lower alphas
            layers = [
                (2.5, 25),
                (1.8, 60),
                (1.2, 140)
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
                    pygame.draw.circle(glow_surf, color, local_start1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end1, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_start2, current_width // 2)
                    pygame.draw.circle(glow_surf, color, local_end2, current_width // 2)

                self.screen.blit(glow_surf, (x, y))

                # Solid core in player color (not white)
                pygame.draw.line(self.screen, WIN_X_COLOR, start_pos1, end_pos1, base_width)
                pygame.draw.line(self.screen, WIN_X_COLOR, start_pos2, end_pos2, base_width)
                pygame.draw.circle(self.screen, WIN_X_COLOR, start_pos1, base_width // 2)
                pygame.draw.circle(self.screen, WIN_X_COLOR, end_pos1, base_width // 2)
                pygame.draw.circle(self.screen, WIN_X_COLOR, start_pos2, base_width // 2)
                pygame.draw.circle(self.screen, WIN_X_COLOR, end_pos2, base_width // 2)
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

                # Solid core in player color (not white)
                pygame.draw.circle(self.screen, WIN_O_COLOR, center, radius, base_width)

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
            mode_surface = FONT_SMALL.render(mode_text, True, TEXT_DARK)
            self.screen.blit(mode_surface, (20, status_y))

        # Bottom row with home and restart hints
        button_row_y = status_y + 40

        # Prepare text surfaces
        home_text = "Press E to Return Home"
        home_color = BUTTON_HOVER if self.home_button_hovered else TEXT_DARK
        home_surface = FONT_SMALL.render(home_text, True, home_color)

        sep_surface = FONT_SMALL.render("|", True, GRAY)

        restart_text = "Press R to Restart"
        restart_surface = FONT_SMALL.render(restart_text, True, TEXT_DARK)

        theme_text = "Press D for Theme"
        theme_surface = FONT_SMALL.render(theme_text, True, TEXT_DARK)

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

    # AI Threading state
    ai_thread = None
    ai_result_container = [None]
    ai_move_start_time = 0

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
        particle_system = ParticleSystem()
        
        def trigger_move_effects(br, bc, cr, cc):
            """Helper to trigger vfx/sfx for a move."""
            # Calculate screen position
            cx = renderer.board_offset_x + bc * renderer.sub_board_size + cc * renderer.cell_size + renderer.cell_size // 2
            cy = renderer.board_offset_y + br * renderer.sub_board_size + cr * renderer.cell_size + renderer.cell_size // 2
            
            # 1. Determine player color
            moved_player = game.current_player
            if not game.game_over:
                 moved_player = 'O' if game.current_player == 'X' else 'X'
                 
            color = PLAYER_X_COLOR if moved_player == 'X' else PLAYER_O_COLOR
            
            # 2. Particles
            particle_system.trigger_move_effect(cx, cy, color)
            
            # 3. Animation
            renderer.notify_move(br, bc, cr, cc)
            
            # 4. Sound with Pan/Var
            width = screen.get_width()
            pan = (cx / width) * 2 - 1
            # Clamp in case of weirdness
            pan = max(-1.0, min(1.0, pan))
            sound_manager.play('click', pan=pan, volume_var=True)

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
                                    trigger_move_effects(board_row, board_col, cell_row, cell_col)
                                    # If 1 player mode and game not over, trigger AI turn
                                    if ai_player and not game.game_over:
                                        ai_waiting = True
                                        ai_move_start_time = pygame.time.get_ticks()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        game = UltimateTicTacToe()
                        particle_system = ParticleSystem()
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
            # Handle AI turn (Threaded for Glass Brain)
            if ai_waiting and not game.game_over and not return_to_home:
                current_time = pygame.time.get_ticks()
                if current_time - ai_move_start_time > 500:  # Minimum delay before starting
                    
                    if ai_thread is None:
                        # Start AI in a thread
                        ai_result_container = [None]
                        
                        def ai_task():
                            # Callback updates renderer state directly
                            def visualization_callback(move_tuple):
                                renderer.thinking_move = move_tuple
                                
                            try:
                                move = ai_player.get_move(game, callback=visualization_callback)
                                ai_result_container[0] = move
                            except Exception as e:
                                print(f"AI Thread Error: {e}")
                            
                        ai_thread = threading.Thread(target=ai_task)
                        ai_thread.start()
                    
                    elif not ai_thread.is_alive():
                        # Thread finished
                        ai_thread.join()
                        move = ai_result_container[0]
                        renderer.thinking_move = None # Clear thinking visualization
                        
                        if move:
                            br, bc, cr, cc = move
                            if game.make_move(br, bc, cr, cc):
                                trigger_move_effects(br, bc, cr, cc)
                        
                        ai_waiting = False
                        ai_thread = None

            # Check for game end triggers
            if game.just_ended:
                game.just_ended = False
                if game.winner:
                    width, height = screen.get_size()
                    particle_system.trigger_confetti(width, height)
                    sound_manager.play('win')
                else:
                    sound_manager.play('sad')

            # Update particles
            particle_system.update()

            # Draw everything
            renderer.draw(game, particle_system)
            pygame.display.flip()

        # If not returning to home, exit the app
        if not return_to_home:
            app_running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
