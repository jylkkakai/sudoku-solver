from PIL import ImageGrab
import cv2 as cv
import numpy as np
import imutils
from pytesseract import image_to_string
import time
import pyautogui as pg

def find_sudoku(image, debug=False):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.GaussianBlur(gray, (7, 7), 1)

    thresh = cv.adaptiveThreshold(blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    thresh = cv.bitwise_not(thresh)

    cnts = cv.findContours(thresh.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv.contourArea, reverse=True)
    puzzleCnt = None

    for c in cnts:
        peri = cv.arcLength(c, True)
        approx = cv.approxPolyDP(c, 0.02 * peri, True)

        # Find contours bigger than 300x300
        if len(approx) == 4 and approx[2][0][0] - approx[0][0][0] > 300 and approx[1][0][1] - approx[3][0][1] > 300:
            puzzleCnt = approx
            break
        
    if puzzleCnt is None:
        raise Exception(("Could not find Sudoku puzzle outline. "
            "Try debugging your thresholding and contour steps."))

    if debug:
        output = image.copy()
        cv.drawContours(output, [puzzleCnt], -1, (0, 255, 0), 2)
        cv.imshow("Puzzle Outline", output)
        cv.waitKey(0)
        
    sudoku_img = image[puzzleCnt[0][0][1]:puzzleCnt[2][0][1], puzzleCnt[0][0][0]:puzzleCnt[2][0][0]]
    sudoku_bbox = [int(puzzleCnt[0][0][0]), int(puzzleCnt[0][0][1]), int(puzzleCnt[2][0][0]), int(puzzleCnt[2][0][1])]

    return sudoku_img, sudoku_bbox

def get_digits_tesseract(image, debug=False):
    x_step = int(image.shape[0]/9)
    y_step = int(image.shape[1]/9)
    arr = np.zeros((9,9), dtype=int)
    for i in range(0, 9):
        for j in range(0, 9):
            digit = image[i*x_step + 5:i*x_step + x_step - 5, j*y_step + 5:j*y_step + y_step - 5]
            sdigit = image_to_string(digit, config="--psm 10")[0]
            arr[i, j] = 0 if sdigit == "_" else int(sdigit)
            if debug:
                cv.imshow("digit", digit)
                cv.waitKey(0)
    return arr

def solve_sudoku(puzzle, debug=False):
    fixed_nums = np.greater(puzzle, np.zeros((9,9)))
    i = 0
    j = 0
    while True:
        if debug:
            print(i, j)
            print(puzzle)
        if fixed_nums[i, j]:
            if j == 8:
                i += 1
                j = 0
            else:
                j += 1
            if i >= 9:
                break
            continue

        if puzzle[i, j] == 9:
            while True:
                if debug:
                    print("\t", i, j)
                    print("\t", puzzle)
                if puzzle[i, j] == 9 and not fixed_nums[i, j]:
                    puzzle[i, j] = 0
                elif puzzle[i, j] < 9 and not fixed_nums[i, j]:
                    break

                if i == 0 and j == 0:
                    raise Exception(("No solution."))
                if j == 0:
                    i -= 1
                    j = 8
                else:
                    j -= 1

        box_i = int(i/3)*3
        box_j = int(j/3)*3
        if puzzle[i, j] + 1 not in puzzle[i, :] and puzzle[i, j] + 1 not in puzzle[:, j] and puzzle[i, j] + 1 not in puzzle[box_i:box_i+3, box_j:box_j+3]:
            puzzle[i, j] += 1
            if j == 8:
                i += 1
                j = 0
            else:
                j += 1
        else:
            puzzle[i, j] += 1

        if i >= 9:
            break

    return fixed_nums

# def fill_puzzle(solution, fixed_nums, bbox):
#     # print(solution)
#     x_step = int((bbox[2] - bbox[0])/9)
#     y_step = int((bbox[3] - bbox[1])/9)
#     x_offset = int(x_step/2)
#     y_offset = int(y_step/2)
#
#     for i in range(0, 9):
#         for j in range(0, 9):
#             if not fixed_nums[i, j]:
#                 pg.click(bbox[0] + j*x_step + x_offset, bbox[1] + i*y_step + y_offset)
#                 time.sleep(0.01)
#                 pg.press(str(solution[i, j])[0])

def fill_puzzle(solution, fixed_nums, bbox):
    x_step = int((bbox[2] - bbox[0])/9)
    y_step = int((bbox[3] - bbox[1])/9)
    x_offset = int(x_step/2)
    y_offset = int(y_step/2)

    i = 0
    j = 0
    pg.click(bbox[0] + x_offset, bbox[1] + y_offset)

    left = i%2 
    while True:
        pg.press(str(solution[i, j])[0])
        dir = 'right'

        if not left and j < 8:
            j += 1
            dir = 'right' 
        elif (j == 8 and not left) or (j == 0 and left):
            i += 1
            left = i%2 
            dir = 'down' 
        else:
            j -= 1
            dir = 'left' 

        pg.press(dir)
        if i == 9:
            break


def new_game(bbox):
    time.sleep(3.0)
    pg.click("new_game.png")
    time.sleep(0.5)
    pg.click("restart.png")
    time.sleep(1.0)
    pg.click(bbox[0] + 20, bbox[1] + 20)
    time.sleep(1.0)
    pg.click()
    time.sleep(0.5)
    pg.click()

try:
    pg.PAUSE = 0.020
    while True:
        start0 = time.time()
        screen_shot = ImageGrab.grab()
        end = time.time()
        print("Imagegrab: ", end - start0, "s")

        start = time.time()
        sudoku, bbox = find_sudoku(np.array(screen_shot))
        end = time.time()
        print("Find sudoku: ", end - start, "s")

        start = time.time()
        arr = get_digits_tesseract(sudoku)
        end = time.time()
        print("Get digits: ", end - start, "s")

        start = time.time()
        fixed_nums = solve_sudoku(arr)
        end = time.time()
        print("Solve sudoku: ", end - start, "s")
        # print(arr)

        start = time.time()
        fixed_nums = fill_puzzle(arr, fixed_nums, bbox)
        end = time.time()
        print("Fill sudoku: ", end - start, "s")
        print("Total: ", end - start0, "s")

        new_game(bbox)

except KeyboardInterrupt:
    pass
