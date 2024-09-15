import time
import pygame
import numpy as np
import random

# Constants, overridden by the setup() function
gridSize = 6
cellSize = 40
screenSize = gridSize * cellSize
fps = 60
sleeptime = 0.1

# Basic color definitions
black = (0, 0, 0)
white = (255, 255, 255)

# Color palette for shapes
colors = ['#988BD0', '#504136', '#457F6E', '#F7C59F']  # Indigo, Taupe, Viridian, Peach

# Mapping of color indices to color names (for debugging purposes)
colorIdxToName = {0: "Indigo", 1: "Taupe", 2: "Viridian", 3: "Peach"}

# Shape definitions represented by arrays
shapes = [
    np.array([[1]]),  # 1x1 square
    np.array([[1, 0], [0, 1]]),  # 2x2 square with diagonal holes
    np.array([[0, 1], [1, 0]]),  # 2x2 square with diagonal holes (transpose)
    np.array([[1, 0], [0, 1], [1, 0], [0, 1]]),  # 2x4 rectangle with holes
    np.array([[0, 1], [1, 0], [0, 1], [1, 0]]),  # 2x4 rectangle with holes (transpose)
    np.array([[1, 0, 1, 0], [0, 1, 0, 1]]),  # 4x2 rectangle with alternating holes
    np.array([[0, 1, 0, 1], [1, 0, 1, 0]]),  # 4x2 rectangle with alternating holes (transpose)
    np.array([[0, 1, 0], [1, 0, 1]]),  # Sparse T-shape
    np.array([[1, 0, 1], [0, 1, 0]])  # Sparse T-shape (reversed)
]

# Corresponding dimensions of the shapes
shapesDims = [
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
shapesIdxToName = {
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

# Global variables
screen = None
clock = None
grid = None
currentShapeIndex = None
currentColorIndex = None
shapePos = None
placedShapes = None

# Function to draw the grid on the screen
def drawGrid(screen):
    for x in range(0, screenSize, cellSize):
        for y in range(0, screenSize, cellSize):
            rect = pygame.Rect(x, y, cellSize, cellSize)
            pygame.draw.rect(screen, black, rect, 1)

# Function to draw the current shape at a given position with a specified color
def drawShape(screen, shape, color, pos):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((pos[0] + j) * cellSize, (pos[1] + i) * cellSize, cellSize, cellSize)
                pygame.draw.rect(screen, color, rect, width=6)

# Function to check if a shape can be placed at a specified position on the grid
def canPlace(grid, shape, pos):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                # Check if the shape fits within the grid bounds
                if pos[0] + j >= gridSize or pos[1] + i >= gridSize:
                    return False
                # Check if the position on the grid is already occupied
                if grid[pos[1] + i, pos[0] + j] != -1:
                    return False
    return True

# Function to place a shape on the grid at a given position
def placeShape(grid, shape, pos, colorIndex):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                grid[pos[1] + i, pos[0] + j] = colorIndex

# Function to remove a shape from the grid (used for undo operations)
def removeShape(grid, shape, pos):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                grid[pos[1] + i, pos[0] + j] = -1

# Function to check if the grid is fully filled and satisfies the color adjacency constraint.
# Add additional constraints if necessary. 
def checkGrid(grid):
    # Ensure all cells are filled
    if -1 in grid:
        return False

    # Check that no adjacent cells have the same color
    for i in range(gridSize):
        for j in range(gridSize):
            color = grid[i, j]
            if i > 0 and grid[i - 1, j] == color:
                return False
            if i < gridSize - 1 and grid[i + 1, j] == color:
                return False
            if j > 0 and grid[i, j - 1] == color:
                return False
            if j < gridSize - 1 and grid[i, j + 1] == color:
                return False

    return True

# Utility function to return the current state of the grid
def exportGridState(grid):
    return grid

# Function to import a grid state (from a file or predefined state)
def importGridState(gridState):
    grid = np.array([ord(char) - 65 for char in gridState]).reshape((gridSize, gridSize))
    return grid

# Function to refresh the screen after an action (such as moving or placing a shape)
def refresh():
    global screen, gridSize, grid, cellSize, colors, currentColorIndex, currentShapeIndex, shapePos, shapes, sleeptime
    screen.fill(white)
    drawGrid(screen)

    # Draw the current state of the grid
    for i in range(gridSize):
        for j in range(gridSize):
            if grid[i, j] != -1:
                rect = pygame.Rect(j * cellSize, i * cellSize, cellSize, cellSize)
                pygame.draw.rect(screen, colors[grid[i, j]], rect)

    # Draw the shape that is currently selected by the user
    drawShape(screen, shapes[currentShapeIndex], colors[currentColorIndex], shapePos)

    pygame.display.flip()
    clock.tick(fps)
    time.sleep(sleeptime)

# Utility function to get a random color that is not adjacent to the current position
def getAvailableColor(grid, x, y):
    adjacent_colors = set()

    # Collect colors of adjacent cells
    if x > 0:
        adjacent_colors.add(grid[y, x - 1])
    if x < gridSize - 1:
        adjacent_colors.add(grid[y, x + 1])
    if y > 0:
        adjacent_colors.add(grid[y - 1, x])
    if y < gridSize - 1:
        adjacent_colors.add(grid[y + 1, x])

    # Find available colors that are not adjacent
    available_colors = [i for i in range(len(colors)) if i not in adjacent_colors]

    # Return a random color from the available colors or a fallback random color
    if available_colors:
        return random.choice(available_colors)
    else:
        return random.randint(0, len(colors) - 1)

# Function to add randomly colored boxes to the grid at the start of the game
def addRandomColoredBoxes(grid, num_boxes=5):
    empty_positions = list(zip(*np.where(grid == -1)))
    random_positions = random.sample(empty_positions, min(num_boxes, len(empty_positions)))

    # Place random colored boxes at selected positions
    for pos in random_positions:
        color_index = getAvailableColor(grid, pos[1], pos[0])
        grid[pos[0], pos[1]] = color_index

# Function to set up the environment (optionally with a graphical interface)
def setup(GUI=True, render_delay_sec=0.1, gs=6, num_colored_boxes=5):
    global gridSize, screen, clock, grid, currentShapeIndex, currentColorIndex, shapePos, placedShapes, sleeptime, screenSize
    gridSize = gs
    sleeptime = render_delay_sec
    grid = np.full((gridSize, gridSize), -1)
    currentShapeIndex = 0
    currentColorIndex = 0
    shapePos = [0, 0]
    placedShapes = []

    # Add random colored boxes at the beginning
    addRandomColoredBoxes(grid, num_colored_boxes)

    # Initialize the graphical interface (if enabled)
    if GUI:
        pygame.init()
        screenSize = gridSize * cellSize  # Calculate screen size based on the grid size
        screen = pygame.display.set_mode((screenSize, screenSize))
        pygame.display.set_caption("Shape Placement Grid")
        clock = pygame.time.Clock()

        refresh()

# Main loop for interacting with the GUI environment
def loop_gui():
    global currentShapeIndex, currentColorIndex, shapePos, grid, placedShapes
    running = True
    while running:
        screen.fill(white)
        drawGrid(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                # Handle key events to move shapes and perform actions
                if event.key == pygame.K_w:
                    shapePos[1] = max(0, shapePos[1] - 1)
                elif event.key == pygame.K_s:
                    shapePos[1] = min(gridSize - len(shapes[currentShapeIndex]), shapePos[1] + 1)
                elif event.key == pygame.K_a:
                    shapePos[0] = max(0, shapePos[0] - 1)
                elif event.key == pygame.K_d:
                    shapePos[0] = min(gridSize - len(shapes[currentShapeIndex][0]), shapePos[0] + 1)
                elif event.key == pygame.K_p:  # Place the shape on the grid
                    if canPlace(grid, shapes[currentShapeIndex], shapePos):
                        placeShape(grid, shapes[currentShapeIndex], shapePos, currentColorIndex)
                        placedShapes.append((currentShapeIndex, shapePos.copy(), currentColorIndex))
                        if checkGrid(grid):
                            # Calculate and display score based on the number of shapes used
                            score = (gridSize**2) / len(placedShapes)
                            print("All cells are covered with no overlaps and no adjacent same colors! Your score is:", score)
                        else:
                            print("Grid conditions not met!")
                elif event.key == pygame.K_h:  # Switch to the next shape
                    currentShapeIndex = (currentShapeIndex + 1) % len(shapes)
                    currentShapeDimensions = shapesDims[currentShapeIndex]
                    xXented = shapePos[0] + currentShapeDimensions[0]
                    yXetended = shapePos[1] + currentShapeDimensions[1]

                    if (xXented > gridSize and yXetended > gridSize):
                        # Adjust position if the shape exceeds the grid boundary
                        shapePos[0] -= (xXented - gridSize)
                        shapePos[1] -= (yXetended - gridSize)
                    if (yXetended > gridSize):
                        shapePos[1] -= (yXetended - gridSize)
                    if (xXented > gridSize):
                        shapePos[0] -= (xXented - gridSize)

                    print("Current shape", shapesIdxToName[currentShapeIndex])
                elif event.key == pygame.K_k:  # Switch to the next color
                    currentColorIndex = (currentColorIndex + 1) % len(colors)
                elif event.key == pygame.K_u:  # Undo the last placed shape
                    if placedShapes:
                        lastShapeIndex, lastShapePos, lastColorIndex = placedShapes.pop()
                        removeShape(grid, shapes[lastShapeIndex], lastShapePos)
                elif event.key == pygame.K_e:  # Export the current grid state
                    gridState = exportGridState(grid)
                    print("Exported Grid State: \n", gridState)
                    print("Placed Shapes:", placedShapes)
                elif event.key == pygame.K_i:  # Import a dummy grid state (for testing)
                    dummyGridState = exportGridState(np.random.randint(-1, 4, size=(gridSize, gridSize)))
                    grid = importGridState(dummyGridState)
                    placedShapes.clear()  # Clear history since we are importing a new state

        # Draw all placed shapes
        for i in range(gridSize):
            for j in range(gridSize):
                if grid[i, j] != -1:
                    rect = pygame.Rect(j * cellSize, i * cellSize, cellSize, cellSize)
                    pygame.draw.rect(screen, colors[grid[i, j]], rect)

        # Draw the current shape
        drawShape(screen, shapes[currentShapeIndex], colors[currentColorIndex], shapePos)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()

# Command-based environment interaction similar to Gym
def execute(command='e'):
    global currentShapeIndex, currentColorIndex, shapePos, grid, placedShapes
    done = False
    if command.lower() in ['e', 'export']:
        new_event = pygame.event.Event(pygame.KEYDOWN, unicode='e', key=ord('e'))
        try:
            pygame.event.post(new_event)
            refresh()
        except:
            pass
        return shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done
    if command.lower() in ['w', 'up']:
        new_event = pygame.event.Event(pygame.KEYDOWN, unicode='w', key=ord('w'))
        try:
            pygame.event.post(new_event)
            refresh()
        except:
            pass
        shapePos[1] = max(0, shapePos[1] - 1)
    elif command.lower() in ['s', 'down']:
        shapePos[1] = min(gridSize - len(shapes[currentShapeIndex]), shapePos[1] + 1)
        new_event = pygame.event.Event(pygame.KEYDOWN, unicode='s', key=ord('s'))
        try:
            pygame.event.post(new_event)
            refresh()
        except:
            pass
    elif command.lower() in ['a', 'left']:
        shapePos[0] = max(0, shapePos[0] - 1)
        new_event = pygame.event.Event(pygame.KEYDOWN, unicode='a', key=ord('a'))
        try:
            pygame.event.post(new_event)
            refresh()
        except:
            pass
    elif command.lower() in ['d', 'right']:
        shapePos[0] = min(gridSize - len(shapes[currentShapeIndex][0]), shapePos[0] + 1)
        new_event = pygame.event.Event(pygame.KEYDOWN, unicode='d', key=ord('d'))
        try:
            pygame.event.post(new_event)
            refresh()
        except:
            pass
    elif command.lower() in ['p', 'place']:
        if canPlace(grid, shapes[currentShapeIndex], shapePos):
            placeShape(grid, shapes[currentShapeIndex], shapePos, currentColorIndex)
            placedShapes.append((currentShapeIndex, shapePos.copy(), currentColorIndex))
            exportGridState(grid)
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='p', key=ord('p'))
            try:
                pygame.event.post(new_event)
                refresh()
            except:
                pass
            if checkGrid(grid):
                done = True
            else:
                done = False
    elif command.lower() in ['h', 'switchshape']:
        currentShapeIndex = (currentShapeIndex + 1) % len(shapes)
        new_event = pygame.event.Event(pygame.KEYDOWN, unicode='h', key=ord('h'))
        try:
            pygame.event.post(new_event)
            refresh()
        except:
            pass
    elif command.lower() in ['k', 'switchcolor']:
        currentColorIndex = (currentColorIndex + 1) % len(colors)
        new_event = pygame.event.Event(pygame.KEYDOWN, unicode='k', key=ord('k'))
        try:
            pygame.event.post(new_event)
            refresh()
        except:
            pass
    elif command.lower() in ['u', 'undo']:
        if placedShapes:
            lastShapeIndex, lastShapePos, lastColorIndex = placedShapes.pop()
            removeShape(grid, shapes[lastShapeIndex], lastShapePos)
            new_event = pygame.event.Event(pygame.KEYDOWN, unicode='u', key=ord('u'))
            try:
                pygame.event.post(new_event)
                refresh()
            except:
                pass

    return shapePos, currentShapeIndex, currentColorIndex, grid, placedShapes, done

# Debug function to print the grid state
def printGridState(grid):
    for row in grid:
        print(' '.join(f'{cell:2}' for cell in row))
    print()

# Main function to initialize the environment and start the game loop
def main():
    setup(True, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
    loop_gui()

# Function to print user controls and instructions
def printControls():
    print("W/A/S/D to move the shapes.")
    print("H to change the shape.")
    print("K to change the color.")
    print("P to place the shape.")
    print("U to undo the last placed shape.")
    print("E to print the grid state from GUI to terminal.")
    print("I to import a dummy grid state.")
    print("Q to quit (terminal mode only).")
    print("Press any key to continue")

if __name__ == "__main__":
    printControls()
    main()
