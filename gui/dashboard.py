"""
DefenseShot: Elite Sniper Academy
Main dashboard GUI - shows available modules
"""

import pygame
import subprocess
import sys
import os
from gui.utils import Button, ModuleCard, ProgressBar, render_text
from db.database import get_unlocked_modules, get_user_stats, load_session, clear_session
from config import *

class Dashboard:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
        self.background_image = pygame.image.load(
            r"C:\Users\B.PURNA\PycharmProjects\DefenseShot\assets\images\background.jpg")
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Load current user - FIXED: Handle None and missing 'id' key
        session_data = load_session()
        if session_data and isinstance(session_data, dict) and 'id' in session_data:
            self.user = session_data
        else:
            # Default guest user structure
            self.user = {'id': 0, 'username': 'Guest', 'email': ''}

        # Load user progress
        self.modules = []
        self.user_stats = {}
        self.load_user_data()

        self.setup_ui()

    def load_user_data(self):
        """Load user modules and statistics"""
        # FIXED: Use get() method to safely access 'id' key
        user_id = self.user.get('id', 0)

        if user_id > 0:  # Not guest
            # Get unlocked modules
            unlocked = get_unlocked_modules(user_id)
            unlocked_numbers = [m['module_number'] for m in unlocked]
            completed_numbers = [m['module_number'] for m in unlocked if m['is_completed']]

            # Create all modules
            for i in range(1, TOTAL_MODULES + 1):
                self.modules.append({
                    'number': i,
                    'title': MODULE_TOPICS.get(i, f"Module {i}"),
                    'unlocked': i in unlocked_numbers,
                    'completed': i in completed_numbers
                })

            # Get user stats
            self.user_stats = get_user_stats(user_id) or {}
        else:
            # Guest mode - only first module unlocked
            for i in range(1, TOTAL_MODULES + 1):
                self.modules.append({
                    'number': i,
                    'title': MODULE_TOPICS.get(i, f"Module {i}"),
                    'unlocked': i == 1,
                    'completed': False
                })
            self.user_stats = {
                'completed_modules': 0,
                'total_modules': TOTAL_MODULES,
                'average_score': 0,
                'total_study_time': 0
            }

    def setup_ui(self):
        """Setup UI elements"""
        # Header buttons
        self.logout_btn = Button(
            SCREEN_WIDTH - 120, 10, 100, 30,
            "LOGOUT", self.font_small
        )
        self.stats_btn = Button(
            SCREEN_WIDTH - 240, 10, 100, 30,
            "STATS", self.font_small
        )

        # Module cards
        self.module_cards = []
        cards_per_row = 4
        card_width = 250
        card_height = 150
        start_x = (SCREEN_WIDTH - (cards_per_row * card_width + (cards_per_row - 1) * 20)) // 2
        start_y = 180

        for i, module in enumerate(self.modules):
            row = i // cards_per_row
            col = i % cards_per_row

            x = start_x + col * (card_width + 20)
            y = start_y + row * (card_height + 20)

            card = ModuleCard(
                x, y, card_width, card_height,
                module['number'], module['title'],
                module['unlocked'], module['completed']
            )
            self.module_cards.append(card)

        # Progress bar
        self.progress_bar = ProgressBar(
            50, 100, SCREEN_WIDTH - 100, 20, TOTAL_MODULES
        )
        self.progress_bar.set_value(self.user_stats.get('completed_modules', 0))

        # Show stats panel
        self.show_stats = False

    def handle_event(self, event):
        """Handle pygame events"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check header buttons
            if self.logout_btn.is_clicked(event.pos):
                clear_session()
                return "logout"

            if self.stats_btn.is_clicked(event.pos):
                self.show_stats = not self.show_stats
                return None

            # Check module cards
            for card in self.module_cards:
                if card.is_clicked(event.pos):
                    return self.launch_module(card.module_number)

        elif event.type == pygame.MOUSEMOTION:
            # Update button hover states
            self.logout_btn.update(event.pos)
            self.stats_btn.update(event.pos)

            # Update card hover states
            for card in self.module_cards:
                card.update(event.pos)

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.show_stats = False
            elif event.key == pygame.K_F1:
                self.show_stats = not self.show_stats

        return None

    def launch_module(self, module_number):
        """Launch specific module"""
        try:
            # Run module script
            module_script = os.path.join("modules", f"module{module_number}.py")
            if os.path.exists(module_script):
                subprocess.run([sys.executable, module_script], check=True)
                # Reload user data after module completion
                self.load_user_data()
                self.setup_ui()
            else:
                print(f"Module {module_number} script not found")
        except subprocess.CalledProcessError:
            print(f"Error launching module {module_number}")
        except Exception as e:
            print(f"Unexpected error: {e}")

        return None

    def render(self):
        """Render dashboard"""
        # Background
        self.screen.fill(BLACK)

         # Military pattern background
        # Background image
        self.screen.blit(self.background_image, (0, 0))
        # Optional overlay for better text visibility
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(100)  # Adjust transparency (0 = fully transparent, 255 = fully black)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        # for i in range(0, SCREEN_WIDTH, 80):
        #     for j in range(0, SCREEN_HEIGHT, 80):
        #         pygame.draw.rect(self.screen, DARK_GRAY, (i, j, 40, 40))

        # Header
        self.render_header()

        # Progress section
        self.render_progress()

        # Module grid
        self.render_modules()

        # Stats overlay
        if self.show_stats:
            self.render_stats_overlay()

        # Footer
        self.render_footer()

    def render_header(self):
        """Render header section"""
        # Title - FIXED: Use get() method for safe access
        username = self.user.get('username', 'Guest')
        title_text = f"🎯 Welcome, {username}!"
        title_surface = self.font_large.render(title_text, True, ORANGE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, 40))
        self.screen.blit(title_surface, title_rect)

        # Buttons
        self.logout_btn.render(self.screen, RED)
        self.stats_btn.render(self.screen, MILITARY_GREEN)

    def render_progress(self):
        """Render progress section"""
        # Progress label
        progress_text = f"Training Progress: {self.user_stats.get('completed_modules', 0)}/{TOTAL_MODULES} Modules"
        progress_surface = self.font_medium.render(progress_text, True, WHITE)
        self.screen.blit(progress_surface, (50, 75))

        # Progress bar
        self.progress_bar.render(self.screen)

        # Percentage
        percentage = (self.user_stats.get('completed_modules', 0) / TOTAL_MODULES) * 100
        percent_text = f"{percentage:.1f}%"
        percent_surface = self.font_small.render(percent_text, True, WHITE)
        self.screen.blit(percent_surface, (SCREEN_WIDTH - 100, 75))

    def render_modules(self):
        """Render module grid"""
        # Section title
        section_title = "Training Modules"
        section_surface = self.font_medium.render(section_title, True, WHITE)
        section_rect = section_surface.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(section_surface, section_rect)

        # Module cards
        for card in self.module_cards:
            card.render(self.screen)

        # Instructions
        instructions = [
            "• Click on available modules to start training",
            "• Complete modules sequentially to unlock new content",
            "• Achieve 8/10 or higher score to progress to next module"
        ]

        y_offset = SCREEN_HEIGHT - 80
        for instruction in instructions:
            inst_surface = self.font_small.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(inst_surface, (50, y_offset))
            y_offset += 20

    def render_stats_overlay(self):
        """Render statistics overlay"""
        # Semi-transparent background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # Stats panel
        panel_width = 500
        panel_height = 400
        panel_x = (SCREEN_WIDTH - panel_width) // 2
        panel_y = (SCREEN_HEIGHT - panel_height) // 2

        pygame.draw.rect(self.screen, DARK_GRAY, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 3)

        # Stats title
        title_text = "📊 Training Statistics"
        title_surface = self.font_large.render(title_text, True, ORANGE)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH//2, panel_y + 40))
        self.screen.blit(title_surface, title_rect)

        # Stats content
        stats_data = [
            ("Completed Modules", f"{self.user_stats.get('completed_modules', 0)}/{TOTAL_MODULES}"),
            ("Average Score", f"{self.user_stats.get('average_score', 0):.1f}/10"),
            ("Total Study Time", f"{self.user_stats.get('total_study_time', 0)//60} minutes"),
            ("Progress", f"{(self.user_stats.get('completed_modules', 0)/TOTAL_MODULES)*100:.1f}%")
        ]

        y_offset = panel_y + 100
        for label, value in stats_data:
            label_surface = self.font_medium.render(f"{label}:", True, WHITE)
            value_surface = self.font_medium.render(value, True, YELLOW)

            self.screen.blit(label_surface, (panel_x + 50, y_offset))
            self.screen.blit(value_surface, (panel_x + 300, y_offset))
            y_offset += 50

        # Close instruction
        close_text = "Press ESC or F1 to close"
        close_surface = self.font_small.render(close_text, True, LIGHT_GRAY)
        close_rect = close_surface.get_rect(center=(SCREEN_WIDTH//2, panel_y + panel_height - 30))
        self.screen.blit(close_surface, close_rect)

    def render_footer(self):
        """Render footer"""
        footer_text = "DefenseShot: Elite Sniper Academy v1.0 | Press F1 for Statistics"
        footer_surface = self.font_small.render(footer_text, True, GRAY)
        footer_rect = footer_surface.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 20))
        self.screen.blit(footer_surface, footer_rect)