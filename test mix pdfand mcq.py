#module1.py code
import pygame
import sys
import random
import os
import math
import json
from datetime import datetime
import fitz  # PyMuPDF

# --- Initialization ---
pygame.init()
pygame.mixer.init()

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
        "question": "What is the primary focus of 'The Art of War'?",
        "options": ["A. Building fortifications", "B. Strategy and conflict resolution", "C. Weapon development", "D. Naval warfare"],
        "answer": "B",
        "difficulty": "Easy",
        "category": "Fundamentals"
    },
    {
        "question": "According to Sun Tzu, what is the best way to win a battle?",
        "options": ["A. Using superior numbers", "B. Winning without fighting", "C. Developing advanced weapons", "D. Long sieges"],
        "answer": "B",
        "difficulty": "Easy",
        "category": "Strategy"
    },
    {
        "question": "Which of the following is NOT one of the five things to assess before battle according to Sun Tzu?",
        "options": ["A. The Way", "B. The weather", "C. The terrain", "D. The enemy's weaponry"],
        "answer": "D",
        "difficulty": "Medium",
        "category": "Assessment"
    },
    {
        "question": "What does Sun Tzu say about deception in warfare?",
        "options": ["A. It should never be used", "B. It is essential to military operations", "C. It only works against weak enemies", "D. It is dishonorable"],
        "answer": "B",
        "difficulty": "Medium",
        "category": "Tactics"
    },
    {
        "question": "According to Sun Tzu, what should you do when facing a stronger enemy?",
        "options": ["A. Attack immediately", "B. Avoid them if possible", "C. Surrender", "D. Request reinforcements"],
        "answer": "B",
        "difficulty": "Medium",
        "category": "Strategy"
    },
    {
        "question": "What does Sun Tzu compare military formation to in Chapter 6?",
        "options": ["A. A mountain", "B. Water", "C. Fire", "D. Wind"],
        "answer": "B",
        "difficulty": "Hard",
        "category": "Formations"
    },
    {
        "question": "Which of these is considered one of the five dangerous traits in generals according to Sun Tzu?",
        "options": ["A. Being too cautious", "B. Being ready to die", "C. Being too intelligent", "D. Being too wealthy"],
        "answer": "B",
        "difficulty": "Hard",
        "category": "Leadership"
    },
    {
        "question": "What does Sun Tzu say about surrounding an enemy army?",
        "options": ["A. Always leave them an escape route", "B. Completely encircle them", "C. Never surround them", "D. Only surround weaker armies"],
        "answer": "A",
        "difficulty": "Hard",
        "category": "Tactics"
    },
    {
        "question": "According to Sun Tzu, what should you do when on 'deadly ground'?",
        "options": ["A. Retreat immediately", "B. Fight", "C. Negotiate", "D. Surrender"],
        "answer": "B",
        "difficulty": "Hard",
        "category": "Terrain"
    },
    {
        "question": "What does Sun Tzu mean by 'the unorthodox and the orthodox give rise to each other'?",
        "options": ["A. They should never be mixed", "B. They are interchangeable tactics", "C. Only orthodox methods work", "D. Unorthodox methods are superior"],
        "answer": "B",
        "difficulty": "Hard",
        "category": "Strategy"
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
    pygame.draw.circle(surface, RED, (x, y), 3)
    pygame.draw.line(surface, RED, (x - size // 2, y), (x + size // 2, y), 2)
    pygame.draw.line(surface, RED, (x, y - size // 2), (x, y + size // 2), 2)


def show_question(surface, question_data, timer):
    question_text = question_data['question']
    category = question_data.get('category', 'General')
    difficulty = question_data.get('difficulty', 'Medium')

    panel_height = 120
    panel = pygame.Surface((WIDTH - 40, panel_height), pygame.SRCALPHA)
    panel.fill((0, 0, 0, 180))
    surface.blit(panel, (20, 10))

    cat_text = font_small.render(f"Category: {category} | Difficulty: {difficulty}", True, CYAN)
    surface.blit(cat_text, (30, 20))

    time_left = max(0, 30 - timer // 60)
    timer_color = RED if time_left < 10 else YELLOW if time_left < 20 else GREEN
    timer_text = font_medium.render(f"Time: {time_left}s", True, timer_color)
    surface.blit(timer_text, (WIDTH - 150, 20))

    words = question_text.split()
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        if font_medium.size(test_line)[0] > WIDTH - 100:
            if len(current_line) > 1:
                current_line.pop()
                lines.append(' '.join(current_line))
                current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    for i, line in enumerate(lines):
        text_surface = font_medium.render(line, True, WHITE)
        surface.blit(text_surface, (30, 50 + i * 30))


def show_main_menu(surface):
    surface.fill(BLACK)
    title_text = title_font.render("ELITE SNIPER ACADEMY", True, YELLOW)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))

    for offset in range(5, 0, -1):
        glow_surface = title_font.render("ELITE SNIPER ACADEMY", True, (255, 255, 0, 50))
        surface.blit(glow_surface, (title_rect.x - offset, title_rect.y - offset))

    surface.blit(title_text, title_rect)

    subtitle = big_font.render("Defense Knowledge Training System", True, WHITE)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, HEIGHT // 4 + 80))
    surface.blit(subtitle, subtitle_rect)

    instructions = [
        "1. Study the defense materials (PDF Viewer)",
        "2. Test your knowledge with the interactive quiz",
        "3. Earn points by answering quickly and accurately",
        "",
        "SPACE - Shoot | ESC - Exit | ENTER - Start"
    ]

    for i, instruction in enumerate(instructions):
        color = CYAN if instruction.startswith(("1.", "2.", "3.")) else WHITE
        text = font.render(instruction, True, color)
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + i * 30))
        surface.blit(text, text_rect)


def run_quiz():
    particle_system = ParticleSystem()
    wind_system = WindSystem()
    score_system = ScoreSystem()
    background = create_background()

    game_state = "menu"
    q_index = 0
    question_timer = 0
    bullets = []
    bottles = []
    result = ""
    result_timer = 0
    current_difficulty = "Medium"
    difficulty_multiplier = DIFFICULTY_LEVELS[current_difficulty]

    pygame.mouse.set_visible(False)

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_state == "menu":
                        running = False
                        break
                    else:
                        game_state = "menu"

                elif event.key == pygame.K_RETURN:
                    if game_state == "menu":
                        game_state = "playing"
                        q_index = 0
                        score_system = ScoreSystem()
                        bottles = []
                        bullets = []
                        question_timer = 0
                        result = ""
                    elif game_state == "results":
                        game_state = "menu"

                elif event.key == pygame.K_SPACE and game_state == "playing":
                    wind_effect = wind_system.get_effect()
                    bullets.append(Bullet(mouse_pos[0], mouse_pos[1], wind_effect))
                    score_system.total_shots += 1

        if game_state == "menu":
            show_main_menu(screen)

        elif game_state == "playing":
            if q_index >= len(questions):
                game_state = "results"
                continue

            if not bottles:
                question = questions[q_index]
                options = question['options']
                bottles = []
                spacing = WIDTH // 5
                x = spacing

                for opt in options:
                    is_correct = opt.startswith(question['answer'])
                    bottles.append(
                        Bottle(opt, x, HEIGHT // 2 - 60, correct=is_correct, difficulty=difficulty_multiplier))
                    x += spacing

                question_timer = 0

            question_timer += 1
            wind_system.update()
            particle_system.update()

            if question_timer > 1800:
                result = "Time's Up!"
                result_timer = pygame.time.get_ticks()
                score_system.add_miss()
                bottles = []
                q_index += 1
                continue

            for bottle in bottles:
                bottle.update()

            for bullet in bullets[:]:
                bullet.move()

                for bottle in bottles:
                    if bottle.rect.collidepoint(bullet.x + 45, bullet.y + 35):
                        if bottle.correct:
                            result = "Correct!"
                            points = score_system.add_hit(question_timer, bullet.distance_traveled)
                            particle_system.add_hit_effect(bottle.rect.centerx, bottle.rect.centery)
                            result += f" (+{points} pts)"
                        else:
                            result = "Wrong Answer!"
                            score_system.add_miss()
                            particle_system.add_explosion(bottle.rect.centerx, bottle.rect.centery, RED)

                        bottle.hit_animation = 30
                        result_timer = pygame.time.get_ticks()
                        bullets.clear()
                        bottles = []
                        q_index += 1
                        break

                if not bullet.active:
                    bullets.remove(bullet)

            screen.blit(background, (0, 0))

            if bottles:
                show_question(screen, questions[q_index], question_timer)

            for bottle in bottles:
                bottle.draw(screen)

            for bullet in bullets:
                bullet.draw(screen)

            particle_system.draw(screen)
            wind_system.draw_indicator(screen)
            score_system.draw_hud(screen)

            draw_crosshair(screen, mouse_pos)

            if bottles:
                instr = font.render("🎯 Aim with mouse | SPACE to shoot | ESC to Exit", True, WHITE)
                screen.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT - 40))

            if result and pygame.time.get_ticks() - result_timer < 2000:
                result_color = GREEN if "Correct" in result else RED if "Wrong" in result else YELLOW
                result_surface = big_font.render(result, True, result_color)
                result_rect = result_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

                bg_rect = result_rect.inflate(40, 20)
                pygame.draw.rect(screen, BLACK, bg_rect)
                pygame.draw.rect(screen, result_color, bg_rect, 3)

                screen.blit(result_surface, result_rect)

        elif game_state == "results":
            screen.fill(BLACK)
            title = title_font.render("QUIZ RESULTS", True, YELLOW)
            title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 6))
            screen.blit(title, title_rect)

            stats = [
                f"Final Score: {score_system.score:,}",
                f"Accuracy: {score_system.get_accuracy():.1f}%",
                f"Max Streak: {score_system.max_streak}",
                f"Total Hits: {score_system.hits}",
                f"Time Bonuses: {score_system.time_bonuses}",
                "",
                "Press ENTER to return to menu | ESC to Exit"
            ]

            for i, stat in enumerate(stats):
                color = YELLOW if stat.startswith("Final Score") else WHITE
                text = font_medium.render(stat, True, color)
                text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 3 + i * 40))
                screen.blit(text, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        game_state = "menu"
                        break

        pygame.display.flip()
        clock.tick(60)


def run_pdf_viewer(pdf_path=r"C:\Users\B.PURNA\PycharmProjects\DefenseShot\study_materials\module_1.pdf"):
    try:
        reader = PDFReader(pdf_path)
    except Exception as e:
        print(f"Failed to load PDF: {e}")
        return

    current_state = "intro"
    running = True

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif current_state == "intro" and event.key == pygame.K_RETURN:
                    current_state = "pdf_view"
                elif current_state == "pdf_view":
                    if event.key == pygame.K_RIGHT:
                        reader.next_page()
                    elif event.key == pygame.K_LEFT:
                        reader.previous_page()
                    elif event.key == pygame.K_q and reader.can_take_quiz:
                        run_quiz()
                        current_state = "intro"
                        reader = PDFReader(pdf_path)

        if current_state == "intro":
            title = title_font.render("Defense Training Materials", True, YELLOW)
            clue = font.render("Press ENTER to begin studying the materials...", True, CYAN)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT//3))
            screen.blit(clue, (WIDTH//2 - clue.get_width()//2, HEIGHT//2))
        elif current_state == "pdf_view":
            reader.update()
            reader.draw(screen)
            instructions = [
                "LEFT/RIGHT - Navigate pages",
                "Q - Take Quiz (when available)",
                "ESC - Return to menu"
            ]
            for i, instruction in enumerate(instructions):
                text = font.render(instruction, True, WHITE)
                screen.blit(text, (20, HEIGHT - 100 + i * 30))

        pygame.display.flip()
        clock.tick(60)


def main():
    current_state = "main_menu"
    running = True

    while running:
        screen.fill(BLACK)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == "main_menu":
                        running = False
                    else:
                        current_state = "main_menu"
                elif event.key == pygame.K_1 and current_state == "main_menu":
                    run_pdf_viewer()
                    current_state = "main_menu"
                elif event.key == pygame.K_2 and current_state == "main_menu":
                    run_quiz()
                    current_state = "main_menu"

        if current_state == "main_menu":
            title = title_font.render("DEFENSE TRAINING SYSTEM", True, YELLOW)
            title_rect = title.get_rect(center=(WIDTH//2, HEIGHT//4))
            screen.blit(title, title_rect)

            options = [
                "1. Study Defense Materials (PDF Viewer)",
                "2. Take Knowledge Quiz",
                "",
                "Select an option (1-2)",
                "ESC to Exit"
            ]

            for i, option in enumerate(options):
                color = CYAN if option.startswith(("1.", "2.")) else WHITE
                text = font_medium.render(option, True, color)
                text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + i * 40))
                screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
