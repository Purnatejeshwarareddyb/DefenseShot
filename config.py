"""
DefenseShot: Elite Sniper Academy
Global configuration file - constants, paths, and settings
"""

import os

# Application Settings
APP_NAME = "DefenseShot: Elite Sniper Academy"
VERSION = "1.0.0"

# Display Settings
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Military Colors
MILITARY_GREEN = (85, 107, 47)
DESERT_TAN = (210, 180, 140)
NAVY_BLUE = (0, 0, 128)
CAMOUFLAGE_BROWN = (101, 67, 33)

# Quiz Settings
MIN_STUDY_TIME = 5  # Seconds before quiz appears
QUIZ_PASS_SCORE = 8  # Score to unlock next module (out of 10)
TOTAL_MODULES = 10
QUIZ_QUESTIONS_PER_MODULE = 10
QUIZ_TIME_LIMIT = 300  # 5 minutes per quiz

# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STUDY_DIR = os.path.join(BASE_DIR, "study_materials")
MCQ_DIR = os.path.join(BASE_DIR, "mcqs")
DB_PATH = os.path.join(BASE_DIR, "db", "defenseshot.db")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
USER_DATA_DIR = os.path.join(BASE_DIR, "user_data")
SESSION_FILE = os.path.join(USER_DATA_DIR, "session.json")

# Database Settings
DB_VERSION = 1

# UI Settings
BUTTON_HEIGHT = 50
BUTTON_WIDTH = 200
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32
FONT_SIZE_TITLE = 48

# Module Topics (for reference)
MODULE_TOPICS = {
    1: "Arrays and Dynamic Arrays",
    2: "Linked Lists",
    3: "Stacks and Queues",
    4: "Trees and Binary Search Trees",
    5: "Heaps and Priority Queues",
    6: "Hash Tables and Hash Maps",
    7: "Graph Fundamentals",
    8: "Graph Traversal (DFS/BFS)",
    9: "Sorting Algorithms",
    10: "Searching Algorithms",
    11: "Dynamic Programming Basics",
    12: "Advanced Dynamic Programming",
    13: "Greedy Algorithms",
    14: "Divide and Conquer",
    15: "Backtracking",
    16: "String Algorithms",
    17: "Advanced Graph Algorithms",
    18: "Computational Geometry",
    19: "Network Flow",
    20: "Advanced Data Structures"
}

# Sound Settings
SOUND_ENABLED = True
SOUND_VOLUME = 0.7

# Animation Settings
ANIMATION_SPEED = 5
FADE_SPEED = 3

# Security Settings
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600  # 1 hour in seconds

# Create directories if they don't exist
def create_directories():
    """Create necessary directories"""
    directories = [
        os.path.dirname(DB_PATH),
        STUDY_DIR,
        MCQ_DIR,
        ASSETS_DIR,
        os.path.join(ASSETS_DIR, "images"),
        os.path.join(ASSETS_DIR, "sounds"),
        os.path.join(ASSETS_DIR, "fonts"),
        USER_DATA_DIR
    ]

    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)

# Initialize directories on import
create_directories()