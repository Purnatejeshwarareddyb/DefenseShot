"""
DefenseShot: Elite Sniper Academy
GUI utility functions and classes
"""

import pygame
from config import *

class Button:
    """Generic button class"""
    def __init__(self, x, y, width, height, text, font, color=WHITE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.color = color
        self.hover = False
        self.pressed = False

    def is_clicked(self, pos):
        """Check if button is clicked"""
        return self.rect.collidepoint(pos)

    def update(self, mouse_pos):
        """Update button state"""
        self.hover = self.rect.collidepoint(mouse_pos)

    def render(self, screen, bg_color=GRAY, hover_color=LIGHT_GRAY):
        """Render button"""
        # Background
        color = hover_color if self.hover else bg_color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        # Text
        text_surface = self.font.render(self.text, True, self.color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

class InputField:
    """Text input field"""
    def __init__(self, x, y, width, height, placeholder, font, password=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.placeholder = placeholder
        self.font = font
        self.password = password
        self.text = ""
        self.active = False
        self.cursor_pos = 0
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        """Handle input events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.text = self.text[:self.cursor_pos-1] + self.text[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.text):
                    self.text = self.text[:self.cursor_pos] + self.text[self.cursor_pos+1:]
            elif event.key == pygame.K_LEFT:
                self.cursor_pos = max(0, self.cursor_pos - 1)
            elif event.key == pygame.K_RIGHT:
                self.cursor_pos = min(len(self.text), self.cursor_pos + 1)
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.text)
            elif event.unicode.isprintable():
                self.text = self.text[:self.cursor_pos] + event.unicode + self.text[self.cursor_pos:]
                self.cursor_pos += 1

    def update(self):
        """Update cursor animation"""
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink every 30 frames
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def get_text(self):
        """Get current text"""
        return self.text

    def clear(self):
        """Clear text"""
        self.text = ""
        self.cursor_pos = 0

    def render(self, screen):
        """Render input field"""
        # Background
        color = WHITE if self.active else LIGHT_GRAY
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK if self.active else GRAY, self.rect, 2)

        # Text
        display_text = self.text
        if self.password and self.text:
            display_text = "*" * len(self.text)

        if not display_text and not self.active:
            # Show placeholder
            text_surface = self.font.render(self.placeholder, True, GRAY)
        else:
            text_surface = self.font.render(display_text, True, BLACK)

        # Clip text to fit in field
        text_rect = text_surface.get_rect()
        text_rect.centery = self.rect.centery
        text_rect.x = self.rect.x + 10

        screen.blit(text_surface, text_rect)

        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + self.font.size(display_text[:self.cursor_pos])[0]
            pygame.draw.line(screen, BLACK,
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.y + self.rect.height - 5), 2)

class ProgressBar:
    """Progress bar widget"""
    def __init__(self, x, y, width, height, max_value=100):
        self.rect = pygame.Rect(x, y, width, height)
        self.max_value = max_value
        self.current_value = 0
        self.color = GREEN
        self.bg_color = DARK_GRAY

    def set_value(self, value):
        """Set current value"""
        self.current_value = max(0, min(value, self.max_value))

    def render(self, screen):
        """Render progress bar"""
        # Background
        pygame.draw.rect(screen, self.bg_color, self.rect)

        # Progress
        if self.current_value > 0:
            progress_width = int((self.current_value / self.max_value) * self.rect.width)
            progress_rect = pygame.Rect(self.rect.x, self.rect.y, progress_width, self.rect.height)
            pygame.draw.rect(screen, self.color, progress_rect)

        # Border
        pygame.draw.rect(screen, WHITE, self.rect, 2)

class ModuleCard:
    """Module card for dashboard"""
    def __init__(self, x, y, width, height, module_number, title, unlocked=False, completed=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.module_number = module_number
        self.title = title
        self.unlocked = unlocked
        self.completed = completed
        self.hover = False
        self.font = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)

    def is_clicked(self, pos):
        """Check if card is clicked"""
        return self.rect.collidepoint(pos) and self.unlocked

    def update(self, mouse_pos):
        """Update card state"""
        self.hover = self.rect.collidepoint(mouse_pos) and self.unlocked

    def render(self, screen):
        """Render module card"""
        # Background color based on state
        if self.completed:
            bg_color = MILITARY_GREEN
        elif self.unlocked:
            bg_color = NAVY_BLUE if self.hover else BLUE
        else:
            bg_color = DARK_GRAY

        pygame.draw.rect(screen, bg_color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)

        # Module number
        number_text = f"Module {self.module_number}"
        number_surface = self.font.render(number_text, True, WHITE)
        number_rect = number_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + 10)
        screen.blit(number_surface, number_rect)

        # Title (wrapped)
        title_lines = wrap_text(self.title, self.font_small, self.rect.width - 20)
        y_offset = self.rect.y + 40
        for line in title_lines:
            line_surface = self.font_small.render(line, True, WHITE)
            line_rect = line_surface.get_rect(centerx=self.rect.centerx, y=y_offset)
            screen.blit(line_surface, line_rect)
            y_offset += 20

        # Status indicator
        if self.completed:
            status_text = "✓ COMPLETED"
            status_color = GREEN
        elif self.unlocked:
            status_text = "AVAILABLE"
            status_color = YELLOW
        else:
            status_text = "LOCKED"
            status_color = RED

        status_surface = self.font_small.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(centerx=self.rect.centerx, y=self.rect.y + self.rect.height - 25)
        screen.blit(status_surface, status_rect)

        # Lock icon for locked modules
        if not self.unlocked:
            lock_text = "🔒"
            lock_surface = self.font.render(lock_text, True, RED)
            lock_rect = lock_surface.get_rect(center=self.rect.center)
            screen.blit(lock_surface, lock_rect)

def render_text(screen, text, font, color, x, y, center=False):
    """Render text at position"""
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        screen.blit(text_surface, text_rect)
    else:
        screen.blit(text_surface, (x, y))
    return text_surface

def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width"""
    words = text.split()
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
                current_line = [word]
            else:
                lines.append(word)

    if current_line:
        lines.append(' '.join(current_line))

    return lines

def draw_gradient_rect(screen, color1, color2, rect):
    """Draw a gradient rectangle"""
    for y in range(rect.height):
        ratio = y / rect.height
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        pygame.draw.line(screen, (r, g, b),
                        (rect.x, rect.y + y),
                        (rect.x + rect.width, rect.y + y))

def create_crosshair(screen, pos, size=20, color=RED):
    """Draw crosshair at position"""
    x, y = pos
    pygame.draw.line(screen, color, (x - size, y), (x + size, y), 2)
    pygame.draw.line(screen, color, (x, y - size), (x, y + size), 2)
    pygame.draw.circle(screen, color, (x, y), size, 2)

def play_sound(sound_path, volume=0.7):
    """Play sound effect"""
    try:
        if SOUND_ENABLED:
            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(volume)
            sound.play()
    except:
        pass  # Ignore if sound file not found

def format_time(seconds):
    """Format seconds into MM:SS format"""
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02d}:{seconds:02d}"

def get_grade_color(score, max_score):
    """Get color based on score percentage"""
    percentage = (score / max_score) * 100
    if percentage >= 90:
        return GREEN
    elif percentage >= 80:
        return YELLOW
    elif percentage >= 70:
        return ORANGE
    else:
        return RED