# import json
# import os
# from typing import Optional, Dict, Any
# from datetime import datetime
#
#
# class SessionManager:
#     def __init__(self, session_file_path: str = "user_data/session.json"):
#         self.session_file_path = session_file_path
#         self.ensure_user_data_directory()
#
#     def ensure_user_data_directory(self):
#         """Create user_data directory if it doesn't exist"""
#         os.makedirs(os.path.dirname(self.session_file_path), exist_ok=True)
#
#     def save_session(self, user_data: Dict[str, Any]) -> bool:
#         """
#         Save user session data to JSON file
#
#         Args:
#             user_data: Dictionary containing user information
#
#         Returns:
#             bool: True if successful, False otherwise
#         """
#         try:
#             session_data = {
#                 "user_id": user_data.get("id"),
#                 "username": user_data.get("username"),
#                 "email": user_data.get("email"),
#                 "login_time": datetime.now().isoformat(),
#                 "last_activity": datetime.now().isoformat(),
#                 "is_logged_in": True
#             }
#
#             with open(self.session_file_path, 'w') as f:
#                 json.dump(session_data, f, indent=4)
#
#             return True
#
#         except Exception as e:
#             print(f"Error saving session: {e}")
#             return False
#
#     def load_session(self) -> Optional[Dict[str, Any]]:
#         """
#         Load user session data from JSON file
#
#         Returns:
#             Dict containing session data or None if no valid session
#         """
#         try:
#             if not os.path.exists(self.session_file_path):
#                 return None
#
#             with open(self.session_file_path, 'r') as f:
#                 session_data = json.load(f)
#
#             # Check if session is still valid (user is logged in)
#             if not session_data.get("is_logged_in", False):
#                 return None
#
#             return session_data
#
#         except Exception as e:
#             print(f"Error loading session: {e}")
#             return None
#
#     def update_last_activity(self):
#         """Update the last activity timestamp"""
#         try:
#             session_data = self.load_session()
#             if session_data:
#                 session_data["last_activity"] = datetime.now().isoformat()
#
#                 with open(self.session_file_path, 'w') as f:
#                     json.dump(session_data, f, indent=4)
#
#         except Exception as e:
#             print(f"Error updating last activity: {e}")
#
#     def clear_session(self) -> bool:
#         """
#         Clear the current session (logout)
#
#         Returns:
#             bool: True if successful, False otherwise
#         """
#         try:
#             if os.path.exists(self.session_file_path):
#                 # Mark as logged out instead of deleting
#                 session_data = self.load_session()
#                 if session_data:
#                     session_data["is_logged_in"] = False
#                     session_data["logout_time"] = datetime.now().isoformat()
#
#                     with open(self.session_file_path, 'w') as f:
#                         json.dump(session_data, f, indent=4)
#
#                 return True
#
#         except Exception as e:
#             print(f"Error clearing session: {e}")
#             return False
#
#     def is_logged_in(self) -> bool:
#         """
#         Check if user is currently logged in
#
#         Returns:
#             bool: True if logged in, False otherwise
#         """
#         session_data = self.load_session()
#         return session_data is not None and session_data.get("is_logged_in", False)
#
#     def get_current_user_id(self) -> Optional[int]:
#         """
#         Get the current logged-in user's ID
#
#         Returns:
#             int: User ID or None if not logged in
#         """
#         session_data = self.load_session()
#         if session_data:
#             return session_data.get("user_id")
#         return None
#
#     def get_current_username(self) -> Optional[str]:
#         """
#         Get the current logged-in user's username
#
#         Returns:
#             str: Username or None if not logged in
#         """
#         session_data = self.load_session()
#         if session_data:
#             return session_data.get("username")
#         return None
#
#     def get_session_info(self) -> Dict[str, Any]:
#         """
#         Get complete session information
#
#         Returns:
#             Dict containing all session data
#         """
#         session_data = self.load_session()
#         if session_data:
#             return session_data
#         return {}
#
#
# # Example usage functions for integration with your existing code
# def login_user(user_data: Dict[str, Any]) -> bool:
#     """
#     Login a user and create session
#
#     Args:
#         user_data: User information from database
#
#     Returns:
#         bool: True if login successful
#     """
#     session_manager = SessionManager()
#     return session_manager.save_session(user_data)
#
#
# def logout_user() -> bool:
#     """
#     Logout current user
#
#     Returns:
#         bool: True if logout successful
#     """
#     session_manager = SessionManager()
#     return session_manager.clear_session()
#
#
# def get_logged_in_user() -> Optional[Dict[str, Any]]:
#     """
#     Get current logged-in user information
#
#     Returns:
#         Dict with user info or None if not logged in
#     """
#     session_manager = SessionManager()
#     return session_manager.load_session()
#
#
# def is_user_logged_in() -> bool:
#     """
#     Check if any user is currently logged in
#
#     Returns:
#         bool: True if logged in
#     """
#     session_manager = SessionManager()
#     return session_manager.is_logged_in()