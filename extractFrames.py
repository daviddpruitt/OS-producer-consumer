#!/usr/bin/env python3

import cv2
vidcap = cv2.VideoCapture('clip2.mp4')
success,image = vidcap.read()
count = 0
print("Reading frame {} {} ".format(count, success))
while success:
  cv2.imwrite("frame{:04d}.jpg".format(count), image)   
  success,image = vidcap.read()
  print('Reading frame {} {}'.format(count, success))
  count += 1
