from PIL import ImageGrab
import cv2 as cv
import numpy as np
import imutils
from pytesseract import image_to_string
import easyocr

screen_shot = ImageGrab.grab()

def find_sudoku(image, debug=False):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    # blurred = gray
    # blurred = cv.GaussianBlur(gray, (3, 3), 1)
    blurred = cv.GaussianBlur(gray, (7, 7), 1)

    thresh = cv.adaptiveThreshold(blurred, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 11, 2)
    thresh = cv.bitwise_not(thresh)

    # cv.imshow("gray", thresh)
    # cv.waitKey(0)
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
        
    # return thresh[puzzleCnt[0][0][1]:puzzleCnt[2][0][1], puzzleCnt[0][0][0]:puzzleCnt[2][0][0]]
    return image[puzzleCnt[0][0][1]:puzzleCnt[2][0][1], puzzleCnt[0][0][0]:puzzleCnt[2][0][0]]

def get_digits_tesseract(image, debug=False):
    arr = np.zeros((9,9))
    for i in range(0, 9):
        for j in range(0, 9):
            digit = image[i*55 + 5:i*55 + 50, j*55 + 5:j*55 + 50]
            sdigit = image_to_string(digit, config="--psm 10")[0]
            # print(0 if sdigit == "_" else int(sdigit),  end=" ")
            arr[i, j] = 0 if sdigit == "_" else int(sdigit)
            if debug:
                cv.imshow("digit", digit)
                cv.waitKey(0)
        # print()
    return arr
#
# def get_digits_easyocr(image, debug=False):
#     arr = np.zeros((9,9))
#     reader = easyocr.Reader(['ch_sim','en'])
#     for i in range(0, 9):
#         for j in range(0, 9):
#             digit = image[i*55 + 5:i*55 + 50, j*55 + 5:j*55 + 50]
#             sdigit = reader.readtext(digit, detail=0)
#             print(sdigit)
#             # sdigit = image_to_string(digit, config="--psm 10")[0]
#             # print(0 if sdigit == "_" else int(sdigit),  end=" ")
#             arr[i, j] = 0 if sdigit == "_" else int(sdigit)
#             if debug:
#                 cv.imshow("digit", digit)
#                 cv.waitKey(0)
#         # print()
#     return arr



sudoku = find_sudoku(np.array(screen_shot))
print("find_sudoku finished..")
# print(image_to_string(cv.cvtColor(sudoku, cv.COLOR_BGR2RGB)))
arr = get_digits_tesseract(sudoku)
# arr = get_digits_easyocr(sudoku)
print(arr)
# sudoku = find_sudoku(np.array(screen_shot), debug=True)

# cv.imshow("gray", sudoku)
# cv.waitKey(0)

# screen_shot.show("shot")
