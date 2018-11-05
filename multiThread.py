#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

def extractFrames(fileName, outputBuffer, buffLock, buffFillSem, buffEmptSem, compLock):
    vidcap = cv2.VideoCapture(fileName)
    success,image = vidcap.read()
    count = 0
    print("Reading frame {} {} ".format(count, success))
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame 
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        # take out an empty
        buffEmptSem.acquire()
        # lock the buffer to avoid any issues
        buffLock.acquire()
        outputBuffer.put(jpgAsText)

        # unlock the buffer
        buffLock.release()

        # Add a fill entry
        buffFillSem.release()
        
        success,image = vidcap.read()
        print('Reading frame {} {}'.format(count, success))
        count += 1

    print("Frame extraction complete")
    compLock.release()

    
def convertToGrayscale(inputBuffer, outputBuffer):
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

def displayFrames(inputBuffer, buffLock, buffFillSem, buffEmptSem, compLock):
    count = 0
    complete = False

    complete = compLock.acquire(blocking=False)
    #for frameAsText in iter(inputBuffer.get, None): #inputBuffer:
    while not complete:
        # reduce fill count by one
        buffFillSem.acquire()

        # lock the buffer
        buffLock.acquire()

        # get data from buffer
        frameAsText = inputBuffer.get()

        # unlock the buffer
        buffLock.release()

        # increase the empty count by one
        buffEmptSem.release()
        
        # decode the frame 
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)
        
        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

        print("Displaying frame {}".format(count))        

        # display the image
        cv2.imshow("Video", img)
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

        complete = compLock.acquire(blocking=False)
    
    cv2.destroyAllWindows()

# filename of clip to load
filename = 'clip2.mp4'

# create a shared buffer for load -> display
buffer = []

# create a load buffer lock
buffLock = threading.Lock()

# create a load buffer semaphore
buffFillSem = threading.Semaphore(0)
buffEmptSem = threading.Semaphore(10)

# create a lock to determine when complete
compLock = threading.Lock()
compLock.acquire()

# shared queue  
extractionQueue = queue.Queue()

# extract the frames
extractionThread = threading.Thread(target=extractFrames, args=(filename,extractionQueue, buffLock, buffFillSem, buffEmptSem, compLock))

#extractFrames(filename, extractionQueue)

# display the frames
#displayFrames(extractionQueue)

displayThread = threading.Thread(target=displayFrames, args=(extractionQueue, buffLock, buffFillSem, buffEmptSem, compLock))

print("Starting threads")
extractionThread.start()
displayThread.start()


