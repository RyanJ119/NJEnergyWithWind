from PIL import Image
import numpy as np

START, UP, DOWN, LEFT, RIGHT = 0, 1, 2, 3, 4
SIZE_OF_PIXEL = 600.0

def outline(im):
    im = Image.open(im)
    pixels = np.asarray(im)
    bw = np.full((len(pixels), len(pixels[0])), False)
    first = (-1, -1)
    for r in range(len(pixels)):
        for c in range(len(pixels[0])):
            for v in pixels[r][c]:
                if not v == 255:
                    if first == (-1, -1):
                        first = (r, c)
                    bw[r][c] = True
                    break

    def getoob(y, x):
        if (0 <= y < len(pixels)) and (0 <= x < len(pixels[0])):
            return bw[y][x]
        else:
            return False

    p = first
    prevposition = position = (0.0, 0.0)
    prevdire = START
    positions = []
    while True:
        q = (getoob(p[0] - 1, p[1] - 1), getoob(p[0] - 1, p[1]),
            getoob(p[0], p[1] - 1), getoob(p[0], p[1]))
        
        blabla = 0
        for i in range(4):
            if q[i]: blabla += (0b1000 >> i)
        
        dire = START
        movev = (0.0, 0.0)
        movep = (0, 0)
        match blabla:
            case 0b1000 | 0b1100 | 0b1101:
                dire = LEFT
                movev = (-SIZE_OF_PIXEL, 0.0)
                movep = (0, -1)
            case 0b0001 | 0b0011 | 0b1011:
                dire = RIGHT
                movev = (SIZE_OF_PIXEL, 0.0)
                movep = (0, 1)
            case 0b0010 | 0b1010 | 0b1110:
                dire = DOWN
                movev = (0.0, -SIZE_OF_PIXEL)
                movep = (1, 0)
            case 0b0100 | 0b0101 | 0b0111:
                dire = UP
                movev = (0.0, SIZE_OF_PIXEL)
                movep = (-1, 0)

        if prevdire != START and dire != prevdire:
            positions.append(prevposition)
            prevposition = position

        prevdire = dire

        position = (position[0] + movev[0], position[1] + movev[1])
        p = (p[0] + movep[0], p[1] + movep[1])
        
        if p == first:
            positions.append(prevposition)
            break

    return np.array(positions)