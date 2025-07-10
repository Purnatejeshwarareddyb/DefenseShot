# Module 9: PDF + Quiz logic
# Enhanced Module 1: PDF + Quiz with Progress Tracking and Next Module Button
# module1.py code with database integration and progress unlocking

import pygame
import sys
import random
import os
import math
import json
import sqlite3
from datetime import datetime
import fitz  # PyMuPDF
import subprocess


# --- Database Setup and Functions ---
def init_database():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect('defense_training.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Modules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS modules (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            is_locked INTEGER DEFAULT 1,
            required_score INTEGER DEFAULT 80
        )
    ''')

    # User progress table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module_id INTEGER,
            score INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_unlocked INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (module_id) REFERENCES modules (id)
        )
    ''')

    # Quiz results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            module_id INTEGER,
            score INTEGER,
            total_questions INTEGER,
            time_taken INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (module_id) REFERENCES modules (id)
        )
    ''')

    # Insert default modules if they don't exist
    modules_data = [
        (1, "Defense Fundamentals", "Basic defense concepts and strategies", 0, 80),
        (2, "Advanced Tactics", "Advanced tactical operations", 1, 80),
        (3, "Strategic Planning", "Long-term strategic planning", 1, 80),
        (4, "Intelligence Analysis", "Intelligence gathering and analysis", 1, 80),
        (5, "Cyber Defense", "Cybersecurity and digital warfare", 1, 80),
    ]

    for module_data in modules_data:
        cursor.execute('''
            INSERT OR IGNORE INTO modules (id, name, description, is_locked, required_score)
            VALUES (?, ?, ?, ?, ?)
        ''', module_data)

    conn.commit()
    conn.close()


def save_quiz_result(user_id, module_id, score, total_questions, time_taken):
    """Save quiz result to database"""
    conn = sqlite3.connect('defense_training.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO quiz_results (user_id, module_id, score, total_questions, time_taken)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, module_id, score, total_questions, time_taken))

    conn.commit()
    conn.close()


def update_progress(user_id, module_id, score):
    """Update user progress for a module"""
    conn = sqlite3.connect('defense_training.db')
    cursor = conn.cursor()

    # Check if progress entry exists
    cursor.execute('''
        SELECT id FROM user_progress WHERE user_id = ? AND module_id = ?
    ''', (user_id, module_id))

    if cursor.fetchone():
        # Update existing progress
        cursor.execute('''
            UPDATE user_progress 
            SET score = ?, completed_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND module_id = ?
        ''', (score, user_id, module_id))
    else:
        # Insert new progress
        cursor.execute('''
            INSERT INTO user_progress (user_id, module_id, score, is_unlocked)
            VALUES (?, ?, ?, 1)
        ''', (user_id, module_id, score))

    conn.commit()
    conn.close()


def unlock_next_module(user_id, current_module_id):
    """Unlock the next module if current module is passed"""
    conn = sqlite3.connect('defense_training.db')
    cursor = conn.cursor()

    next_module_id = current_module_id + 1

    # Check if next module exists
    cursor.execute('SELECT id FROM modules WHERE id = ?', (next_module_id,))
    if cursor.fetchone():
        # Check if user already has progress for next module
        cursor.execute('''
            SELECT id FROM user_progress WHERE user_id = ? AND module_id = ?
        ''', (user_id, next_module_id))

        if cursor.fetchone():
            # Update existing entry
            cursor.execute('''
                UPDATE user_progress 
                SET is_unlocked = 1 
                WHERE user_id = ? AND module_id = ?
            ''', (user_id, next_module_id))
        else:
            # Create new entry
            cursor.execute('''
                INSERT INTO user_progress (user_id, module_id, score, is_unlocked)
                VALUES (?, ?, 0, 1)
            ''', (user_id, next_module_id))

    conn.commit()
    conn.close()


def get_logged_in_user_id():
    """Get the current logged-in user ID from session"""
    try:
        # Create user_data directory if it doesn't exist
        os.makedirs("user_data", exist_ok=True)

        # Check if session file exists
        session_file = "user_data/session.json"
        if os.path.exists(session_file):
            with open(session_file, "r") as f:
                session = json.load(f)
                return session.get("user_id", None)
        else:
            # Create a default session for testing
            default_session = {"user_id": 1, "username": "test_user"}
            with open(session_file, "w") as f:
                json.dump(default_session, f)
            return 1
    except Exception as e:
        print(f"Error reading session: {e}")
        return 1  # Default user ID for testing


def create_default_user():
    """Create a default user for testing if none exists"""
    conn = sqlite3.connect('defense_training.db')
    cursor = conn.cursor()

    # Check if any users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Create default user
        cursor.execute('''
            INSERT INTO users (username, password, email)
            VALUES (?, ?, ?)
        ''', ("test_user", "password123", "test@example.com"))
        conn.commit()

    conn.close()


def show_error_message(screen, title, message):
    """Show error message without disrupting main screen"""
    error_surface = pygame.Surface((400, 200))
    error_surface.fill((0, 0, 0))
    pygame.draw.rect(error_surface, (255, 0, 0), (0, 0, 400, 200), 2)

    error_font = pygame.font.Font(None, 24)
    title_text = error_font.render(title, True, (255, 0, 0))
    message_text = error_font.render(message, True, (255, 255, 255))

    error_surface.blit(title_text, (50, 50))
    error_surface.blit(message_text, (50, 100))

    # Blit to main screen
    screen.blit(error_surface, (screen.get_width() // 2 - 200, screen.get_height() // 2 - 100))
    pygame.display.flip()

    # Wait 2 seconds
    pygame.time.wait(2000)


def open_module_10():
    """Open module_2.py file with improved path handling"""

    # Try multiple possible paths
    possible_paths = [
        r"C:\Users\B.PURNA\PycharmProjects\DefenseShot\modules\module10.py",  # Original path
        os.path.join(os.path.dirname(__file__), "modules", "module10.py"),  # Relative to current file
        os.path.join(os.path.dirname(__file__), "module10.py"),  # Same directory
        "modules/module10.py",  # Relative path
        "module10.py"  # Current directory
    ]

    module2_path = None

    # Find the first existing path
    for path in possible_paths:
        if os.path.exists(path):
            module2_path = path
            break

    if module2_path:
        try:
            # Try to run the module_2.py file
            subprocess.Popen([sys.executable, module2_path])
            print(f"✅ Module 2 opened successfully from: {module2_path}")
            return True
        except Exception as e:
            print(f"❌ Error opening Module 2: {e}")
            return False
    else:
        print("❌ Module 2 file not found in any of these locations:")
        for path in possible_paths:
            print(f"   - {path}")

        # Show user-friendly error message
        show_error_message(pygame.display.get_surface(), "Module 2 file not found!", "Please check file path")
        return False


# --- DSA Implementations ---
class CommandTrie:
    def __init__(self):
        self.root = {}
        self.is_end = False

    def insert(self, command):
        node = self.root
        for char in command:
            if char not in node:
                node[char] = {}
            node = node[char]
        node['is_end'] = True

    def search(self, prefix):
        node = self.root
        for char in prefix:
            if char not in node:
                return []
            node = node[char]

        return self._get_all_words(node, prefix)

    def _get_all_words(self, node, prefix):
        words = []
        if 'is_end' in node:
            words.append(prefix)

        for char, child_node in node.items():
            if char != 'is_end':
                words.extend(self._get_all_words(child_node, prefix + char))

        return words


class PerformanceSegmentTree:
    def __init__(self, data):
        self.n = len(data)
        self.tree = [0] * (4 * self.n)
        self.build(data, 0, 0, self.n - 1)

    def build(self, data, node, start, end):
        if start == end:
            self.tree[node] = data[start]
        else:
            mid = (start + end) // 2
            self.build(data, 2 * node + 1, start, mid)
            self.build(data, 2 * node + 2, mid + 1, end)
            self.tree[node] = max(self.tree[2 * node + 1], self.tree[2 * node + 2])

    def query_max(self, node, start, end, l, r):
        if r < start or end < l:
            return float('-inf')
        if l <= start and end <= r:
            return self.tree[node]

        mid = (start + end) // 2
        left_max = self.query_max(2 * node + 1, start, mid, l, r)
        right_max = self.query_max(2 * node + 2, mid + 1, end, l, r)
        return max(left_max, right_max)

    def update(self, node, start, end, idx, val):
        if start == end:
            self.tree[node] = val
        else:
            mid = (start + end) // 2
            if idx <= mid:
                self.update(2 * node + 1, start, mid, idx, val)
            else:
                self.update(2 * node + 2, mid + 1, end, idx, val)
            self.tree[node] = max(self.tree[2 * node + 1], self.tree[2 * node + 2])


class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None


class AdvancedTreeOperations:
    def __init__(self):
        self.operations_count = 0

    def tree_traversal_with_conditions(self, root, condition_func):
        result = []

        def traverse(node):
            if not node:
                return

            if condition_func(node):
                result.append(node.value)

            traverse(node.left)
            traverse(node.right)

        traverse(root)
        return result

    def tree_restructure(self, root, restructure_rules):
        if not root:
            return None

        for rule in restructure_rules:
            if rule.condition(root):
                root = rule.apply(root)

        root.left = self.tree_restructure(root.left, restructure_rules)
        root.right = self.tree_restructure(root.right, restructure_rules)

        return root
# --- Button Class ---
class Button:
    def __init__(self, x, y, width, height, text, color, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font
        self.hover_color = tuple(min(255, c + 30) for c in color)
        self.is_hovered = False
        self.visible = True
        self.enabled = True
        self.glow_animation = 0

    def handle_event(self, event):
        if not self.visible or not self.enabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                return True
        elif event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)

        return False

    def update(self):
        if self.visible and self.enabled:
            self.glow_animation += 0.1
            if self.glow_animation > 2 * math.pi:
                self.glow_animation = 0

    def draw(self, surface):
        if not self.visible:
            return

        # Draw glow effect for enabled buttons
        if self.enabled:
            glow_intensity = int(20 + 15 * math.sin(self.glow_animation))
            glow_color = tuple(min(255, c + glow_intensity) for c in self.color)
            glow_rect = self.rect.inflate(6, 6)
            pygame.draw.rect(surface, glow_color, glow_rect, border_radius=8)

        # Draw main button
        current_color = self.hover_color if self.is_hovered else self.color
        if not self.enabled:
            current_color = tuple(c // 2 for c in current_color)

        pygame.draw.rect(surface, current_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=5)

        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)


# --- Pygame Initialization ---
pygame.init()
pygame.mixer.init()

# Display setup - MUST COME FIRST
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Elite Sniper Academy - Defense Training System")

# THEN load background image
try:
    background_image = pygame.image.load(R"C:\Users\B.PURNA\PycharmProjects\DefenseShot\assets\images\background2.jpg")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
except:
    print("Warning: Could not load background image - using fallback")
    # Create fallback background using the now-defined WIDTH and HEIGHT
    background_image = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(20 + (60 - 20) * color_ratio)
        g = int(30 + (80 - 30) * color_ratio)
        b = int(60 + (120 - 60) * color_ratio)
        pygame.draw.line(background_image, (r, g, b), (0, y), (WIDTH, y))

# Display setup
infoObject = pygame.display.Info()
WIDTH, HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Elite Sniper Academy - Defense Training System")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont('arial', 18)
font = pygame.font.SysFont('arial', 24)
font_medium = pygame.font.SysFont('arial', 28)
big_font = pygame.font.SysFont('arial', 36)
title_font = pygame.font.SysFont('arial', 48, bold=True)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)

# Game constants
CROSSHAIR_SIZE = 40
WIND_STRENGTH = 0
DIFFICULTY_LEVELS = {"Easy": 1.0, "Medium": 1.5, "Hard": 2.0, "Expert": 2.5}
PAGE_DISPLAY_TIME = 5  # seconds for PDF viewing

# Global variable to track if progress has been updated
progress_updated = False


# --- Core Classes ---
class Particle:
    def __init__(self, x, y, color, velocity, life_time=60):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.life_time = life_time
        self.max_life = life_time
        self.size = random.randint(2, 6)

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life_time -= 1
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] + 0.2)  # Gravity

    def draw(self, surface):
        if self.life_time > 0:
            alpha = int(255 * (self.life_time / self.max_life))
            color_with_alpha = (*self.color[:3], alpha)
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add_explosion(self, x, y, color=ORANGE):
        for _ in range(15):
            velocity = (random.uniform(-8, 8), random.uniform(-8, -2))
            self.particles.append(Particle(x, y, color, velocity, random.randint(30, 60)))

    def add_hit_effect(self, x, y):
        for _ in range(8):
            velocity = (random.uniform(-4, 4), random.uniform(-4, 4))
            self.particles.append(Particle(x, y, GREEN, velocity, 20))

    def update(self):
        self.particles = [p for p in self.particles if p.life_time > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


class Bullet:
    def __init__(self, x, y, wind_effect=0):
        self.start_x = x
        self.start_y = y
        self.x = x - 45
        self.y = y - 30
        self.vel_y = 15
        self.wind_effect = wind_effect
        self.trail = []
        self.active = True
        self.distance_traveled = 0

    def move(self):
        if self.y > -50:
            self.y -= self.vel_y
            self.x += self.wind_effect
            self.distance_traveled += self.vel_y
            self.trail.append((self.x + 45, self.y + 35))
            if len(self.trail) > 8:
                self.trail.pop(0)
        else:
            self.active = False

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            trail_color = (255, 255, 0, alpha)
            pygame.draw.circle(surface, (255, 255, 0), pos, max(1, 4 - i))
        pygame.draw.circle(surface, YELLOW, (int(self.x + 45), int(self.y + 35)), 6)
        pygame.draw.circle(surface, ORANGE, (int(self.x + 45), int(self.y + 35)), 3)


class Bottle:
    def __init__(self, label, x, y, correct=False, difficulty=1.0):
        self.label = label
        self.rect = pygame.Rect(x, y, 70, 120)
        self.base_vel = random.choice([-2, 2]) * difficulty
        self.vel = self.base_vel
        self.correct = correct
        self.hit_animation = 0
        self.rotation = 0
        self.scale = 1.0
        self.color = (139, 69, 19) if not correct else (0, 150, 0)
        self.bob_offset = random.random() * 6.28
        self.original_y = y

    def update(self):
        self.rect.x += self.vel
        if self.rect.left <= 50 or self.rect.right >= WIDTH - 50:
            self.vel = -self.vel * random.uniform(0.8, 1.2)
        self.bob_offset += 0.05
        self.rect.y = self.original_y + math.sin(self.bob_offset) * 8
        if self.hit_animation > 0:
            self.hit_animation -= 1
            self.scale = 1.0 + (self.hit_animation / 30.0) * 0.3
            self.rotation += 15

    def draw(self, surface):
        scaled_width = int(self.rect.width * self.scale)
        scaled_height = int(self.rect.height * self.scale)
        scaled_rect = pygame.Rect(
            self.rect.centerx - scaled_width // 2,
            self.rect.centery - scaled_height // 2,
            scaled_width,
            scaled_height
        )
        if self.correct:
            for i in range(3):
                glow_rect = scaled_rect.inflate(i * 4, i * 4)
                pygame.draw.ellipse(surface, (0, 255, 0, 100 - i * 30), glow_rect)
        pygame.draw.ellipse(surface, self.color, scaled_rect)
        pygame.draw.ellipse(surface, WHITE, scaled_rect, 3)
        text = font_small.render(self.label, True, WHITE)
        text_rect = text.get_rect(center=scaled_rect.center)
        surface.blit(text, text_rect)


class WindSystem:
    def __init__(self):
        self.strength = 0
        self.direction = 1
        self.change_timer = 0

    def update(self):
        self.change_timer += 1
        if self.change_timer > 180:
            self.strength = random.uniform(0, 3)
            self.direction = random.choice([-1, 1])
            self.change_timer = 0

    def get_effect(self):
        return self.strength * self.direction * 0.3

    def draw_indicator(self, surface):
        indicator_x = 50
        indicator_y = HEIGHT - 150
        pygame.draw.rect(surface, BLACK, (indicator_x - 5, indicator_y - 5, 110, 30))
        pygame.draw.rect(surface, WHITE, (indicator_x - 5, indicator_y - 5, 110, 30), 2)
        arrow_length = int(self.strength * 20)
        if self.strength > 0:
            start_x = indicator_x + 50
            end_x = start_x + (arrow_length * self.direction)
            pygame.draw.line(surface, CYAN, (start_x, indicator_y + 10), (end_x, indicator_y + 10), 3)
            if arrow_length > 5:
                pygame.draw.polygon(surface, CYAN, [
                    (end_x, indicator_y + 10),
                    (end_x - 5 * self.direction, indicator_y + 5),
                    (end_x - 5 * self.direction, indicator_y + 15)
                ])
        wind_text = font_small.render(f"Wind: {self.strength:.1f}", True, WHITE)
        surface.blit(wind_text, (indicator_x, indicator_y - 25))


class ScoreSystem:
    def __init__(self):
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.accuracy = []
        self.time_bonuses = 0
        self.total_shots = 0
        self.hits = 0

    def add_hit(self, time_taken, distance):
        self.hits += 1
        self.streak += 1
        self.max_streak = max(self.max_streak, self.streak)
        time_bonus = max(0, 50 - int(time_taken / 100))
        self.time_bonuses += time_bonus
        distance_bonus = int(distance / 10)
        streak_multiplier = min(self.streak * 0.1, 2.0)
        total_points = int((100 + time_bonus + distance_bonus) * (1 + streak_multiplier))
        self.score += total_points
        return total_points

    def add_miss(self):
        self.streak = 0
        self.total_shots += 1

    def get_accuracy(self):
        if self.total_shots == 0:
            return 0
        return (self.hits / (self.hits + self.total_shots)) * 100

    def draw_hud(self, surface):
        hud_y = 60
        score_text = font_medium.render(f"Score: {self.score:,}", True, YELLOW)
        surface.blit(score_text, (20, hud_y))
        streak_color = GREEN if self.streak > 2 else WHITE
        streak_text = font.render(f"Streak: {self.streak}", True, streak_color)
        surface.blit(streak_text, (20, hud_y + 35))
        accuracy = self.get_accuracy()
        acc_color = GREEN if accuracy > 80 else YELLOW if accuracy > 60 else RED
        acc_text = font.render(f"Accuracy: {accuracy:.1f}%", True, acc_color)
        surface.blit(acc_text, (20, hud_y + 70))


class PDFReader:
    def __init__(self, pdf_path):
        self.doc = fitz.open(pdf_path)
        self.total_pages = len(self.doc)
        self.current_page = 0
        self.page_surface = None
        self.page_timer = 0
        self.can_take_quiz = False
        self.flip_animation = 0
        self.scale = 1.0
        self.load_current_page()

    def load_current_page(self):
        page = self.doc.load_page(self.current_page)
        rect = page.rect
        scale = min((WIDTH * 0.8) / rect.width, (HEIGHT * 0.8) / rect.height)
        matrix = fitz.Matrix(scale, scale)
        pix = page.get_pixmap(matrix=matrix)
        mode = "RGB" if not pix.alpha else "RGBA"
        self.page_surface = pygame.image.frombuffer(pix.samples, (pix.width, pix.height), mode)
        self.page_timer = pygame.time.get_ticks()
        self.can_take_quiz = False
        self.flip_animation = 30

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.load_current_page()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_current_page()

    def update(self):
        if self.flip_animation > 0:
            self.flip_animation -= 1
            self.scale = 1.0 + (self.flip_animation / 30.0) * 0.2
        if not self.can_take_quiz:
            if (pygame.time.get_ticks() - self.page_timer) / 1000 >= PAGE_DISPLAY_TIME:
                self.can_take_quiz = True

    def draw(self, surface):
        if not self.page_surface:
            return

        scaled_w = int(self.page_surface.get_width() * self.scale)
        scaled_h = int(self.page_surface.get_height() * self.scale)
        rect = pygame.Rect((WIDTH - scaled_w) // 2, (HEIGHT - scaled_h) // 2, scaled_w, scaled_h)
        notebook = rect.inflate(60, 80)

        pygame.draw.rect(surface, (240, 240, 220), notebook)
        pygame.draw.rect(surface, DARK_GRAY, notebook, 5)
        for i in range(5):
            y = notebook.top + 50 + i * 40
            pygame.draw.circle(surface, GRAY, (notebook.left + 20, y), 8)
            pygame.draw.circle(surface, WHITE, (notebook.left + 20, y), 5)

        pygame.draw.rect(surface, GRAY, rect.move(3, 3))
        pygame.draw.rect(surface, WHITE, rect)
        pygame.draw.rect(surface, DARK_GRAY, rect, 2)

        if self.scale != 1.0:
            scaled = pygame.transform.scale(self.page_surface, (scaled_w, scaled_h))
            surface.blit(scaled, rect.topleft)
        else:
            surface.blit(self.page_surface, rect.topleft)

        txt = font.render(f"Page {self.current_page + 1} of {self.total_pages}", True, DARK_GRAY)
        surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.bottom + 10))
        self.draw_timer(surface)

    def draw_timer(self, surface):
        elapsed = (pygame.time.get_ticks() - self.page_timer) / 1000
        if not self.can_take_quiz:
            remaining = max(0, PAGE_DISPLAY_TIME - elapsed)
            timer_txt = font_medium.render(f"Reading... {remaining:.1f}s", True, RED)
            pygame.draw.rect(surface, BLACK, (WIDTH - 220, 20, 200, 40))
            pygame.draw.rect(surface, RED, (WIDTH - 220, 20, 200, 40), 2)
            surface.blit(timer_txt, (WIDTH - 210, 30))
            progress = elapsed / PAGE_DISPLAY_TIME
            pygame.draw.rect(surface, GRAY, (WIDTH - 210, 65, 180, 10))
            pygame.draw.rect(surface, YELLOW, (WIDTH - 210, 65, int(180 * progress), 10))
        else:
            msg = font_medium.render("Press Q to take quiz!", True, GREEN)
            pygame.draw.rect(surface, BLACK, (WIDTH - 240, 20, 220, 40))
            pygame.draw.rect(surface, GREEN, (WIDTH - 240, 20, 220, 40), 2)
            surface.blit(msg, (WIDTH - 230, 30))


# --- Game Data ---
questions = [
    {
        "question": "What is the theme for the Indian Air Force (IAF) in the current year, signifying its push towards self-reliance and 'Make in India'?",
        "options": ["A. 'Saksham, Sashakt, Atmanirbhar'", "B. 'Innovate, Integrate, Dominate'", "C. 'Strength, Security, Self-Reliance'", "D. 'Modernize, Mobilize, Master'"],
        "answer": "A",
        "difficulty": "Easy",
        "category": "Indian Air Force Initiative"
    },
    {
        "question": "Who is the Defence Minister of India, whose message is included in the compendium?",
        "options": ["A. Rajnath Singh", "B. Amit Shah", "C. Nirmala Sitharaman", "D. Subrahmanyam Jaishankar"],
        "answer": "A",
        "difficulty": "Easy",
        "category": "Leadership"
    },
    {
        "question": "What is the name of the new directorate formed at Air HQ with the aim of facilitating innovations in the IAF and increasing interaction with private industries?",
        "options": ["A. Directorate of Aerospace Design (DAD)", "B. Directorate of Indigenous Development (DID)", "C. Directorate of Air Force Modernization (DAM)", "D. Directorate of Strategic Partnerships (DSP)"],
        "answer": "A",
        "difficulty": "Medium",
        "category": "Organizational Structure"
    },
    {
        "question": "When was the message from the Defence Minister, Rajnath Singh, dated in the compendium?",
        "options": ["A. 06 Feb, 2025", "B. 15 Jan, 2024", "C. 22 Mar, 2023", "D. 01 Dec, 2022"],
        "answer": "A",
        "difficulty": "Medium",
        "category": "Document Information"
    },
    {
        "question": "Which of the following is NOT one of the classifications for projects mentioned in the 'Contents' section of the compendium?",
        "options": ["A. Naval Systems", "B. Weapon System", "C. Air Defence", "D. DefSpace/Satellite"],
        "answer": "A",
        "difficulty": "Medium",
        "category": "Project Classification"
    },
    {
        "question": "What are the three main sections into which the compendium is arranged for the ease of readers?",
        "options": ["A. Ongoing Projects, Open Projects, Future Opportunities", "B. Air Superiority, Ground Support, Naval Operations", "C. Design, Development, Deployment", "D. Challenges, Solutions, Partnerships"],
        "answer": "A",
        "difficulty": "Hard",
        "category": "Document Structure"
    },
    {
        "question": "What are the two locations where Regional Aerospace Innovation Divisions (RAIDs) have been established under DAD as dedicated industry outreach teams for IAF?",
        "options": ["A. Bangalore and Gandhinagar", "B. New Delhi and Mumbai", "C. Chennai and Kolkata", "D. Hyderabad and Pune"],
        "answer": "A",
        "difficulty": "Hard",
        "category": "Industry Outreach"
    },
    {
        "question": "The Defence Minister's message states that the endeavor of India, as a technologically advanced country, is to cover technological gaps in the journey towards what in Aerospace?",
        "options": ["A. Atmanirbharta", "B. Global Dominance", "C. Economic Prosperity", "D. Diplomatic Influence"],
        "answer": "A",
        "difficulty": "Medium",
        "category": "National Vision"
    },
    {
        "question": "The IAF Compendium of Challenges & Opportunities for Indian Industry is described as encapsulating what two main aspects?",
        "options": ["A. Strategic challenges and technological opportunities", "B. Historical achievements and future aspirations", "C. Financial investments and human resource development", "D. International collaborations and internal reforms"],
        "answer": "A",
        "difficulty": "Medium",
        "category": "Compendium Purpose"
    },
    {
        "question": "What does the preface state about the images used in the compendium?",
        "options": ["A. They are for representative purposes and intended only to introduce the challenge.", "B. They depict actual combat scenarios.", "C. They are blueprints for future aircraft.", "D. They are historical photographs of IAF operations."],
        "answer": "A",
        "difficulty": "Easy",
        "category": "Document Guidelines"
    }
]


# --- Game Functions ---
def create_background():
    background = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        color_ratio = y / HEIGHT
        r = int(20 + (60 - 20) * color_ratio)
        g = int(30 + (80 - 30) * color_ratio)
        b = int(60 + (120 - 60) * color_ratio)
        pygame.draw.line(background, (r, g, b), (0, y), (WIDTH, y))
    for _ in range(100):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT // 2)
        pygame.draw.circle(background, WHITE, (x, y), 1)
    return background


def draw_crosshair(surface, mouse_pos):
    x, y = mouse_pos
    time_offset = pygame.time.get_ticks() * 0.005
    breathing = math.sin(time_offset) * 2
    size = CROSSHAIR_SIZE + breathing
    pygame.draw.circle(surface, RED, (x, y), int(size), 2)
    pygame.draw.line(surface, RED, (x - size, y), (x + size, y), 2)
    pygame.draw.line(surface, RED, (x, y - size), (x, y + size), 2)
    # Center dot
    pygame.draw.circle(surface, YELLOW, (x, y), 3)


def draw_menu(surface):
    # Draw background first
    surface.blit(background_image, (0, 0))

    # Add semi-transparent overlay for readability
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Black with ~70% opacity
    surface.blit(overlay, (0, 0))

    # Rest of your existing menu drawing code...
    title_text = title_font.render("Elite Sniper Academy", True, YELLOW)
    subtitle_text = big_font.render("Defense Training Module 1", True, WHITE)

    surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    surface.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 4 + 80))

    # Menu options
    options = [
        "1. Read PDF Training Manual",
        "2. Take Quiz",
        "3. Practice Range",
        "4. DSA Visualizations",
        "5. Exit"
    ]

    for i, option in enumerate(options):
        option_text = font_medium.render(option, True, WHITE)
        surface.blit(option_text, (WIDTH // 2 - option_text.get_width() // 2, HEIGHT // 2 + i * 60))

def quiz_game():
    """Main quiz game function"""
    global progress_updated

    current_question = 0
    score = 0
    quiz_questions = random.sample(questions, 10)  # Select 10 random questions
    selected_answer = None
    show_result = False
    result_timer = 0
    start_time = pygame.time.get_ticks()
    user_id = get_logged_in_user_id()
    quiz_completed = False

    # Create Next Module button (initially hidden)
    next_module_button = Button(
        WIDTH // 2 - 150, HEIGHT - 150, 300, 60,
        "🎯 Open Next Module", (0, 150, 0), WHITE, font_medium
    )
    next_module_button.visible = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_1 and not show_result and not quiz_completed:
                    selected_answer = "A"
                elif event.key == pygame.K_2 and not show_result and not quiz_completed:
                    selected_answer = "B"
                elif event.key == pygame.K_3 and not show_result and not quiz_completed:
                    selected_answer = "C"
                elif event.key == pygame.K_4 and not show_result and not quiz_completed:
                    selected_answer = "D"
                elif event.key == pygame.K_RETURN and selected_answer and not show_result and not quiz_completed:
                    # Check answer
                    if selected_answer == quiz_questions[current_question]["answer"]:
                        score += 1
                    show_result = True
                    result_timer = pygame.time.get_ticks()
                elif event.key == pygame.K_SPACE and show_result and not quiz_completed:
                    # Next question
                    current_question += 1
                    if current_question >= len(quiz_questions):
                        # Quiz completed
                        quiz_completed = True
                        end_time = pygame.time.get_ticks()
                        time_taken = (end_time - start_time) // 1000

                        # Save results and update progress
                        save_quiz_result(user_id, 1, score, len(quiz_questions), time_taken)
                        update_progress(user_id, 1, score)

                        # Show Next Module button if score >= 8
                        if score >= 8:
                            next_module_button.visible = True
                            unlock_next_module(user_id, 1)

                        progress_updated = True
                    else:
                        selected_answer = None
                        show_result = False

            # Handle Next Module button click
            if next_module_button.handle_event(event):
                if open_module_10():
                    # Don't exit immediately, let user continue or choose to exit
                    print("Module 2 opened successfully!")
                    # Optional: You can add a small delay or message here
                    pygame.time.wait(1000)  # Wait 1 second to show the action worked

                else:
                    print("Failed to open Module 2")

        # Update button
        next_module_button.update()

        # Draw everything
        screen.blit(background_image, (0, 0))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        if not quiz_completed:
            # Draw current question
            question_data = quiz_questions[current_question]

            # Question number and category
            q_num_text = font_medium.render(f"Question {current_question + 1}/{len(quiz_questions)}", True, YELLOW)
            screen.blit(q_num_text, (50, 50))

            category_text = font.render(f"Category: {question_data['category']}", True, CYAN)
            screen.blit(category_text, (50, 90))

            difficulty_text = font.render(f"Difficulty: {question_data['difficulty']}", True, ORANGE)
            screen.blit(difficulty_text, (50, 120))

            # Question text
            question_text = font_medium.render(question_data["question"], True, WHITE)
            screen.blit(question_text, (50, 180))

            # Options
            for i, option in enumerate(question_data["options"]):
                color = WHITE
                if selected_answer == chr(65 + i):  # A, B, C, D
                    color = YELLOW

                option_text = font.render(f"{i + 1}. {option}", True, color)
                screen.blit(option_text, (50, 240 + i * 40))

            # Show result if answer was selected
            if show_result:
                correct_answer = question_data["answer"]
                if selected_answer == correct_answer:
                    result_text = font_medium.render("✅ Correct!", True, GREEN)
                else:
                    result_text = font_medium.render(f"❌ Wrong! Correct answer: {correct_answer}", True, RED)

                screen.blit(result_text, (50, 400))

                continue_text = font.render("Press SPACE to continue", True, WHITE)
                screen.blit(continue_text, (50, 450))
            else:
                # Instructions
                if selected_answer:
                    instruction_text = font.render("Press ENTER to submit answer", True, GREEN)
                else:
                    instruction_text = font.render("Press 1-4 to select answer", True, WHITE)
                screen.blit(instruction_text, (50, 400))

        else:
            # Quiz completed - show results

            # Title
            title_text = title_font.render("Quiz Completed!", True, YELLOW)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 100))

            # Score
            score_text = big_font.render(f"Score: {score}/10", True, WHITE)
            screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 200))

            # Performance message
            if score >= 8:
                performance_text = font_medium.render("🎉 Excellent! You can proceed to the next module!", True, GREEN)
                next_module_button.visible = True
            elif score >= 6:
                performance_text = font_medium.render("Good job! Keep practicing to improve.", True, YELLOW)
            else:
                performance_text = font_medium.render("Keep studying and try again!", True, RED)

            screen.blit(performance_text, (WIDTH // 2 - performance_text.get_width() // 2, 280))

            # Instructions
            instruction_text = font.render("Press ESC to return to menu", True, WHITE)
            screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, 350))

            # Draw Next Module button if visible
            next_module_button.draw(screen)

        # Current score display
        score_display = font.render(f"Current Score: {score}/{current_question + (1 if show_result else 0)}", True,
                                    WHITE)
        screen.blit(score_display, (WIDTH - 250, 50))

        pygame.display.flip()
        clock.tick(60)


def pdf_reader():
    """PDF reading function with Module 9 content"""
    try:
        pdf_path = r"C:\Users\B.PURNA\PycharmProjects\DefenseShot\study_materials\module_9.pdf"
        if not os.path.exists(pdf_path):
            # Display the Module 9 content directly if PDF doesn't exist
            screen.blit(background_image, (0, 0))

            # Module 9 title
            title_text = title_font.render("Module 9: Advanced Tree Structures", True, YELLOW)
            screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

            # DSA Topics
            topics_title = big_font.render("DSA Topics:", True, CYAN)
            screen.blit(topics_title, (100, 120))

            topics = [
                "• Trie: Command autocomplete, communication protocols",
                "• Segment Trees: Range-based analytics, performance metrics",
                "• Advanced Tree Operations: Complex data structure manipulations"
            ]

            for i, topic in enumerate(topics):
                topic_text = font.render(topic, True, WHITE)
                screen.blit(topic_text, (120, 170 + i * 40))

            # Purpose section
            purpose_title = big_font.render("Purpose:", True, CYAN)
            screen.blit(purpose_title, (100, 300))

            purposes = [
                "• Implement efficient communication systems",
                "• Perform complex range queries on performance data",
                "• Create sophisticated autocomplete systems"
            ]

            for i, purpose in enumerate(purposes):
                purpose_text = font.render(purpose, True, WHITE)
                screen.blit(purpose_text, (120, 350 + i * 40))

            # Implementation note
            impl_text = font.render("See code implementation for details...", True, YELLOW)
            screen.blit(impl_text, (WIDTH // 2 - impl_text.get_width() // 2, 500))

            # Instructions
            instruction_text = font.render("Press ESC to return to menu, Q for quiz", True, WHITE)
            screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT - 50))

            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "exit"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return "menu"
                        elif event.key == pygame.K_q:
                            return "quiz"
                clock.tick(60)
        else:
            # Original PDF reader code
            reader = PDFReader(pdf_path)
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "exit"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return "menu"
                        elif event.key == pygame.K_LEFT:
                            reader.previous_page()
                        elif event.key == pygame.K_RIGHT:
                            reader.next_page()
                        elif event.key == pygame.K_q and reader.can_take_quiz:
                            return "quiz"

                reader.update()
                screen.blit(background_image, (0, 0))
                reader.draw(screen)
                pygame.display.flip()
                clock.tick(60)

    except Exception as e:
        print(f"Error in PDF reader: {e}")
        return "menu"

def practice_range():
    """Practice shooting range"""
    particles = ParticleSystem()
    wind_system = WindSystem()
    score_system = ScoreSystem()

    bullets = []
    bottles = []

    # Create bottles
    for i in range(8):
        x = random.randint(100, WIDTH - 170)
        y = random.randint(100, HEIGHT - 250)
        label = random.choice(["Enemy", "Friendly", "Civilian", "Target"])
        correct = label == "Enemy"
        bottles.append(Bottle(label, x, y, correct))

    background = background_image  # Use the loaded image

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    wind_effect = wind_system.get_effect()
                    bullets.append(Bullet(mouse_pos[0], mouse_pos[1], wind_effect))
                    score_system.total_shots += 1

        # Update systems
        wind_system.update()
        particles.update()

        # Update bullets
        for bullet in bullets[:]:
            bullet.move()
            if not bullet.active:
                bullets.remove(bullet)
                score_system.add_miss()
            else:
                # Check collision with bottles
                for bottle in bottles[:]:
                    if bottle.rect.colliderect(pygame.Rect(bullet.x + 40, bullet.y + 30, 10, 10)):
                        if bottle.correct:
                            points = score_system.add_hit(pygame.time.get_ticks(), bullet.distance_traveled)
                            particles.add_hit_effect(bottle.rect.centerx, bottle.rect.centery)
                        else:
                            score_system.add_miss()
                            particles.add_explosion(bottle.rect.centerx, bottle.rect.centery, RED)

                        bottles.remove(bottle)
                        bullets.remove(bullet)

                        # Add new bottle
                        x = random.randint(100, WIDTH - 170)
                        y = random.randint(100, HEIGHT - 250)
                        label = random.choice(["Enemy", "Friendly", "Civilian", "Target"])
                        correct = label == "Enemy"
                        bottles.append(Bottle(label, x, y, correct))
                        break

        # Update bottles
        for bottle in bottles:
            bottle.update()

        # Draw everything
        screen.blit(background, (0, 0))

        # Draw bottles
        for bottle in bottles:
            bottle.draw(screen)

        # Draw bullets
        for bullet in bullets:
            bullet.draw(screen)

        # Draw particles
        particles.draw(screen)

        # Draw UI
        wind_system.draw_indicator(screen)
        score_system.draw_hud(screen)

        # Draw crosshair
        draw_crosshair(screen, pygame.mouse.get_pos())

        # Instructions
        instruction_text = font.render("Left click to shoot, ESC to return", True, WHITE)
        screen.blit(instruction_text, (20, HEIGHT - 40))

        pygame.display.flip()
        clock.tick(60)


def dsa_visualizations():
    """Show DSA visualizations menu"""
    trie = CommandTrie()
    # Insert some military commands
    commands = ["attack", "defend", "retreat", "recon", "surveillance", "extract", "engage", "hold"]
    for cmd in commands:
        trie.insert(cmd)

    # Sample data for segment tree
    performance_data = [random.randint(50, 100) for _ in range(16)]
    segment_tree = PerformanceSegmentTree(performance_data)

    # Create a sample tree for advanced operations
    root = TreeNode("Command")
    root.left = TreeNode("Attack")
    root.right = TreeNode("Defend")
    root.left.left = TreeNode("Flank")
    root.left.right = TreeNode("Ambush")
    root.right.left = TreeNode("Fortify")
    root.right.right = TreeNode("Retreat")

    advanced_ops = AdvancedTreeOperations()

    # Buttons for each visualization
    trie_button = Button(WIDTH // 2 - 200, 200, 400, 50, "Trie: Command Autocomplete", BLUE, WHITE, font_medium)
    segment_button = Button(WIDTH // 2 - 200, 300, 400, 50, "Segment Tree: Performance Analytics", GREEN, WHITE,
                            font_medium)
    tree_button = Button(WIDTH // 2 - 200, 400, 400, 50, "Advanced Tree Operations", PURPLE, WHITE, font_medium)
    back_button = Button(WIDTH // 2 - 100, 500, 200, 50, "Back to Menu", RED, WHITE, font_medium)

    current_visualization = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"

            if trie_button.handle_event(event):
                current_visualization = "trie"
            elif segment_button.handle_event(event):
                current_visualization = "segment"
            elif tree_button.handle_event(event):
                current_visualization = "tree"
            elif back_button.handle_event(event):
                return "menu"

        screen.blit(background_image, (0, 0))

        # Title
        title = title_font.render("DSA Visualizations", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        # Draw buttons
        trie_button.draw(screen)
        segment_button.draw(screen)
        tree_button.draw(screen)
        back_button.draw(screen)

        # Draw visualizations
        if current_visualization == "trie":
            draw_trie_visualization(screen, trie)
        elif current_visualization == "segment":
            draw_segment_tree_visualization(screen, segment_tree, performance_data)
        elif current_visualization == "tree":
            draw_tree_visualization(screen, root, advanced_ops)

        pygame.display.flip()
        clock.tick(60)


def draw_trie_visualization(surface, trie):
    """Draw Trie visualization"""
    # Draw title
    title = font_medium.render("Command Autocomplete System", True, CYAN)
    surface.blit(title, (50, 100))

    # Draw search box
    pygame.draw.rect(surface, WHITE, (50, 150, 300, 40), 2)

    # Draw sample autocomplete
    prefix = "a"  # Example prefix
    results = trie.search(prefix)
    results_text = font.render(f"Commands starting with '{prefix}': {', '.join(results)}", True, YELLOW)
    surface.blit(results_text, (50, 200))

    # Draw trie structure (simplified)
    y_offset = 250
    for i, (char, node) in enumerate(trie.root.items()):
        if char != 'is_end':
            node_text = font.render(f"Node: {char}", True, WHITE)
            surface.blit(node_text, (50, y_offset + i * 30))
            if 'is_end' in node:
                end_text = font.render("(end)", True, GREEN)
                surface.blit(end_text, (150, y_offset + i * 30))


def draw_segment_tree_visualization(surface, segment_tree, data):
    """Draw Segment Tree visualization"""
    # Draw title
    title = font_medium.render("Performance Analytics", True, CYAN)
    surface.blit(title, (50, 100))

    # Draw data
    data_text = font.render(f"Performance Data: {data}", True, WHITE)
    surface.blit(data_text, (50, 150))

    # Draw query example
    l, r = 3, 10
    max_val = segment_tree.query_max(0, 0, segment_tree.n - 1, l, r)
    query_text = font.render(f"Max between indices {l}-{r}: {max_val}", True, YELLOW)
    surface.blit(query_text, (50, 200))

    # Draw tree visualization (simplified)
    tree_text = font.render("Segment Tree Structure (simplified):", True, WHITE)
    surface.blit(tree_text, (50, 250))

    for i in range(min(5, len(segment_tree.tree))):
        node_text = font.render(f"Node {i}: {segment_tree.tree[i]}", True, WHITE)
        surface.blit(node_text, (70, 290 + i * 30))


def draw_tree_visualization(surface, root, advanced_ops):
    """Draw Tree visualization"""
    # Draw title
    title = font_medium.render("Command Decision Tree", True, CYAN)
    surface.blit(title, (50, 100))

    # Draw tree structure
    def draw_node(node, x, y, dx):
        if not node:
            return

        # Draw node
        pygame.draw.circle(surface, PURPLE, (x, y), 20)
        node_text = font_small.render(node.value[:4], True, WHITE)
        surface.blit(node_text, (x - 15, y - 10))

        # Draw connections to children
        if node.left:
            pygame.draw.line(surface, WHITE, (x, y + 20), (x - dx, y + 70), 2)
            draw_node(node.left, x - dx, y + 80, dx // 2)
        if node.right:
            pygame.draw.line(surface, WHITE, (x, y + 20), (x + dx, y + 70), 2)
            draw_node(node.right, x + dx, y + 80, dx // 2)

    draw_node(root, WIDTH // 2, 150, 150)

    # Example operation
    condition = lambda node: len(node.value) > 5
    result = advanced_ops.tree_traversal_with_conditions(root, condition)
    op_text = font.render(f"Nodes with long names: {result}", True, YELLOW)
    surface.blit(op_text, (50, 400))


def main():
    """Main game loop"""
    global progress_updated

    # Initialize database and create default user
    init_database()
    create_default_user()

    current_state = "menu"

    while True:
        if current_state == "menu":
            # Draw menu
            draw_menu(screen)
            pygame.display.flip()

            # Handle menu input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        current_state = "pdf"
                    elif event.key == pygame.K_2:
                        current_state = "quiz"
                    elif event.key == pygame.K_3:
                        current_state = "practice"
                    elif event.key == pygame.K_4:  # New option
                        current_state = "dsa"
                    elif event.key == pygame.K_5:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

        elif current_state == "pdf":
            result = pdf_reader()
            if result == "exit":
                pygame.quit()
                sys.exit()
            elif result == "quiz":
                current_state = "quiz"
            else:
                current_state = "menu"

        elif current_state == "quiz":
            result = quiz_game()
            if result == "exit":
                pygame.quit()
                sys.exit()
            else:
                current_state = "menu"

        elif current_state == "practice":
            result = practice_range()
            if result == "exit":
                pygame.quit()
                sys.exit()
            else:
                current_state = "menu"

        elif current_state == "dsa":
            result = dsa_visualizations()
            if result == "exit":
                pygame.quit()
                sys.exit()
            else:
                current_state = "menu"

        clock.tick(60)

if __name__ == "__main__":
    main()