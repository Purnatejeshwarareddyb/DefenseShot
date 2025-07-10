# # gui/__init__.py
# # This file makes the gui directory a Python package
#
# # Import UI utilities
# from .utils import Button, SessionHelper, UIHelper, draw_centered_text, draw_text
#
# # Import the enhanced login system components (primary system)
# from .enhanced_login import (
#     EnhancedLoginSystem,
#     EmailService,
#     SecurityHelper,
#     InputField,
#     DatabaseInterface,
#     run_enhanced_login_system,
#     setup_email_service
# )
#
# # Import original login system (backup/legacy)
# try:
#     from .login import run_login_system
# except ImportError:
#     run_login_system = None
#
# # Make these available when someone imports the gui package
# __all__ = [
#     # UI utilities
#     'Button',
#     'SessionHelper',
#     'UIHelper',
#     'draw_centered_text',
#     'draw_text',
#
#     # Enhanced login system (primary)
#     'EnhancedLoginSystem',
#     'EmailService',
#     'SecurityHelper',
#     'InputField',
#     'DatabaseInterface',
#     'run_enhanced_login_system',
#     'setup_email_service',
#
#     # Original login system (backup)
#     'run_login_system'
# ]