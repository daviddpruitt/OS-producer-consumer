#!/usr/bin/env python3

import os
from PIL import Image

count = 0
success = True

inFileName = "frame{:04d}.jpg".format(count)
success = os.path.isfile(inFileName)

print("Reading file {} {}".format(count, success))
while success:
    jpgImg = Image.open(inFileName)

    outFileName = "frame{:04d}.bmp".format(count)
    jpgImg.save(outFileName)

    count += 1
    inFileName = "frame{:04d}.jpg".format(count)
    success = os.path.isfile(inFileName)
    print("Reading file {} {}".format(count, success))
    
    
    
