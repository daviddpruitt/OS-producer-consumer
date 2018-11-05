#!/usr/bin/env python3

import cv2

count = 0
success = True

inFileName = "frame{:04d}.jpg".format(count)
inputImage = cv2.imread(inFileName, cv2.IMREAD_GRAYSCALE)

while inputImage is not None:
    print("Converting frame {}".format(count))

    outFileName = "frame{:04d}.png".format(count)
    cv2.imwrite(outFileName, inputImage)

    count += 1
    inFileName = "frame{:04d}.jpg".format(count)
    inputImage = cv2.imread(inFileName, cv2.IMREAD_GRAYSCALE)

    
    
