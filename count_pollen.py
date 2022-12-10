import numpy as np
import cv2
import matplotlib.pyplot as plt


def count_pollen(mainImg, outputImgName, cannyEdgeLow, cannyEdgeHigh, houghParam2, minDist, minRad, maxRad):
    # read image
    image = cv2.imread(mainImg)

    # gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # median filter for smoothing
    median = cv2.medianBlur(gray, 5)

    # Contrast Limited Adaptive Histogram Equalization
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    claheNorm = clahe.apply(median)

    # contrast stretching
    # Function to map each intensity level to output intensity level.

    def pixelVal(pix, r1, s1, r2, s2):
        if (0 <= pix and pix <= r1):
            return (s1 / r1) * pix
        elif (r1 < pix and pix <= r2):
            return ((s2 - s1) / (r2 - r1)) * (pix - r1) + s1
        else:
            return ((255 - s2) / (255 - r2)) * (pix - r2) + s2

    # Define parameters.
    r1 = 100
    s1 = 0
    r2 = 100
    s2 = 255

    # Vectorize the function to apply it to each value in the Numpy array.
    pixelVal_vec = np.vectorize(pixelVal)
    contrast_stretched_blurM = pixelVal_vec(claheNorm, r1, s1, r2, s2)
    cv2.imwrite('contrast_stretch_blurM.png', contrast_stretched_blurM)
    imageContrast = cv2.imread("contrast_stretch_blurM.png")

    # edge detection using canny edge detector
    edge = cv2.Canny(imageContrast, cannyEdgeLow, cannyEdgeHigh)

    # morphological operations
    kernel = np.ones((5, 5), np.uint8)

    closing = cv2.morphologyEx(edge, cv2.MORPH_CLOSE, kernel)

    dilation = cv2.dilate(closing, kernel, iterations=1)

    # Otsu's thresholding
    ret4, th4 = cv2.threshold(
        dilation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Initialize the list
    Cell_count, x_count, y_count = [], [], []

    # read original image, to display the circle and center detection 
    display = cv2.imread(mainImg)

    # hough transform with modified circular parameters
    circles = cv2.HoughCircles(th4, cv2.HOUGH_GRADIENT, 1.75, minDist,
                               param1=cannyEdgeHigh, param2=houghParam2, minRadius=minRad, maxRadius=maxRad)

    # circle detection and labeling using hough transformation
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            cv2.circle(display, (x, y), r, (0, 255, 0), 2)
            cv2.rectangle(display, (x - 2, y - 2),
                          (x + 2, y + 2), (0, 128, 255), -1)
            Cell_count.append(r)
            x_count.append(x)
            y_count.append(y)
        # show the output image
        cv2.imwrite(outputImgName, display)

    # display the count of pollen
    print(len(Cell_count))
    # Total number of radius
    print(Cell_count)
    # X co-ordinate of circle
    print(x_count)
    # Y co-ordinate of circle
    print(y_count)

    # image write statements:
    # uncomment if you want to see step-by-step process
    cv2.imwrite('claheNorm.png', claheNorm)
    cv2.imwrite('edge.png', edge)
    cv2.imwrite("closing.png", closing)
    cv2.imwrite("dilation.png", dilation)
    cv2.imwrite("th4.png", th4)


mainImg = "practice_image_1.jpg"
outputImgName = "main_output.png"

# params to be modified to detect pollen
cannyEdgeLow = 100
cannyEdgeHigh = 230
houghParam2 = 33  # controls tuning of circle detection

minDist = 70    # min distance between circles
minRad = 10     # min radius of circles
maxRad = 60     # max radius of circles

count_pollen(mainImg, outputImgName, cannyEdgeLow,
             cannyEdgeHigh, houghParam2, minDist, minRad, maxRad)
