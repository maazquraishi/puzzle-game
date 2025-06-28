# Sliding Puzzle Game

A feature-rich 4x4 sliding puzzle game built with Python and Pygame.

## Features

- **4x4 Grid**: Classic sliding puzzle with numbered tiles 1-15 and one empty space
- **Smart Shuffling**: Ensures the puzzle is always solvable
- **Interactive Gameplay**: Click on tiles adjacent to the empty space to move them
- **Move Counter**: Tracks the number of moves made
- **Timer**: Shows elapsed time since game start
- **Smooth Animations**: Tiles slide smoothly when moved
- **New Game Button**: Reset and shuffle the board for a new challenge
- **Auto Solve**: Uses A* algorithm to automatically solve the puzzle
- **Win Detection**: Congratulates you when the puzzle is solved
- **Clean UI**: Responsive and intuitive user interface

## Requirements

- Python 3.6+
- Pygame 2.0.0+

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the game:
   ```bash
   python sliding_puzzle.py
   ```

## How to Play

1. **Objective**: Arrange the numbered tiles in order from 1-15, with the empty space in the bottom-right corner
2. **Movement**: Click on any tile adjacent to the empty space to slide it into the empty position
3. **New Game**: Click the "New Game" button to shuffle the board and start over
4. **Auto Solve**: Click the "Auto Solve" button to watch the A* algorithm solve the puzzle automatically
5. **Track Progress**: Monitor your moves and time in the bottom-left corner

## Game Controls

- **Mouse Click**: Move tiles or interact with buttons
- **New Game Button**: Shuffle and reset the puzzle
- **Auto Solve Button**: Automatically solve the current puzzle state

## Algorithm Details

The auto-solve feature uses the A* pathfinding algorithm with Manhattan distance as the heuristic function. This ensures optimal solutions while maintaining reasonable performance.

## Technical Features

- **Solvability Check**: Ensures all generated puzzles have valid solutions
- **Smooth Animations**: Interpolated tile movements for better user experience
- **Efficient Rendering**: Optimized drawing routines for smooth 60 FPS gameplay
- **State Management**: Clean separation between game logic and presentation

Enjoy solving the puzzle!
