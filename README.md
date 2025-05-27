Pac-Man Game
A Python implementation of the classic Pac-Man game using Pygame. Features include multiple levels, A* pathfinding for Pac-Man, ghost AI, power pellets, and warp tunnels.
Installation

Clone the repository:git clone https://github.com/yourusername/pacman_game.git
cd pacman_game


Install dependencies:pip install -r requirements.txt


Run the game:python main.py



Features

Two maze levels
A* pathfinding for Pac-Man with ghost avoidance
Ghost AI with power mode behavior
Warp tunnels and power pellets
Score tracking and level progression

Controls

The game is AI-controlled; Pac-Man moves automatically using A* pathfinding.

Project Structure

pacman/: Contains game modules
init.py: Marks the directory as a Python package
constants.py: Game settings and maze data
rendering.py: Drawing functions for maze, Pac-Man, ghosts, and screens
game_logic.py: Game logic including movement, collisions, and pathfinding


main.py: Entry point to run the game
requirements.txt: Lists Pygame dependency
.gitignore: Specifies files to ignore in Git

License
MIT License
