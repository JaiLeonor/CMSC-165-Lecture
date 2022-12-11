import numpy as np
import cv2
import matplotlib.pyplot as plt
import cmath

def remove_text(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    thresh = cv2.threshold(gray, 155, 255, cv2.THRESH_BINARY)[1]

    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_DILATE, kernel)

    mask = np.zeros_like(gray, np.uint8)
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    dimensions = (0, 0)

    for cnt in cnts:
        area = cv2.contourArea(cnt)
        if area > 1000:
            perimeter = cv2.arcLength(cnt, True)

            #Calculate dimensions of the rectangle (ax**2 + bx + c = 0)
            b = -perimeter / 2

            # calculate the discriminant
            d = (b ** 2) - (4 * area)

            # find two solutions
            sol1 = (-b - cmath.sqrt(d)) / 2
            sol2 = (-b + cmath.sqrt(d)) / 2

            dimensions = (sol1.real, sol2.real)

            cv2.drawContours(mask,[cnt],0,255,-1)

    result = cv2.inpaint(image,mask,3,cv2.INPAINT_NS)

    cv2.imwrite('remove_text.png', result)

    return result, dimensions

def count_pollen(mainImg, outputImgName, cannyEdgeLow, cannyEdgeHigh, houghParam2, minDist, minRad, maxRad, classThreshold):
    # read image
    image = cv2.imread(mainImg)

    #Remove text
    image, dimensions = remove_text(image)

    # print(dimensions)

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

    #Classify pollens
    def classify_pollen(image, x, y, r, threshold):
        circle_img = np.zeros((image.shape[0], image.shape[1]), np.uint8)
        cv2.circle(circle_img, (x, y,), r, (255, 255, 255), -1)
        if cv2.mean(image, mask=circle_img)[0] > threshold: 
            return 1
        return 0

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
    ret4, th4 = cv2.threshold(dilation, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    remove_text(image)

    # Initialize the list
    pollen_count, x_count, y_count, pollen_class = [], [], [], []

    # read original image, to display the circle and center detection 
    display = cv2.imread(mainImg)

    # hough transform with modified circular parameters
    circles = cv2.HoughCircles(th4, cv2.HOUGH_GRADIENT, 1.75, minDist, param1=cannyEdgeHigh, param2=houghParam2, minRadius=minRad, maxRadius=maxRad)

    # circle detection and labeling using hough transformation
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")
        # loop over the (x, y) coordinates and radius of the circles
        for (x, y, r) in circles:
            pollen_class.append(classify_pollen(claheNorm, x, y, r, classThreshold))
            if pollen_class[-1]:
                cv2.circle(display, (x, y), r, (255, 255, 0), 2)
                cv2.rectangle(display, (x - 2, y - 2), (x + 2, y + 2), (150, 128, 255), -1)
            else:
                cv2.circle(display, (x, y), r, (0, 255, 0), 2)
                cv2.rectangle(display, (x - 2, y - 2), (x + 2, y + 2), (0, 128, 255), -1)
            pollen_count.append(r)
            x_count.append(x)
            y_count.append(y)
        # show the output image
        cv2.imwrite(outputImgName, display)

    # returns all the necessary values to display
    # NOTE: still missing pixel-to-micrometer, largest dark, largest light
    return ["pix2mm", pollen_class.count(0), pollen_class.count(1), "dark", "light"]

    # display the count of pollen
    # print(len(pollen_count))
    # Total number of radius
    # print(pollen_count)
    # X co-ordinate of circle
    # print(x_count)
    # Y co-ordinate of circle
    # print(y_count)

    # image write statements:
    # uncomment if you want to see step-by-step process
    cv2.imwrite('claheNorm.png', claheNorm)
    cv2.imwrite('edge.png', edge)
    cv2.imwrite("closing.png", closing)
    cv2.imwrite("dilation.png", dilation)
    cv2.imwrite("th4.png", th4)


mainImg = "practice_image_3.jpg"
outputImgName = "main_output.png"

# params to be modified to detect pollen
classThreshold = 70
cannyEdgeLow = 100
cannyEdgeHigh = 230
houghParam2 = 33  # controls tuning of circle detection

minDist = 70    # min distance between circles
minRad = 10     # min radius of circles
maxRad = 60     # max radius of circles

count_pollen(mainImg, outputImgName, cannyEdgeLow, cannyEdgeHigh, houghParam2, minDist, minRad, maxRad, classThreshold)
