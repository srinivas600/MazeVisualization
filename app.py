import os
import numpy as np
import matplotlib.pyplot as plt
import random
import logging
from heapq import heappush, heappop

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MazeGenerator:
    """A class to generate and visualize mazes using depth-first search algorithm."""

    def __init__(self, width=10, height=10, num_exits=1):
        """
        Initialize the maze generator with given dimensions.

        Args:
            width (int): Width of the maze (default: 10)
            height (int): Height of the maze (default: 10)
            num_exits (int): Number of exits to create (default: 1)
        """
        self.width = width
        self.height = height
        self.num_exits = num_exits
        self.maze = np.ones((2 * height + 1, 2 * width + 1))
        self.visited = set()
        self.paths = []  # Store paths to all exits
        self.start = (1, 0)  # Fixed start position
        self.exits = []

    def generate_maze(self):
        """Generate a random maze using depth-first search algorithm."""
        try:
            logger.info("Starting maze generation...")
            self._dfs(1, 1)
            self.maze[self.start] = 0  # Create entrance
            self._generate_exits()  # Create multiple exits
            logger.info("Maze generation completed successfully")
            return self.maze
        except Exception as e:
            logger.error(f"Error generating maze: {e}")
            raise

    def _dfs(self, x, y):
        """Implement depth-first search to carve paths in the maze."""
        self.visited.add((x, y))
        self.maze[y, x] = 0

        # Possible directions: right, down, left, up
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (0 < new_x < self.maze.shape[1] - 1 and
                0 < new_y < self.maze.shape[0] - 1 and
                (new_x, new_y) not in self.visited):
                self.maze[y + dy // 2, x + dx // 2] = 0
                self._dfs(new_x, new_y)

    def _generate_exits(self):
        """Generate multiple exits along the maze's boundaries."""
        possible_exits = []

        # Collect all valid edge positions
        for y in range(1, self.maze.shape[0] - 1, 2):
            if self.maze[y, -2] == 0:  # Right edge
                possible_exits.append((y, self.maze.shape[1] - 1))
            if self.maze[y, 1] == 0:  # Left edge
                possible_exits.append((y, 0))

        for x in range(1, self.maze.shape[1] - 1, 2):
            if self.maze[-2, x] == 0:  # Bottom edge
                possible_exits.append((self.maze.shape[0] - 1, x))
            if self.maze[1, x] == 0:  # Top edge
                possible_exits.append((0, x))

        # Randomly select unique exits
        self.exits = random.sample(possible_exits, min(self.num_exits, len(possible_exits)))

        # Carve exits
        for y, x in self.exits:
            self.maze[y, x] = 0

    def _heuristic(self, a, b):
        """Calculate Manhattan distance heuristic."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_neighbors(self, pos):
        """Get valid neighboring positions."""
        y, x = pos
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        neighbors = []
        
        for dy, dx in directions:
            new_y, new_x = y + dy, x + dx
            if (0 <= new_y < self.maze.shape[0] and 
                0 <= new_x < self.maze.shape[1] and 
                self.maze[new_y, new_x] == 0):
                neighbors.append((new_y, new_x))
        
        return neighbors

    def find_all_paths(self):
        """Find paths to all exits using A* algorithm."""
        logger.info("Finding paths to all exits...")
        self.paths = []
        
        for exit_pos in self.exits:
            path = self._astar(self.start, exit_pos)
            if path:
                self.paths.append(path)
                logger.info(f"Path found to exit at {exit_pos}")
            else:
                logger.warning(f"No path found to exit at {exit_pos}")

    def _astar(self, start, goal):
        """A* pathfinding algorithm implementation."""
        frontier = []
        heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heappop(frontier)[1]

            if current == goal:
                break

            for next_pos in self._get_neighbors(current):
                new_cost = cost_so_far[current] + 1

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self._heuristic(goal, next_pos)
                    heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Reconstruct path
        if goal not in came_from:
            return None

        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path

    def visualize_maze(self):
        """Visualize the generated maze and paths using matplotlib."""
        try:
            logger.info("Starting maze visualization...")
            plt.figure(figsize=(10, 10))
            plt.imshow(self.maze, cmap='binary', interpolation='nearest')

            # Find paths if not already found
            if not self.paths:
                self.find_all_paths()

            # Plot paths with different colors
            colors = ['blue', 'purple', 'orange', 'cyan']
            for i, path in enumerate(self.paths):
                if path:
                    path_y, path_x = zip(*path)
                    plt.plot(path_x, path_y, color=colors[i % len(colors)], 
                            linewidth=3, alpha=0.7, label=f'Path to Exit {i+1}')

            # Highlight start in green
            plt.scatter(self.start[1], self.start[0], color='green', s=100, label='Start')

            # Highlight exits in red
            for exit_pos in self.exits:
                plt.scatter(exit_pos[1], exit_pos[0], color='red', s=100, label='Exit')

            plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1))
            plt.axis('off')
            plt.title('Generated Maze with A* Paths\n(Black: Walls, White: Paths)')

            plt.show()
            logger.info("Maze visualization completed")
        except Exception as e:
            logger.error(f"Error visualizing maze: {e}")
            raise

# Example usage
try:
    # Create a maze generator instance
    generator = MazeGenerator(width=15, height=15, num_exits=4)
    # Generate the maze
    maze = generator.generate_maze()

    # Find and visualize paths
    generator.find_all_paths()
    generator.visualize_maze()

except Exception as e:
    logger.error(f"An error occurred: {e}")
