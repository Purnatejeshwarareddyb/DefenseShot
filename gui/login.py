"""
DefenseShot: Elite Sniper Academy
Login and Registration GUI module
"""

import pygame
import sys
from gui.utils import Button, InputField, render_text
from db.database import register_user, verify_login, load_session
from config import *


class LoginManager:
    def __init__(self, screen):
        self.screen = screen
        self.background_image = pygame.image.load(
            r"C:\Users\B.PURNA\PycharmProjects\DefenseShot\assets\images\background.jpg")
        self.background_image = pygame.transform.scale(self.background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.mode = "login"  # "login" or "register"
        self.message = ""
        self.message_color = WHITE

        # REMOVED AUTO-LOGIN - Always show login screen
        self.auto_login = False
        self.current_user = None

        self.setup_ui()

    def setup_ui(self):
        """Setup UI elements"""
        center_x = SCREEN_WIDTH // 2

        # Title
        self.title_pos = (center_x, 100)

        # Input fields
        self.username_field = InputField(
            center_x - 150, 250, 300, 40,
            "Username", self.font_medium
        )
        self.password_field = InputField(
            center_x - 150, 320, 300, 40,
            "Password", self.font_medium, password=True
        )
        self.email_field = InputField(
            center_x - 150, 390, 300, 40,
            "Email (optional)", self.font_medium
        )

        # Buttons
        self.login_btn = Button(
            center_x - 100, 480, 200, 50,
            "LOGIN", self.font_medium
        )
        self.register_btn = Button(
            center_x - 100, 550, 200, 50,
            "REGISTER", self.font_medium
        )
        self.switch_btn = Button(
            center_x - 100, 620, 200, 30,
            "Switch to Register", self.font_small
        )
        self.quit_btn = Button(
            center_x - 50, 680, 100, 30,
            "QUIT", self.font_small
        )

        # Guest mode button
        self.guest_btn = Button(
            center_x - 100, 460, 200, 30,
            "Continue as Guest", self.font_small
        )

    def handle_event(self, event):
        """Handle pygame events"""
        # REMOVED AUTO-LOGIN CHECK - Always process events normally

        # Handle input fields
        self.username_field.handle_event(event)
        self.password_field.handle_event(event)
        if self.mode == "register":
            self.email_field.handle_event(event)

        # Handle buttons
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.login_btn.is_clicked(event.pos) and self.mode == "login":
                return self.handle_login()
            elif self.register_btn.is_clicked(event.pos) and self.mode == "register":
                return self.handle_register()
            elif self.switch_btn.is_clicked(event.pos):
                self.switch_mode()
            elif self.quit_btn.is_clicked(event.pos):
                return "quit"
            elif self.guest_btn.is_clicked(event.pos):
                return self.handle_guest_login()

        # Handle Enter key
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.mode == "login":
                    return self.handle_login()
                else:
                    return self.handle_register()

        return None

    def handle_login(self):
        """Handle login attempt"""
        username = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()

        if not username or not password:
            self.message = "Please enter username and password"
            self.message_color = RED
            return None

        success, result = verify_login(username, password)

        if success:
            self.current_user = result
            self.message = "Login successful!"
            self.message_color = GREEN
            return "login_success"
        else:
            self.message = result
            self.message_color = RED
            return None

    def handle_register(self):
        """Handle registration attempt"""
        username = self.username_field.get_text().strip()
        password = self.password_field.get_text().strip()
        email = self.email_field.get_text().strip()

        if not username or not password:
            self.message = "Please enter username and password"
            self.message_color = RED
            return None

        if len(password) < PASSWORD_MIN_LENGTH:
            self.message = f"Password must be at least {PASSWORD_MIN_LENGTH} characters"
            self.message_color = RED
            return None

        success, result = register_user(username, password, email if email else None)

        if success:
            self.message = "Registration successful! Please login."
            self.message_color = GREEN
            self.switch_mode()
        else:
            self.message = result
            self.message_color = RED

        return None

    def handle_guest_login(self):
        """Handle guest login"""
        # Create a temporary guest user
        self.current_user = {
            'id': 0,
            'username': 'Guest',
            'email': ''
        }
        return "login_success"

    def switch_mode(self):
        """Switch between login and register modes"""
        if self.mode == "login":
            self.mode = "register"
            self.switch_btn.text = "Switch to Login"
            self.email_field.active = False
        else:
            self.mode = "login"
            self.switch_btn.text = "Switch to Register"

        # Clear fields and message
        self.username_field.clear()
        self.password_field.clear()
        self.email_field.clear()
        self.message = ""

    def render(self):
        """Render login screen"""
        # Background
        self.screen.fill(BLACK)

        # Military-style background pattern
        self.screen.blit(self.background_image, (0, 0))

        # for i in range(0, SCREEN_WIDTH, 100):
        #     for j in range(0, SCREEN_HEIGHT, 100):
        #         pygame.draw.rect(self.screen, DARK_GRAY, (i, j, 50, 50))

        # Title
        title_text = "🎯 DEFENSESHOT"
        subtitle_text = "Elite Sniper Academy"

        title_surface = self.font_large.render(title_text, True, ORANGE)
        subtitle_surface = self.font_medium.render(subtitle_text, True, WHITE)

        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, 120))

        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)

        # Mode title
        mode_title = "LOGIN" if self.mode == "login" else "REGISTER"
        mode_surface = self.font_medium.render(mode_title, True, MILITARY_GREEN)
        mode_rect = mode_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(mode_surface, mode_rect)

        # Input fields
        self.username_field.render(self.screen)
        self.password_field.render(self.screen)
        if self.mode == "register":
            self.email_field.render(self.screen)

        # Buttons
        if self.mode == "login":
            self.login_btn.render(self.screen, MILITARY_GREEN)
            self.guest_btn.render(self.screen, DARK_GRAY)
        else:
            self.register_btn.render(self.screen, MILITARY_GREEN)

        self.switch_btn.render(self.screen, DARK_GRAY)
        self.quit_btn.render(self.screen, RED)

        # Message
        if self.message:
            message_surface = self.font_small.render(self.message, True, self.message_color)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, 440))
            self.screen.blit(message_surface, message_rect)

        # Instructions
        instructions = [
            "• Use your credentials to access training modules",
            "• Complete modules sequentially to unlock new content",
            "• Achieve 8/10 or higher to progress"
        ]

        y_offset = 750
        for instruction in instructions:
            inst_surface = self.font_small.render(instruction, True, LIGHT_GRAY)
            self.screen.blit(inst_surface, (50, y_offset))
            y_offset += 20