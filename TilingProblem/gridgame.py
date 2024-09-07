import time
import pygame
import numpy as np
import random

# Constants, overridden by setup()
gridSize = 6
cellSize = 40
screenSize = gridSize * cellSize
fps = 60
sleeptime = 0.1

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

# Colors for the shapes
colors = ['#988BD0', '#504136', '#457F6E', '#F7C59F']  # Indigo, Taupe, Viridian, Peach

colorIdxToName = {0: "Indigo", 1: "Taupe", 2: "Viridian", 3: "Peach"}

# Shapes
shapes = [
    np.array([[1]]),  # 1x1 square
    np.array([[1, 0], [0, 1]]),  # 2x2 square with holes
    np.array([[0, 1], [1, 0]]),  # 2x2 square with holes
    np.array([[1, 0], [0, 1], [1, 0], [0, 1]]),  # 2x4 rectangle with holes
    np.array([[0, 1], [1, 0], [0, 1], [1, 0]]),  # 2x4 rectangles with holes
    np.array([[1, 0, 1, 0], [0, 1, 0, 1]]),  # 4x2 rectangle with holes
    np.array([[0, 1, 0, 1], [1, 0, 1, 0]]),  # 4x2 rectangles with holes
    np.array([[0, 1, 0], [1, 0, 1]]),  # T shape with holes
    np.array([[1, 0, 1], [0, 1, 0]])  # T shape with holes
]

shapesDims = [
    (1,1),
    (2,2),
    (2,2),
    (2,4),
    (2,4),
    (4,2),
    (4,2),
    (3,2),
    (3,2)
]
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


def drawGrid(screen):
    for x in range(0, screenSize, cellSize):
        for y in range(0, screenSize, cellSize):
            rect = pygame.Rect(x, y, cellSize, cellSize)
            pygame.draw.rect(screen, black, rect, 1)


def drawShape(screen, shape, color, pos):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                rect = pygame.Rect((pos[0] + j) * cellSize, (pos[1] + i) * cellSize, cellSize, cellSize)
                pygame.draw.rect(screen, color, rect, width=6)


def canPlace(grid, shape, pos):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                if pos[0] + j >= gridSize or pos[1] + i >= gridSize:
                    return False
                if grid[pos[1] + i, pos[0] + j] != -1:
                    return False
    return True


def placeShape(grid, shape, pos, colorIndex):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                grid[pos[1] + i, pos[0] + j] = colorIndex


def removeShape(grid, shape, pos):
    for i, row in enumerate(shape):
        for j, cell in enumerate(row):
            if cell:
                grid[pos[1] + i, pos[0] + j] = -1


def checkGrid(grid):
    ## Check if all the points are actually covered.
    if -1 in grid:
        return False

    ## Check if all the adjacent colors are different.
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


def exportGridState(grid):
    return grid
    # return ''.join(chr(cell + 65) for row in grid for cell in row)


def importGridState(gridState):
    grid = np.array([ord(char) - 65 for char in gridState]).reshape((gridSize, gridSize))
    return grid

def refresh():
    global screen, gridSize, grid, cellSize, colors, currentColorIndex, currentShapeIndex, shapePos, shapes, sleeptime
    screen.fill(white)
    drawGrid(screen)

    for i in range(gridSize):
        for j in range(gridSize):
            if grid[i, j] != -1:
                rect = pygame.Rect(j * cellSize, i * cellSize, cellSize, cellSize)
                pygame.draw.rect(screen, colors[grid[i, j]], rect)

    drawShape(screen, shapes[currentShapeIndex], colors[currentColorIndex], shapePos)

    pygame.display.flip()
    clock.tick(fps)
    time.sleep(sleeptime)


def getAvailableColor(grid, x, y):
    """Returns a random color index that is not adjacent to the current position (x, y)."""
    adjacent_colors = set()

    if x > 0:
        adjacent_colors.add(grid[y, x - 1])
    if x < gridSize - 1:
        adjacent_colors.add(grid[y, x + 1])
    if y > 0:
        adjacent_colors.add(grid[y - 1, x])
    if y < gridSize - 1:
        adjacent_colors.add(grid[y + 1, x])

    available_colors = [i for i in range(len(colors)) if i not in adjacent_colors]

    if available_colors:
        return random.choice(available_colors)
    else:
        return random.randint(0, len(colors) - 1)


def addRandomColoredBoxes(grid, num_boxes=5):
    empty_positions = list(zip(*np.where(grid == -1)))
    random_positions = random.sample(empty_positions, min(num_boxes, len(empty_positions)))

    for pos in random_positions:
        color_index = getAvailableColor(grid, pos[1], pos[0])
        grid[pos[0], pos[1]] = color_index


def setup(GUI=True, render_delay_sec=0.1, gs=6, num_colored_boxes=5):
    global gridSize, screen, clock, grid, currentShapeIndex, currentColorIndex, shapePos, placedShapes, sleeptime
    gridSize = gs
    sleeptime = render_delay_sec
    grid = np.full((gridSize, gridSize), -1)
    currentShapeIndex = 0
    currentColorIndex = 0
    shapePos = [0, 0]
    placedShapes = []

    # Add random colored boxes
    addRandomColoredBoxes(grid, num_colored_boxes)

    if GUI:
        pygame.init()
        screen = pygame.display.set_mode((screenSize, screenSize))
        pygame.display.set_caption("Shape Placement Grid")
        clock = pygame.time.Clock()

        refresh()


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
                if event.key == pygame.K_w:
                    shapePos[1] = max(0, shapePos[1] - 1)
                elif event.key == pygame.K_s:
                    shapePos[1] = min(gridSize - len(shapes[currentShapeIndex]), shapePos[1] + 1)
                elif event.key == pygame.K_a:
                    shapePos[0] = max(0, shapePos[0] - 1)
                elif event.key == pygame.K_d:
                    shapePos[0] = min(gridSize - len(shapes[currentShapeIndex][0]), shapePos[0] + 1)
                elif event.key == pygame.K_p:
                    if canPlace(grid, shapes[currentShapeIndex], shapePos):
                        placeShape(grid, shapes[currentShapeIndex], shapePos, currentColorIndex)
                        placedShapes.append((currentShapeIndex, shapePos.copy(), currentColorIndex))
                        if checkGrid(grid):
                            ## Also calculate the score. 
                            ## The score is inversely proportional to the number of shapes that are used.
                            score = (gridSize**2)/placedShapes
                            print("All cells are covered with no overlaps and no adjacent same colors! Your score is:", score)
                        else:
                            print("Grid conditions not met!")
                elif event.key == pygame.K_h:
                    currentShapeIndex = (currentShapeIndex + 1) % len(shapes)
                    currentShapeDimensions = shapesDims[currentShapeIndex]
                    xXented = shapePos[0] + currentShapeDimensions[0]
                    yXetended = shapePos[1] + currentShapeDimensions[1]

                    if (xXented > gridSize and yXetended > gridSize):
                        ## Move the current pos to the top left
                        shapePos[0] -= (xXented-gridSize) 
                        shapePos[1] -= (yXetended-gridSize) 

                    if (yXetended > gridSize):
                        ## Move the current pos to the top 
                        shapePos[1] -= (yXetended-gridSize) 

                    if (xXented > gridSize):
                        ## Move the current pos to the left
                        shapePos[0] -= (xXented-gridSize) 

                    print("Current shape", shapesIdxToName[currentShapeIndex])
                elif event.key == pygame.K_k:
                    currentColorIndex = (currentColorIndex + 1) % len(colors)
                elif event.key == pygame.K_u:  # Undo the last placed shape
                    if placedShapes:
                        lastShapeIndex, lastShapePos, lastColorIndex = placedShapes.pop()
                        removeShape(grid, shapes[lastShapeIndex], lastShapePos)
                elif event.key == pygame.K_e:  # Export the grid state
                    gridState = exportGridState(grid)
                    print("Exported Grid State: \n", gridState)
                    print("Placed Shapes:", placedShapes)
                elif event.key == pygame.K_i:  # Import the grid state, not needed for us.
                    # Dummy grid state for testing
                    dummyGridState = exportGridState(np.random.randint(-1, 4, size=(gridSize, gridSize)))
                    grid = importGridState(dummyGridState)
                    placedShapes.clear()  # Clear history since we are importing a new state

        # Draw already placed shapes
        for i in range(gridSize):
            for j in range(gridSize):
                if grid[i, j] != -1:
                    rect = pygame.Rect(j * cellSize, i * cellSize, cellSize, cellSize)
                    pygame.draw.rect(screen, colors[grid[i, j]], rect)

        drawShape(screen, shapes[currentShapeIndex], colors[currentColorIndex], shapePos)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


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
        return grid, placedShapes, done
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


def printGridState(grid):
    for row in grid:
        print(' '.join(f'{cell:2}' for cell in row))
    print()


def main():
    setup(True, render_delay_sec=0.1, gs=6, num_colored_boxes=5)
    loop_gui()


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
