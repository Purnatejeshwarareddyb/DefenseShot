#!/usr/bin/env python3
"""
DefenseShot: Elite Sniper Academy
Main entry point - handles login and dashboard routing
"""

import pygame
import sys
import os
from gui.login import LoginManager
from gui.dashboard import Dashboard
from db.database import init_db
from config import *

def main():
    """Main application entry point"""
    # Initialize pygame
    pygame.init()

    # Initialize database
    init_db()

    # Create main window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)

    pygame.display.set_caption("DefenseShot: Elite Sniper Academy")

    # Load icon if available
    try:
        icon = pygame.image.load(os.path.join(ASSETS_DIR, "images", "icon.png"))
        pygame.display.set_icon(icon)
    except:
        pass

    clock = pygame.time.Clock()

    # Initialize login manager
    login_manager = LoginManager(screen)
    dashboard = None

    # Main application loop
    running = True
    logged_in = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if not logged_in:
                # Handle login screen
                result = login_manager.handle_event(event)
                if result == "login_success":
                    logged_in = True
                    dashboard = Dashboard(screen)
                elif result == "quit":
                    running = False
            else:
                # Handle dashboard
                if dashboard:
                    result = dashboard.handle_event(event)
                    if result == "logout":
                        logged_in = False
                        login_manager = LoginManager(screen)
                        dashboard = None
                    elif result == "quit":
                        running = False

        # Render current screen
        screen.fill(BLACK)

        if not logged_in:
            login_manager.render()
        else:
            if dashboard:
                dashboard.render()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()