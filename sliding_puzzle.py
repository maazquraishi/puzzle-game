import pygame
import random
import time
import heapq
from typing import List, Tuple, Optional
import math

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 4
TILE_SIZE = 100
GRID_WIDTH = GRID_SIZE * TILE_SIZE
GRID_HEIGHT = GRID_SIZE * TILE_SIZE
GRID_X = (WINDOW_WIDTH - GRID_WIDTH) // 2
GRID_Y = 50

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)
BLUE = (0, 100, 200)
GREEN = (0, 150, 0)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)

class PuzzleState:
    def __init__(self, board: List[List[int]], empty_pos: Tuple[int, int], moves: int = 0, parent=None):
        self.board = [row[:] for row in board]
        self.empty_pos = empty_pos
        self.moves = moves
        self.parent = parent
        self.heuristic = self.calculate_manhattan_distance()
        
    def calculate_manhattan_distance(self) -> int:
        """Calculate Manhattan distance heuristic for A* algorithm"""
        distance = 0
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.board[i][j] != 0:
                    target_value = self.board[i][j]
                    target_row = (target_value - 1) // GRID_SIZE
                    target_col = (target_value - 1) % GRID_SIZE
                    distance += abs(i - target_row) + abs(j - target_col)
        return distance
    
    def get_neighbors(self) -> List['PuzzleState']:
        """Get all possible moves from current state"""
        neighbors = []
        row, col = self.empty_pos
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                new_board = [row[:] for row in self.board]
                new_board[row][col], new_board[new_row][new_col] = new_board[new_row][new_col], new_board[row][col]
                new_state = PuzzleState(new_board, (new_row, new_col), self.moves + 1, self)
                neighbors.append(new_state)
        
        return neighbors
    
    def is_goal(self) -> bool:
        """Check if current state is the goal state"""
        target = 1
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if i == GRID_SIZE - 1 and j == GRID_SIZE - 1:
                    return self.board[i][j] == 0
                if self.board[i][j] != target:
                    return False
                target += 1
        return True
    
    def __lt__(self, other):
        return (self.moves + self.heuristic) < (other.moves + other.heuristic)
    
    def __eq__(self, other):
        return self.board == other.board
    
    def __hash__(self):
        return hash(tuple(tuple(row) for row in self.board))

class SlidingPuzzle:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sliding Puzzle Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.board = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.empty_pos = (GRID_SIZE - 1, GRID_SIZE - 1)
        self.moves = 0
        self.start_time = time.time()
        self.game_won = False
        self.solving = False
        self.solution_path = []
        self.solution_index = 0
        
        # Animation
        self.animating = False
        self.animation_start_time = 0
        self.animation_duration = 0.2
        self.animation_from = None
        self.animation_to = None
        self.animation_tile = 0
        
        # Buttons
        self.new_game_button = pygame.Rect(50, 500, 120, 40)
        self.solve_button = pygame.Rect(200, 500, 120, 40)
        
        self.initialize_board()
        self.shuffle_board()
    
    def initialize_board(self):
        """Initialize the board with numbers 1-15 and empty space"""
        num = 1
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if i == GRID_SIZE - 1 and j == GRID_SIZE - 1:
                    self.board[i][j] = 0
                else:
                    self.board[i][j] = num
                    num += 1
    
    def is_solvable(self, board: List[List[int]]) -> bool:
        """Check if the puzzle configuration is solvable"""
        # Convert 2D board to 1D array (excluding empty space)
        flat_board = []
        empty_row = 0
        
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if board[i][j] == 0:
                    empty_row = i
                else:
                    flat_board.append(board[i][j])
        
        # Count inversions
        inversions = 0
        for i in range(len(flat_board)):
            for j in range(i + 1, len(flat_board)):
                if flat_board[i] > flat_board[j]:
                    inversions += 1
        
        # For 4x4 grid: puzzle is solvable if:
        # - Grid width is odd and inversion count is even
        # - Grid width is even and (empty row from bottom is odd and inversions even) or (empty row from bottom is even and inversions odd)
        if GRID_SIZE % 2 == 1:
            return inversions % 2 == 0
        else:
            empty_row_from_bottom = GRID_SIZE - empty_row
            if empty_row_from_bottom % 2 == 1:
                return inversions % 2 == 0
            else:
                return inversions % 2 == 1
    
    def shuffle_board(self):
        """Shuffle the board ensuring it's solvable"""
        while True:
            # Create a list of numbers and shuffle
            numbers = list(range(1, GRID_SIZE * GRID_SIZE)) + [0]
            random.shuffle(numbers)
            
            # Convert to 2D board
            temp_board = []
            for i in range(GRID_SIZE):
                row = []
                for j in range(GRID_SIZE):
                    num = numbers[i * GRID_SIZE + j]
                    row.append(num)
                    if num == 0:
                        self.empty_pos = (i, j)
                temp_board.append(row)
            
            # Check if solvable and not already solved
            if self.is_solvable(temp_board) and not self.is_solved(temp_board):
                self.board = temp_board
                break
        
        self.moves = 0
        self.start_time = time.time()
        self.game_won = False
        self.solving = False
        self.solution_path = []
    
    def is_solved(self, board: List[List[int]] = None) -> bool:
        """Check if the puzzle is solved"""
        if board is None:
            board = self.board
            
        target = 1
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if i == GRID_SIZE - 1 and j == GRID_SIZE - 1:
                    return board[i][j] == 0
                if board[i][j] != target:
                    return False
                target += 1
        return True
    
    def get_adjacent_tiles(self, row: int, col: int) -> List[Tuple[int, int]]:
        """Get positions of tiles adjacent to the given position"""
        adjacent = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            if 0 <= new_row < GRID_SIZE and 0 <= new_col < GRID_SIZE:
                adjacent.append((new_row, new_col))
        
        return adjacent
    
    def can_move_tile(self, row: int, col: int) -> bool:
        """Check if a tile can be moved (is adjacent to empty space)"""
        return self.empty_pos in self.get_adjacent_tiles(row, col)
    
    def move_tile(self, row: int, col: int) -> bool:
        """Move a tile if possible"""
        if not self.can_move_tile(row, col) or self.animating or self.solving:
            return False
        
        # Start animation
        self.animating = True
        self.animation_start_time = time.time()
        self.animation_from = (row, col)
        self.animation_to = self.empty_pos
        self.animation_tile = self.board[row][col]
        
        # Perform the move
        empty_row, empty_col = self.empty_pos
        self.board[empty_row][empty_col] = self.board[row][col]
        self.board[row][col] = 0
        self.empty_pos = (row, col)
        self.moves += 1
        
        # Check if puzzle is solved
        if self.is_solved():
            self.game_won = True
        
        return True
    
    def solve_puzzle(self):
        """Solve the puzzle using A* algorithm"""
        if self.solving or self.is_solved():
            return
        
        self.solving = True
        initial_state = PuzzleState(self.board, self.empty_pos)
        
        if initial_state.is_goal():
            self.solving = False
            return
        
        # A* algorithm
        open_set = [initial_state]
        closed_set = set()
        
        while open_set:
            current_state = heapq.heappop(open_set)
            
            if current_state.is_goal():
                # Reconstruct path
                path = []
                while current_state.parent:
                    path.append(current_state)
                    current_state = current_state.parent
                path.reverse()
                
                self.solution_path = path
                self.solution_index = 0
                break
            
            closed_set.add(current_state)
            
            for neighbor in current_state.get_neighbors():
                if neighbor in closed_set:
                    continue
                
                heapq.heappush(open_set, neighbor)
        
        if not self.solution_path:
            self.solving = False
    
    def update_solution(self):
        """Update the board state during automatic solving"""
        if not self.solving or not self.solution_path:
            return
        
        current_time = time.time()
        if current_time - getattr(self, 'last_solution_move', 0) > 0.5:  # Move every 0.5 seconds
            if self.solution_index < len(self.solution_path):
                next_state = self.solution_path[self.solution_index]
                self.board = [row[:] for row in next_state.board]
                self.empty_pos = next_state.empty_pos
                self.moves += 1
                self.solution_index += 1
                self.last_solution_move = current_time
                
                if self.is_solved():
                    self.game_won = True
                    self.solving = False
            else:
                self.solving = False
    
    def handle_click(self, pos: Tuple[int, int]):
        """Handle mouse click events"""
        x, y = pos
        
        # Check button clicks
        if self.new_game_button.collidepoint(pos):
            self.shuffle_board()
            return
        
        if self.solve_button.collidepoint(pos) and not self.solving:
            self.solve_puzzle()
            return
        
        # Check tile clicks
        if GRID_X <= x < GRID_X + GRID_WIDTH and GRID_Y <= y < GRID_Y + GRID_HEIGHT:
            col = (x - GRID_X) // TILE_SIZE
            row = (y - GRID_Y) // TILE_SIZE
            
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                self.move_tile(row, col)
    
    def get_tile_position(self, row: int, col: int, t: float = 1.0) -> Tuple[int, int]:
        """Get the screen position of a tile, with optional animation interpolation"""
        base_x = GRID_X + col * TILE_SIZE
        base_y = GRID_Y + row * TILE_SIZE
        
        # Apply animation if this tile is being animated
        if (self.animating and self.animation_from and 
            self.animation_from == (row, col) and t < 1.0):
            
            from_row, from_col = self.animation_from
            to_row, to_col = self.animation_to
            
            from_x = GRID_X + from_col * TILE_SIZE
            from_y = GRID_Y + from_row * TILE_SIZE
            to_x = GRID_X + to_col * TILE_SIZE
            to_y = GRID_Y + to_row * TILE_SIZE
            
            # Smooth interpolation
            t_smooth = 0.5 * (1 - math.cos(math.pi * t))
            
            base_x = from_x + (to_x - from_x) * t_smooth
            base_y = from_y + (to_y - from_y) * t_smooth
        
        return int(base_x), int(base_y)
    
    def draw_tile(self, row: int, col: int, animation_t: float = 1.0):
        """Draw a single tile"""
        tile_value = self.board[row][col]
        if tile_value == 0:
            return  # Don't draw empty space
        
        x, y = self.get_tile_position(row, col, animation_t)
        
        # Draw tile background
        tile_rect = pygame.Rect(x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4)
        pygame.draw.rect(self.screen, LIGHT_GRAY, tile_rect)
        pygame.draw.rect(self.screen, DARK_GRAY, tile_rect, 2)
        
        # Draw tile number
        text = self.font.render(str(tile_value), True, BLACK)
        text_rect = text.get_rect(center=tile_rect.center)
        self.screen.blit(text, text_rect)
    
    def draw_grid(self):
        """Draw the puzzle grid"""
        # Calculate animation progress
        animation_t = 1.0
        if self.animating:
            elapsed = time.time() - self.animation_start_time
            animation_t = min(elapsed / self.animation_duration, 1.0)
            
            if animation_t >= 1.0:
                self.animating = False
        
        # Draw grid background
        grid_rect = pygame.Rect(GRID_X, GRID_Y, GRID_WIDTH, GRID_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, grid_rect)
        pygame.draw.rect(self.screen, BLACK, grid_rect, 3)
        
        # Draw grid lines
        for i in range(1, GRID_SIZE):
            # Vertical lines
            x = GRID_X + i * TILE_SIZE
            pygame.draw.line(self.screen, BLACK, (x, GRID_Y), (x, GRID_Y + GRID_HEIGHT), 2)
            
            # Horizontal lines
            y = GRID_Y + i * TILE_SIZE
            pygame.draw.line(self.screen, BLACK, (GRID_X, y), (GRID_X + GRID_WIDTH, y), 2)
        
        # Draw tiles
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.draw_tile(i, j, animation_t)
    
    def draw_ui(self):
        """Draw the user interface elements"""
        # Draw title
        title_text = self.font.render("Sliding Puzzle", True, BLACK)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 25))
        self.screen.blit(title_text, title_rect)
        
        # Draw move counter
        moves_text = self.small_font.render(f"Moves: {self.moves}", True, BLACK)
        self.screen.blit(moves_text, (50, 460))
        
        # Draw timer
        elapsed_time = int(time.time() - self.start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = self.small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, BLACK)
        self.screen.blit(time_text, (200, 460))
        
        # Draw buttons
        pygame.draw.rect(self.screen, BLUE, self.new_game_button)
        pygame.draw.rect(self.screen, BLACK, self.new_game_button, 2)
        new_game_text = self.small_font.render("New Game", True, WHITE)
        new_game_rect = new_game_text.get_rect(center=self.new_game_button.center)
        self.screen.blit(new_game_text, new_game_rect)
        
        solve_color = GREEN if not self.solving else GRAY
        pygame.draw.rect(self.screen, solve_color, self.solve_button)
        pygame.draw.rect(self.screen, BLACK, self.solve_button, 2)
        solve_text = self.small_font.render("Auto Solve", True, WHITE)
        solve_rect = solve_text.get_rect(center=self.solve_button.center)
        self.screen.blit(solve_text, solve_rect)
        
        # Draw status messages
        if self.game_won:
            win_text = self.font.render("Congratulations! Puzzle Solved!", True, GREEN)
            win_rect = win_text.get_rect(center=(WINDOW_WIDTH // 2, 550))
            self.screen.blit(win_text, win_rect)
        elif self.solving:
            solving_text = self.small_font.render("Solving automatically...", True, BLUE)
            self.screen.blit(solving_text, (350, 460))
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
            
            # Update automatic solving
            if self.solving:
                self.update_solution()
            
            # Draw everything
            self.screen.fill(WHITE)
            self.draw_grid()
            self.draw_ui()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    game = SlidingPuzzle()
    game.run()
