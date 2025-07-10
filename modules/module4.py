# Enhanced Module 4: PDF + Quiz with Progress Tracking and Next Module Button
# module4.py code with database integration and progress unlocking

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


def open_module_5():
    """Open module_2.py file with improved path handling"""

    # Try multiple possible paths
    possible_paths = [
        r"C:\Users\B.PURNA\PycharmProjects\DefenseShot\modules\module5.py",  # Original path
        os.path.join(os.path.dirname(__file__), "modules", "module5.py"),  # Relative to current file
        os.path.join(os.path.dirname(__file__), "module5.py"),  # Same directory
        "modules/module5.py",  # Relative path
        "module5.py"  # Current directory
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
            print(f"✅ Module 5 opened successfully from: {module2_path}")
            return True
        except Exception as e:
            print(f"❌ Error opening Module 2: {e}")
            return False
    else:
        print("❌ Module 5 file not found in any of these locations:")
        for path in possible_paths:
            print(f"   - {path}")

        # Show user-friendly error message
        show_error_message(pygame.display.get_surface(), "Module 2 file not found!", "Please check file path")
        return False


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
    background_image = pygame.image.load(R"C:\Users\B.PURNA\PycharmProjects\DefenseShot\assets\images\background4.jpg")
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
        "question": "What was the primary cause of the First India-Pakistan War of 1947-48?",
        "options": ["A. Economic disputes over trade routes", "B. Religious conflicts in Punjab", "C. Border skirmishes in Gujarat", "D. The Maharaja of J&K's indecision on joining India or Pakistan"],
        "answer": "D",
        "difficulty": "Easy",
        "category": "Historical Context"
    },
    {
        "question": "How was the Indian Military divided between India and Pakistan after the partition?",
        "options": ["A. Equally between the two nations", "B. 3/4th to India, 1/4th to Pakistan", "C. 1/2 to India, 1/2 to Pakistan", "D. 2/3rd to India, 1/3rd to Pakistan"],
        "answer": "D",
        "difficulty": "Easy",
        "category": "Military Division"
    },
    {
        "question": "Which princely states required military intervention to be integrated into India after independence?",
        "options": ["A. Mysore, Travancore, and Bhopal", "B. Gwalior, Baroda, and Indore", "C. Patiala, Jodhpur, and Bikaner", "D. Hyderabad, Jammu & Kashmir, and Junagadh"],
        "answer": "D",
        "difficulty": "Medium",
        "category": "Princely States"
    },
    {
        "question": "What was the outcome of the UN Security Council's Resolution 47 passed on 21 April 1948?",
        "options": ["A. It was accepted by both India and Pakistan", "B. It led to an immediate ceasefire", "C. It was rejected by India", "D. It was rejected by Pakistan"],
        "answer": "D",
        "difficulty": "Medium",
        "category": "International Diplomacy"
    },
    {
        "question": "What was the key Pakistani strategy in Operation Gibraltar during the 1965 India-Pakistan War?",
        "options": ["A. Launching a full-scale tank assault", "B. Conducting airstrikes on Indian cities", "C. Blocking Indian supply routes", "D. Sending soldiers disguised as Kashmiris to create panic"],
        "answer": "D",
        "difficulty": "Medium",
        "category": "Military Strategy"
    },
    {
        "question": "Which Indian military unit was involved in the historic link-up at Tangail during the 1971 India-Pakistan War?",
        "options": ["A. 4 Grenadiers", "B. 163 Infantry Brigade", "C. 33 Corps", "D. 1 MARATHA LI and 2 PARA (MARATHA)"],
        "answer": "D",
        "difficulty": "Hard",
        "category": "Military Operations"
    },
    {
        "question": "What was the primary reason Pakistan launched Operation Badr during the Kargil War of 1999?",
        "options": ["A. To capture Siachen Glacier", "B. To disrupt Indian trade routes", "C. To gain control of Srinagar", "D. To sever the link between Kashmir and Ladakh"],
        "answer": "D",
        "difficulty": "Hard",
        "category": "Kargil War"
    },
    {
        "question": "Why did India refrain from crossing the Line of Control (LOC) during the Kargil War?",
        "options": ["A. Lack of military resources", "B. Pressure from the United States", "C. Fear of nuclear retaliation", "D. To avoid escalating the conflict and losing international support"],
        "answer": "D",
        "difficulty": "Hard",
        "category": "Strategic Decisions"
    },
    {
        "question": "What was a significant contributing factor to the India-China War of 1962?",
        "options": ["A. China's opposition to India's nuclear program", "B. India's support for Mongolian independence", "C. Economic rivalry over Himalayan trade routes", "D. India's asylum to the Dalai Lama and border disputes"],
        "answer": "D",
        "difficulty": "Medium",
        "category": "India-China Relations"
    },
    {
        "question": "Which operation marked India's first and only amphibious landing during the 1971 India-Pakistan War?",
        "options": ["A. Operation Vijay", "B. Operation Polo", "C. Operation Trident", "D. The landing at Cox's Bazar"],
        "answer": "D",
        "difficulty": "Hard",
        "category": "Naval Operations"
    }
]










# DFS for complete reconnaissance
def deep_reconnaissance(graph, start_territory):
    visited = set()
    intel_gathered = []

    def dfs(territory):
        if territory in visited:
            return
        visited.add(territory)
        intel_gathered.append(territory)

        for neighbor, distance in graph.connections.get(territory, []):
            dfs(neighbor)

    dfs(start_territory)
    return intel_gathered


# BFS for shortest path finding
def find_shortest_route(graph, start, destination):
    from collections import deque
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current, path = queue.popleft()
        if current == destination:
            return path

        if current in visited:
            continue
        visited.add(current)

        for neighbor, distance in graph.connections.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return None

# --- Graph Algorithms Content ---
class TerritoryMap:
    def __init__(self):
        self.territories = {}
        self.connections = {}

    def add_territory(self, name, strategic_value, coordinates):
        self.territories[name] = {
            'value': strategic_value,
            'coordinates': coordinates,
            'controlled': False
        }

    def add_connection(self, territory1, territory2, distance):
        if territory1 not in self.connections:
            self.connections[territory1] = []
        self.connections[territory1].append((territory2, distance))


def graph_practice():
    """Practice graph algorithm concepts"""
    # Create a sample territory map
    territory_map = TerritoryMap()
    territory_map.add_territory("Base", 100, (100, 100))
    territory_map.add_territory("Outpost", 50, (300, 150))
    territory_map.add_territory("Enemy Camp", -75, (500, 200))
    territory_map.add_territory("Resource Depot", 80, (200, 300))
    territory_map.add_territory("Observation Point", 30, (400, 300))
    territory_map.add_territory("Supply Cache", 60, (600, 100))

    territory_map.add_connection("Base", "Outpost", 50)
    territory_map.add_connection("Outpost", "Enemy Camp", 70)
    territory_map.add_connection("Base", "Resource Depot", 60)
    territory_map.add_connection("Resource Depot", "Enemy Camp", 90)
    territory_map.add_connection("Outpost", "Observation Point", 40)
    territory_map.add_connection("Enemy Camp", "Supply Cache", 110)
    territory_map.add_connection("Observation Point", "Supply Cache", 80)

    current_mode = "view"  # view, dfs, bfs
    start_node = None
    end_node = None
    result_nodes = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_d:
                    current_mode = "dfs"
                    start_node = None
                    result_nodes = []
                elif event.key == pygame.K_b:
                    current_mode = "bfs"
                    start_node = None
                    end_node = None
                    result_nodes = []
                elif event.key == pygame.K_v:
                    current_mode = "view"
                elif event.key == pygame.K_r:
                    # Reset selections
                    start_node = None
                    end_node = None
                    result_nodes = []

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    # Check if clicked on a territory
                    for name, data in territory_map.territories.items():
                        x, y = data['coordinates']
                        if math.sqrt((x - mouse_pos[0]) ** 2 + (y - mouse_pos[1]) ** 2) < 20:
                            if current_mode == "dfs":
                                if not start_node:
                                    start_node = name
                                    result_nodes = deep_reconnaissance(territory_map, start_node)
                            elif current_mode == "bfs":
                                if not start_node:
                                    start_node = name
                                elif not end_node and name != start_node:
                                    end_node = name
                                    result_nodes = find_shortest_route(territory_map, start_node, end_node)
                            break

        # Draw everything
        screen.blit(background_image, (0, 0))

        # Draw connections
        for territory, connections in territory_map.connections.items():
            x1, y1 = territory_map.territories[territory]['coordinates']
            for neighbor, distance in connections:
                x2, y2 = territory_map.territories[neighbor]['coordinates']
                pygame.draw.line(screen, GRAY, (x1, y1), (x2, y2), 2)
                # Draw distance
                mid_x = (x1 + x2) // 2
                mid_y = (y1 + y2) // 2
                dist_text = font_small.render(str(distance), True, WHITE)
                screen.blit(dist_text, (mid_x, mid_y))

        # Draw territories
        for name, data in territory_map.territories.items():
            x, y = data['coordinates']
            color = GREEN if data['controlled'] else RED if data['value'] < 0 else BLUE
            pygame.draw.circle(screen, color, (x, y), 20)
            name_text = font_small.render(name, True, WHITE)
            screen.blit(name_text, (x - name_text.get_width() // 2, y - 30))
            value_text = font_small.render(str(data['value']), True, WHITE)
            screen.blit(value_text, (x - value_text.get_width() // 2, y + 25))

        # Highlight result nodes
        for name in result_nodes:
            x, y = territory_map.territories[name]['coordinates']
            pygame.draw.circle(screen, YELLOW, (x, y), 25, 3)
            if current_mode == "bfs" and name in [start_node, end_node]:
                pygame.draw.circle(screen, ORANGE, (x, y), 30, 3)

        # Draw mode information
        mode_text = font_medium.render(f"Mode: {current_mode.upper()}", True, WHITE)
        screen.blit(mode_text, (20, 20))

        if current_mode == "dfs":
            instruction = "Select start territory (D for DFS mode)"
            if start_node:
                instruction = f"DFS from {start_node}: {', '.join(result_nodes)}"
        elif current_mode == "bfs":
            instruction = "Select start and end territories (B for BFS mode)"
            if start_node and end_node:
                instruction = f"Shortest path from {start_node} to {end_node}: {' -> '.join(result_nodes)}"
            elif start_node:
                instruction = f"Start: {start_node}, select destination"
        else:
            instruction = "View mode (V to view, D for DFS, B for BFS)"

        instr_text = font.render(instruction, True, WHITE)
        screen.blit(instr_text, (20, 60))

        help_text = font.render("ESC: Menu | R: Reset | Click territories to select", True, GRAY)
        screen.blit(help_text, (WIDTH - 450, HEIGHT - 40))

        # Draw legend
        legend_y = HEIGHT - 150
        pygame.draw.rect(screen, DARK_GRAY, (20, legend_y - 20, 250, 130))
        pygame.draw.rect(screen, WHITE, (20, legend_y - 20, 250, 130), 2)
        legend_title = font_small.render("Territory Legend:", True, WHITE)
        screen.blit(legend_title, (30, legend_y))

        pygame.draw.circle(screen, BLUE, (40, legend_y + 30), 10)
        ally_text = font_small.render("= Ally Territory", True, WHITE)
        screen.blit(ally_text, (60, legend_y + 25))

        pygame.draw.circle(screen, RED, (40, legend_y + 60), 10)
        enemy_text = font_small.render("= Enemy Territory", True, WHITE)
        screen.blit(enemy_text, (60, legend_y + 55))

        pygame.draw.circle(screen, YELLOW, (40, legend_y + 90), 10, 2)
        result_text = font_small.render("= Algorithm Result", True, WHITE)
        screen.blit(result_text, (60, legend_y + 85))

        pygame.display.flip()
        clock.tick(60)# DFS for complete reconnaissance
def deep_reconnaissance(graph, start_territory):
    visited = set()
    intel_gathered = []

    def dfs(territory):
        if territory in visited:
            return
        visited.add(territory)
        intel_gathered.append(territory)

        for neighbor, distance in graph.connections.get(territory, []):
            dfs(neighbor)

    dfs(start_territory)
    return intel_gathered


# BFS for shortest path finding
def find_shortest_route(graph, start, destination):
    from collections import deque
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current, path = queue.popleft()
        if current == destination:
            return path

        if current in visited:
            continue
        visited.add(current)

        for neighbor, distance in graph.connections.get(current, []):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))

    return None


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
    subtitle_text = big_font.render("Defense Training Module 4", True, WHITE)

    surface.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 4))
    surface.blit(subtitle_text, (WIDTH // 2 - subtitle_text.get_width() // 2, HEIGHT // 4 + 80))

    # Menu options
    options = [
        "1. Read PDF Training Manual",
        "2. Take Quiz",
        "3. Practice Range",
        "4. Graph Algorithm Practice",
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
                if open_module_5():
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
    """PDF reading function"""
    try:
        pdf_path = r"C:\Users\B.PURNA\PycharmProjects\DefenseShot\study_materials\module_4.pdf"  # Make sure this file exists
        if not os.path.exists(pdf_path):
            # Create a simple text message if PDF doesn't exist
            screen.blit(background_image, (0, 0))
            error_text = font_medium.render("PDF file 'defense_manual.pdf' not found!", True, RED)
            instruction_text = font.render("Please place the PDF file in the same directory as this script", True,
                                           WHITE)
            back_text = font.render("Press ESC to return to menu", True, WHITE)

            screen.blit(error_text, (WIDTH // 2 - error_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, HEIGHT // 2))
            screen.blit(back_text, (WIDTH // 2 - back_text.get_width() // 2, HEIGHT // 2 + 50))

            pygame.display.flip()

            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "exit"
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            return "menu"

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

            # Instructions
            instruction_text = font.render("Use LEFT/RIGHT arrows to navigate, ESC to return", True, WHITE)
            screen.blit(instruction_text, (20, HEIGHT - 40))

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
                    elif event.key == pygame.K_4:
                        current_state = "graph_practice"
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

        elif current_state == "graph_practice":
            result = graph_practice()
            if result == "exit":
                pygame.quit()
                sys.exit()
            else:
                current_state = "menu"

        clock.tick(60)

if __name__ == "__main__":
    main()