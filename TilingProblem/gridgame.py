import time
import pygame
import numpy as np
import random

class ShapePlacementGrid:
    def __init__(self, GUI=True, render_delay_sec=0.1, gs=6, num_colored_boxes=5):
        # Constants
        self.gridSize = gs
        self.cellSize = 40
        self.screenSize = self.gridSize * self.cellSize
        self.fps = 60
        self.sleeptime = render_delay_sec

        # Basic color definitions
        self.black = (0, 0, 0)
        self.white = (255, 255, 255)

        # Color palette for shapes
        self.colors = ['#988BD0', '#504136', '#457F6E', '#F7C59F']  # Indigo, Taupe, Viridian, Peach

        # Mapping of color indices to color names (for debugging purposes)
        self.colorIdxToName = {0: "Indigo", 1: "Taupe", 2: "Viridian", 3: "Peach"}

        # Shape definitions represented by arrays
        self.shapes = [
            np.array([[1]]),  # 1x1 square
            np.array([[1, 0], [0, 1]]),  # 2x2 square with diagonal holes
            np.array([[0, 1], [1, 0]]),  # 2x2 square with diagonal holes (transpose)
            np.array([[1, 0], [0, 1], [1, 0], [0, 1]]),  # 2x4 rectangle with holes
            np.array([[0, 1], [1, 0], [0, 1], [1, 0]]),  # 2x4 rectangle with holes (transpose)
            np.array([[1, 0, 1, 0], [0, 1, 0, 1]]),      # 4x2 rectangle with alternating holes
            np.array([[0, 1, 0, 1], [1, 0, 1, 0]]),      # 4x2 rectangle with alternating holes (transpose)
            np.array([[0, 1, 0], [1, 0, 1]]),            # Sparse T-shape
            np.array([[1, 0, 1], [0, 1, 0]])             # Sparse T-shape (reversed)
        ]

        # Corresponding dimensions of the shapes
        self.shapesDims = [
            (1, 1),
            (2, 2),
            (2, 2),
            (2, 4),
            (2, 4),
            (4, 2),
            (4, 2),
            (3, 2),
            (3, 2)
        ]

        # Mapping of shape indices to shape names (for debugging purposes)
        self.shapesIdxToName = {
            0: "Square",
            1: "SquareWithHoles",
            2: "SquareWithHolesTranspose",
            3: "RectangleWithHoles",
            4: "RectangleWithHolesTranspose",
            5: "RectangleVerticalWithHoles",
            6: "RectangleVerticalWithHolesTranspose",
            7: "SparseTShape",
            8: "SparseTShapeReverse",
        }

        # Global variables (now instance attributes)
        self.screen = None
        self.clock = None
        self.grid = np.full((self.gridSize, self.gridSize), -1)
        self.currentShapeIndex = 0
        self.currentColorIndex = 0
        self.shapePos = [0, 0]
        self.placedShapes = []
        self.done = False

        # Initialize grid with random colored boxes
        self._addRandomColoredBoxes(self.grid, num_colored_boxes)

        # Initialize the graphical interface (if enabled)
        if GUI:
            pygame.init()
            self.screenSize = self.gridSize * self.cellSize
            self.screen = pygame.display.set_mode((self.screenSize, self.screenSize))
            pygame.display.set_caption("Shape Placement Grid")
            self.clock = pygame.time.Clock()

            self._refresh()

    def execute(self, command='e'):
        # Command-based environment interaction similar to Gym
        if command.lower() in ['e', 'export']:
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='e', key=ord('e'))
            try:
                pygame.event.post(new_event)
                self._refresh()
            except:
                pass
            return self.shapePos, self.currentShapeIndex, self.currentColorIndex, self.grid, self.placedShapes, self.done
        if command.lower() in ['w', 'up']:
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='w', key=ord('w'))
            try:
                pygame.event.post(new_event)
                self._refresh()
            except:
                pass
            self.shapePos[1] = max(0, self.shapePos[1] - 1)
        elif command.lower() in ['s', 'down']:
            self.shapePos[1] = min(self.gridSize - len(self.shapes[self.currentShapeIndex]), self.shapePos[1] + 1)
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='s', key=ord('s'))
            try:
                pygame.event.post(new_event)
                self._refresh()
            except:
                pass
        elif command.lower() in ['a', 'left']:
            self.shapePos[0] = max(0, self.shapePos[0] - 1)
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='a', key=ord('a'))
            try:
                pygame.event.post(new_event)
                self._refresh()
            except:
                pass
        elif command.lower() in ['d', 'right']:
            self.shapePos[0] = min(self.gridSize - len(self.shapes[self.currentShapeIndex][0]), self.shapePos[0] + 1)
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='d', key=ord('d'))
            try:
                pygame.event.post(new_event)
                self._refresh()
            except:
                pass
        elif command.lower() in ['p', 'place']:
            if self._canPlace(self.grid, self.shapes[self.currentShapeIndex], self.shapePos):
                self._placeShape(self.grid, self.shapes[self.currentShapeIndex], self.shapePos, self.currentColorIndex)
                self.placedShapes.append((self.currentShapeIndex, self.shapePos.copy(), self.currentColorIndex))
                self._exportGridState(self.grid)
                new_event = pygame.event.Event(pygame.KEYDOWN, unicode='p', key=ord('p'))
                try:
                    pygame.event.post(new_event)
                    self._refresh()
                except:
                    pass
                if self._checkGrid(self.grid):
                    self.done = True
                else:
                    self.done = False
        elif command.lower() in ['h', 'switchshape']:
            self.currentShapeIndex = (self.currentShapeIndex + 1) % len(self.shapes)
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='h', key=ord('h'))
            try:
                pygame.event.post(new_event)
                self._refresh()
            except:
                pass
        elif command.lower() in ['k', 'switchcolor']:
            self.currentColorIndex = (self.currentColorIndex + 1) % len(self.colors)
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='k', key=ord('k'))
            try:
                pygame.event.post(new_event)
                self._refresh()
            except:
                pass
        elif command.lower() in ['u', 'undo']:
            if self.placedShapes:
                lastShapeIndex, lastShapePos, lastColorIndex = self.placedShapes.pop()
                self._removeShape(self.grid, self.shapes[lastShapeIndex], lastShapePos)
                new_event = pygame.event.Event(pygame.KEYDOWN, unicode='u', key=ord('u'))
                try:
                    pygame.event.post(new_event)
                    self._refresh()
                except:
                    pass

        return self.shapePos, self.currentShapeIndex, self.currentColorIndex, self.grid, self.placedShapes, self.done

    # All other methods are private (no requirement for public)
    def _drawGrid(self, screen):
        for x in range(0, self.screenSize, self.cellSize):
            for y in range(0, self.screenSize, self.cellSize):
                rect = pygame.Rect(x, y, self.cellSize, self.cellSize)
                pygame.draw.rect(screen, self.black, rect, 1)

    def _drawShape(self, screen, shape, color, pos):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect((pos[0] + j) * self.cellSize, (pos[1] + i) * self.cellSize, self.cellSize, self.cellSize)
                    pygame.draw.rect(screen, color, rect, width=6)

    def _canPlace(self, grid, shape, pos):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    if pos[0] + j >= self.gridSize or pos[1] + i >= self.gridSize:
                        return False
                    if grid[pos[1] + i, pos[0] + j] != -1:
                        return False
        return True

    def _placeShape(self, grid, shape, pos, colorIndex):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid[pos[1] + i, pos[0] + j] = colorIndex

    def _removeShape(self, grid, shape, pos):
        for i, row in enumerate(shape):
            for j, cell in enumerate(row):
                if cell:
                    grid[pos[1] + i, pos[0] + j] = -1

    def _checkGrid(self, grid):
        # Ensure all cells are filled
        if -1 in grid:
            return False

        # Check that no adjacent cells have the same color
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                color = grid[i, j]
                if i > 0 and grid[i - 1, j] == color:
                    return False
                if i < self.gridSize - 1 and grid[i + 1, j] == color:
                    return False
                if j > 0 and grid[i, j - 1] == color:
                    return False
                if j < self.gridSize - 1 and grid[i, j + 1] == color:
                    return False

        return True

    def _exportGridState(self, grid):
        ## To export the grid for debug purposes.
        return grid

    def _importGridState(self, gridState):
        ## Can be used to import a grid for same atarting conditions from a file.
        grid = np.array([ord(char) - 65 for char in gridState]).reshape((self.gridSize, self.gridSize))
        return grid

    def _refresh(self):
        self.screen.fill(self.white)
        self._drawGrid(self.screen)

        # Draw the current state of the grid
        for i in range(self.gridSize):
            for j in range(self.gridSize):
                if self.grid[i, j] != -1:
                    rect = pygame.Rect(j * self.cellSize, i * self.cellSize, self.cellSize, self.cellSize)
                    pygame.draw.rect(self.screen, self.colors[self.grid[i, j]], rect)

        # Draw the shape that is currently selected by the user
        self._drawShape(self.screen, self.shapes[self.currentShapeIndex], self.colors[self.currentColorIndex], self.shapePos)

        pygame.display.flip()
        self.clock.tick(self.fps)
        time.sleep(self.sleeptime)

    def getAvailableColor(self, grid, x, y):
        ## Gets the possible available colors given a point on the grid.
        ## You may use this fucntion while solving the maze
        adjacent_colors = set()

        # Collect colors of adjacent cells
        if x > 0:
            adjacent_colors.add(grid[y, x - 1])
        if x < self.gridSize - 1:
            adjacent_colors.add(grid[y, x + 1])
        if y > 0:
            adjacent_colors.add(grid[y - 1, x])
        if y < self.gridSize - 1:
            adjacent_colors.add(grid[y + 1, x])

        # Find available colors that are not adjacent
        available_colors = [i for i in range(len(self.colors)) if i not in adjacent_colors]

        # Return a random color from the available colors or a fallback random color
        if available_colors:
            return random.choice(available_colors)
        else:
            return random.randint(0, len(self.colors) - 1)

    def _addRandomColoredBoxes(self, grid, num_boxes=5):
        ## Adds the random colored boxes.
        empty_positions = list(zip(*np.where(grid == -1)))
        random_positions = random.sample(empty_positions, min(num_boxes, len(empty_positions)))

        # Place random colored boxes at selected positions
        for pos in random_positions:
            color_index = self.getAvailableColor(grid, pos[1], pos[0])
            grid[pos[0], pos[1]] = color_index

    def _loop_gui(self):
        ## Main Loop for the GUI
        running = True
        while running:
            self.screen.fill(self.white)
            self._drawGrid(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    # Handle key events to move shapes and perform actions
                    if event.key == pygame.K_w:
                        self.shapePos[1] = max(0, self.shapePos[1] - 1)
                    elif event.key == pygame.K_s:
                        self.shapePos[1] = min(self.gridSize - len(self.shapes[self.currentShapeIndex]), self.shapePos[1] + 1)
                    elif event.key == pygame.K_a:
                        self.shapePos[0] = max(0, self.shapePos[0] - 1)
                    elif event.key == pygame.K_d:
                        self.shapePos[0] = min(self.gridSize - len(self.shapes[self.currentShapeIndex][0]), self.shapePos[0] + 1)
                    elif event.key == pygame.K_p:  # Place the shape on the grid
                        if self._canPlace(self.grid, self.shapes[self.currentShapeIndex], self.shapePos):
                            self._placeShape(self.grid, self.shapes[self.currentShapeIndex], self.shapePos, self.currentColorIndex)
                            self.placedShapes.append((self.currentShapeIndex, self.shapePos.copy(), self.currentColorIndex))
                            if self._checkGrid(self.grid):
                                # Calculate and display score based on the number of shapes used
                                score = (self.gridSize**2) / len(self.placedShapes)
                                print("All cells are covered with no overlaps and no adjacent same colors! Your score is:", score)
                            else:
                                print("Grid conditions not met!")
                    elif event.key == pygame.K_h:  # Switch to the next shape
                        self.currentShapeIndex = (self.currentShapeIndex + 1) % len(self.shapes)
                        currentShapeDimensions = self.shapesDims[self.currentShapeIndex]
                        xXented = self.shapePos[0] + currentShapeDimensions[0]
                        yXetended = self.shapePos[1] + currentShapeDimensions[1]

                        if (xXented > self.gridSize and yXetended > self.gridSize):
                            self.shapePos[0] -= (xXented - self.gridSize)
                            self.shapePos[1] -= (yXetended - self.gridSize)
                        elif (yXetended > self.gridSize):
                            self.shapePos[1] -= (yXetended - self.gridSize)
                        elif (xXented > self.gridSize):
                            self.shapePos[0] -= (xXented - self.gridSize)

                        print("Current shape", self.shapesIdxToName[self.currentShapeIndex])
                    elif event.key == pygame.K_k:  # Switch to the next color
                        self.currentColorIndex = (self.currentColorIndex + 1) % len(self.colors)
                    elif event.key == pygame.K_u:  # Undo the last placed shape
                        if self.placedShapes:
                            lastShapeIndex, lastShapePos, lastColorIndex = self.placedShapes.pop()
                            self._removeShape(self.grid, self.shapes[lastShapeIndex], lastShapePos)
                    elif event.key == pygame.K_e:  # Export the current grid state
                        gridState = self._exportGridState(self.grid)
                        print("Exported Grid State: \n", gridState)
                        print("Placed Shapes:", self.placedShapes)
                    elif event.key == pygame.K_i:  # Import a dummy grid state (for testing)
                        dummyGridState = self._exportGridState(np.random.randint(-1, 4, size=(self.gridSize, self.gridSize)))
                        self.grid = self._importGridState(dummyGridState)
                        self.placedShapes.clear()  # Clear history since we are importing a new state

            # Draw all placed shapes
            for i in range(self.gridSize):
                for j in range(self.gridSize):
                    if self.grid[i, j] != -1:
                        rect = pygame.Rect(j * self.cellSize, i * self.cellSize, self.cellSize, self.cellSize)
                        pygame.draw.rect(self.screen, self.colors[self.grid[i, j]], rect)

            # Draw the current shape
            self._drawShape(self.screen, self.shapes[self.currentShapeIndex], self.colors[self.currentColorIndex], self.shapePos)

            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()

    def _printGridState(self, grid):
        ## Utility method. Can be used for debugging.
        for row in grid:
            print(' '.join(f'{cell:2}' for cell in row))
        print()

    def _printControls(self):
        ## Prints the controls for manual control
        print("W/A/S/D to move the shapes.")
        print("H to change the shape.")
        print("K to change the color.")
        print("P to place the shape.")
        print("U to undo the last placed shape.")
        print("E to print the grid state from GUI to terminal.")
        print("I to import a dummy grid state.")
        print("Q to quit (terminal mode only).")
        print("Press any key to continue")

    def _main(self):
        ## Allows manual control over the environment.
        self._loop_gui()


if __name__ == "__main__":
    # Exact same functionality as original code
    # printControls() and main() now encapsulated in the class:
    game = ShapePlacementGrid(True, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
    game._printControls()
    game._main()
