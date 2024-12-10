from PIL import ImageGrab
import cv2 as cv
import numpy as np
import imutils
from pytesseract import image_to_string
import time

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
    sudoku_bbox = [(puzzleCnt[0][0][0], puzzleCnt[0][0][1]), (puzzleCnt[2][0][0], puzzleCnt[2][0][1])]

    return sudoku_img, sudoku_bbox

def get_digits_tesseract(image, debug=False):
    arr = np.zeros((9,9))
    for i in range(0, 9):
        for j in range(0, 9):
            digit = image[i*55 + 5:i*55 + 50, j*55 + 5:j*55 + 50]
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
        if i == 9:
            break

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

# print(arr)

start = time.time()
solve_sudoku(arr)
end = time.time()
print("Solve sudoku: ", end - start, "s")
print("Total: ", end - start0, "s")

print(arr)
