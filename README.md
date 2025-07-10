# Project documentation
# DefenseShot: Elite Sniper Academy

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![PyGame](https://img.shields.io/badge/PyGame-2.0+-green.svg)](https://pygame.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A **modular, offline, Python-based desktop application** that combines tactical learning with interactive gaming. DefenseShot transforms traditional study materials into an engaging, progressive learning experience using PDF study modules, timed quizzes, and shooter-style gameplay mechanics.

## 🎯 Project Overview

DefenseShot is designed as a **gamified learning management system** where users progress through 10 sequential modules, each containing:
- PDF study materials with timed reading
- Interactive shooter-style quizzes
- Progress tracking and module unlocking system
- User authentication and score management

Perfect for **science exhibitions**, **portfolio demonstrations**, and **placement interviews** - showcasing full-stack desktop development skills.

## ✨ Key Features

### 🔐 User Authentication System
- Secure login/registration with password hashing
- Session management for persistent user states
- User progress tracking across all modules

### 📚 Progressive Learning System
- 10 sequential study modules with PDF materials
- Timed reading sessions (minimum 5 seconds per module)
- Module unlock system based on quiz performance
- Comprehensive progress tracking

### 🎮 Interactive Gaming Elements
- Shooter-style quiz interface using PyGame
- Real-time scoring and feedback
- Audio effects for correct/incorrect answers
- Engaging visual elements and animations

### 💾 Robust Data Management
- SQLite database for offline functionality
- User progress persistence
- Quiz results and performance analytics
- Modular database design for easy expansion

## 🏗️ Project Structure

```
DefenseShot/
│
├── main.py                          # Entry point, handles login, dashboard
├── config.py                        # Global constants, paths, min time etc.
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
│
├── db/
│   ├── database.py                  # SQLite connection + queries
│   └── defenseshot.db               # SQL commands to create all tables
│
├── gui/
│   ├── login.py                     # Login and register UI logic
│   ├── dashboard.py                 # Shows 11 modules, locked/unlocked
│   └── utils.py                     # Shared functions, session handling
│
├── modules/
│   ├── module1.py                   # PDF + Quiz logic for Module 1
│   ├── module2.py                   # Locked until module1 quiz is passed
│   ├── ...
│   └── module11.py                  # Final module
│
├── study_materials/       (****  because of the no space i am not uploding this file so please while creating the project by cloning thing please add this with your modules***)
│   ├── module_1.pdf
│   ├── module_2.pdf
│   └── ... (up to module_10.pdf)
│
│
├── assets/
│   ├── images/                     # Icons, module cards, logos
│   ├── sounds/                     # Gunshot, correct, wrong audio
│   └── fonts/                      # Custom fonts if needed
│
└── user_data/
    └── session.json                # Stores current user info (temp)
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- PyCharm Community Edition (recommended)
- Windows/Linux/macOS compatible

### Installation Steps

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/DefenseShot.git
cd DefenseShot
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Initialize the database:**
```bash
python -c "from db.database import initialize_database; initialize_database()"
```

4. **Run the application:**
```bash
python main.py
```

## 📦 Dependencies

```
pygame>=2.0.0
PyMuPDF>=1.23.0
sqlite3 (built-in)
hashlib (built-in)
json (built-in)
```

## 🎮 How to Use

### 1. **Login/Registration**
- Launch the application
- Create a new account or login with existing credentials
- User data is securely stored with hashed passwords

### 2. **Dashboard Navigation**
- View all 10 modules on the main dashboard
- Only unlocked modules are clickable
- Track your progress visually

### 3. **Module Workflow**
- **Study Phase**: Read the PDF material (minimum 5 seconds)
- **Quiz Phase**: Take the interactive shooter-style quiz
- **Progress**: Score 8/10 or higher to unlock the next module
- **Repeat**: Continue through all 10 modules

### 4. **Progress Tracking**
- View your quiz scores and completion times
- Track unlocked modules and overall progress
- Review past quiz attempts and performance

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

### Progress Table
```sql
CREATE TABLE IF NOT EXISTS progress (
    user_id INTEGER,
    module_id INTEGER,
    unlocked BOOLEAN DEFAULT 0,
    quiz_score INTEGER,
    completed_at TIMESTAMP,
    PRIMARY KEY (user_id, module_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### Quiz Results Table
```sql
CREATE TABLE IF NOT EXISTS quiz_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    module_id INTEGER,
    score INTEGER,
    total_questions INTEGER,
    time_taken INTEGER,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

## 🎯 Configuration

Key settings in `config.py`:
```python
MIN_STUDY_TIME = 5        # Minimum seconds to study PDF
QUIZ_PASS_SCORE = 8       # Required score out of 10
TOTAL_MODULES = 10        # Total number of modules
```

## 🚀 Development Guide

### Adding New Modules
1. Create `moduleX.py` in the `modules/` directory
2. Add corresponding PDF to `study_materials/`
3. Implement quiz logic following the existing module structure
4. Update database with new module information

### Customizing Quiz Logic
Each module contains customizable quiz logic:
- Question types and formats
- Scoring mechanisms
- Visual and audio feedback
- Time limits and constraints

### Extending Database
- Add new tables in `schema.sql`
- Update `database.py` with new query functions
- Modify relevant modules to use new data structures

## 🏆 Project Highlights

### Technical Excellence
- **Modular Architecture**: Clean separation of concerns
- **Database Integration**: Professional-grade data management
- **User Experience**: Intuitive interface with progress tracking
- **Game Development**: Interactive PyGame implementation

### Educational Value
- **Data Structures & Algorithms**: Each module can implement different DSA concepts
- **Software Engineering**: Demonstrates full development lifecycle
- **Problem Solving**: Combines multiple technologies effectively

### Portfolio Impact
- **Full-Stack Development**: Frontend, backend, and database layers
- **Cross-Platform**: Runs on multiple operating systems
- **Scalable Design**: Easy to extend and modify
- **Professional Quality**: Production-ready code structure

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎓 Academic Usage

This project is designed for:
- **Science Exhibition** presentations
- **Portfolio** demonstrations
- **Placement Interview** discussions
- **Academic Project** submissions

## 📞 Support

For questions, issues, or suggestions:
- Open an issue on GitHub
- Contact the development team
- Check the documentation in `/docs`

## 🌟 Acknowledgments

- Built with Python and PyGame
- Inspired by gamified learning principles
- Designed for educational and portfolio purposes

---

**DefenseShot: Elite Sniper Academy** - Where Learning Meets Gaming Excellence! 🎯
https://github.com/Purnatejeshwarareddyb/DefenseShot/blob/main/Screenshot%202025-07-10%20164529.png
