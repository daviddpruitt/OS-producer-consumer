#!/usr/bin/env python3

import cv2

count = 0
frameFileName = "frame{:04d}.png".format(count)
img = cv2.imread(frameFileName)

while img is not None:
    print("Displaying frame {}".format(count))
    cv2.imshow("Video", img)
    if cv2.waitKey(42) and 0xFF == ord("q"):
        break

    count += 1
    frameFileName = "frame{:04d}.png".format(count)
    img = cv2.imread(frameFileName)
    
cv2.destroyAllWindows()
