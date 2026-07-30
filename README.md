🐍 AI-Enhanced Snake Game (Competition Edition)

A modern, high-performance, AI-driven evolution of the classic Snake game. Built for the Symbiosis Institute of Technology (SIT), Nagpur induction competition.

This project transforms a simple arcade concept into a fully-fledged software application featuring an autonomous AI opponent, dynamic difficulty scaling, a robust finite state machine, and decoupled rendering logic for buttery-smooth 60 FPS visuals.

👨‍💻 Author Information

Name: Nitin Sah

PRN: 26070521143

Section: C

University: Symbiosis Institute of Technology (SIT), Nagpur

✨ Key Features

🧠 Autonomous AI Opponent: Play against a second snake controlled by a Breadth-First Search (BFS) pathfinding algorithm. The AI treats walls, the player, and itself as dynamic obstacles.

⚙️ Dynamic Difficulty & Game Balance: Choose between Easy, Medium, and Hard. The difficulty dynamically adjusts the AI's "Flaw Rate" (introducing calculated human-like hesitation) and game speed.

🎞️ Decoupled Logic & Smooth Rendering (Lerp): The game logic runs at a fixed interval (e.g., 120ms), but the graphics render at 60 FPS. Uses Linear Interpolation (Lerp) to smoothly animate the snakes between grid points.

🖥️ Robust State Machine: Clean UI flow transitioning gracefully between WELCOME ➔ NAME_ENTRY ➔ DIFFICULTY_SELECT ➔ PLAYING ➔ GAME_OVER.

🎨 Dual-Aesthetic Visuals: Features sleek, dark-mode accessible menus (powered by pygame_gui) that explode into a high-contrast Neon Synthwave arena during gameplay.

🛠️ Under the Hood (Technical Highlights)

Pathfinding & Survival Fallback: If the AI is completely trapped and the BFS algorithm cannot find a path to the food, it switches to a "Survival State," calculating the safest adjacent square to prolong the match.

Optimized Search: Utilizes Python's collections.deque for O(1) queue operations during BFS, ensuring the pathfinding completes in milliseconds without dropping the frame rate.

Event-Driven UI: Replaced hardcoded menu drawing with pygame_gui for professional, accessible, and responsive user interfaces (supporting both mouse hover/click and WASD keyboard navigation).

Native Resolution Scaling: Calculates grid sizes dynamically based on the active window dimensions, ensuring razor-sharp graphics in windowed or 1080p fullscreen mode.

🚀 Installation & How to Run

Prerequisites

Make sure you have Python installed (3.8 or higher is recommended).

1. Clone the repository

git clone https://github.com/nitinsah1804/AI-powered-snake-game/edit/main/README.md
cd ai-snake-game


2. Install dependencies

Install the required libraries (pygame and pygame_gui) using pip:

pip install pygame pygame_gui


3. Run the game

python main.py


🎮 Controls

Menus

Mouse: Hover and click to select difficulties and buttons.

Keyboard: W/S or Up/Down arrows to navigate. Enter to confirm.

Gameplay

Player Movement: W, A, S, D or Arrow Keys.

Fullscreen Toggle: F

Quit/Exit: ESC or Ctrl + Q

Built with logic, rendered with style. Created for SIT Nagpur, 2026.
