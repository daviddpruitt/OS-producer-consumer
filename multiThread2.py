#!/usr/bin/env python3

import threading
import cv2
import numpy as np
import base64
import queue

class SharedBuffer:
    buffLock     = None
    buffFillSem  = None
    buffEmptySem = None
    buffQueue    = None
    numItems     = 0
    
    def __init__(self, initialCapacity=10):
        """ Initializes a shared queue with a default initial capacity of 10 """
        # create a load buffer lock
        self.buffLock = threading.Lock()

        # create a load buffer semaphore
        self.buffFillSem = threading.Semaphore(0)
        self.buffEmptSem = threading.Semaphore(initialCapacity)

        # shared queue  
        self.buffQueue = queue.Queue()

    def addItem(self, item):
        """ 
        Add an item to the queue if the queue is
        full then this call will block until the 
        item can be added
        """

        # take out an empty
        self.buffEmptSem.acquire()

        # lock the buffer to avoid multiple concurrent accesses
        self.buffLock.acquire()
        
        self.buffQueue.put(item)
        self.numItems += 1
        
        # unlock the buffer
        self.buffLock.release()

        # Add a fill entry
        self.buffFillSem.release()
        
    def getItem(self):
        """
        Remove and return the oldest item from the queue
        If the queue is empty the call will block
        until an item is added
        """

        # reduce fill count by one
        self.buffFillSem.acquire()

        # lock the buffer to avoid multple concurrent accesses
        self.buffLock.acquire()

        # get data from buffer
        retItem = self.buffQueue.get()
        self.numItems -= 1

        # unlock the buffer
        self.buffLock.release()

        # increase the empty count by one
        self.buffEmptSem.release()

        return retItem

    def isEmpty(self):
        """
        Returns whether or no the queue is empty
        """
        return self.numItems == 0

def extractFrames(fileName, outputQueue, compLock):
    vidcap = cv2.VideoCapture(fileName)
    success,image = vidcap.read()
    count = 0
    print("Extracting frame {}".format(count))
    while success:
        # get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)

        #encode the frame 
        jpgAsText = base64.b64encode(jpgImage)

        # add the frame to the buffer
        outputQueue.addItem(jpgAsText)
        
        success,image = vidcap.read()
        print('Extracting frame {}'.format(count))
        count += 1

    compLock.release()
    print("Frame extraction complete release")


    
def convertToGrayscale(inputQueue, outputQueue, inputLock, outputLock):
    count = 0
    complete = False

    complete = inputLock.acquire(blocking=False) and inputQueue.isEmpty()
    while not complete:
        # get the next frame
        frameAsText = inputQueue.getItem()
        
        # decode the frame 
        jpgRawImage = base64.b64decode(frameAsText)

        # convert the raw frame to a numpy array
        jpgImage = np.asarray(bytearray(jpgRawImage), dtype=np.uint8)

        # get a jpg encoded frame
        img = cv2.imdecode( jpgImage ,cv2.IMREAD_UNCHANGED)

        print("Converting frame {}".format(count))

        grayScaleImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # get a jpg encoded frame
        success, jpgGrayScaleImage = cv2.imencode('.jpg', grayScaleImg)

        #encode the frame 
        jpgGrayScaleAsText = base64.b64encode(jpgGrayScaleImage)

        # add the frame to the buffer
        outputQueue.addItem(jpgGrayScaleAsText)

        # if the queue is empty check to see
        # if the producer process is complete
        # these checks need to be done seperately
        # because checking the lock will take out a
        # lock and will subsequently fail
        if inputQueue.isEmpty():
            if inputLock.acquire(blocking=False):
                complete = True

        
        count += 1
    print("From conversion complete")
    outputLock.release()

def displayFrames(inputQueue, compLock):
    count = 0
    complete = False

    complete = compLock.acquire(blocking=False) and inputQueue.isEmpty()
    #for frameAsText in iter(inputBuffer.get, None): #inputBuffer:
    while not complete:
        # get the next frame
        frameAsText = inputQueue.getItem()
        
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

        # if the queue is empty check to see
        # if the producer process is complete
        # these checks need to be done seperately
        # because checking the lock will take out a
        # lock and will subsequently fail
        if inputQueue.isEmpty():
            if compLock.acquire(blocking=False):
                complete = True

    cv2.destroyAllWindows()
    print("Done displaying frames")

# filename of clip to load
filename = 'clip2.mp4'

# create a shared buffer for load -> display
buffer = []

# create a lock to determine when complete
compExtractLock = threading.Lock()
compExtractLock.acquire()

# create a lock to determine when complete
compConvLock = threading.Lock()
compConvLock.acquire()

# shared queue for extracting frames
extractionQueue = SharedBuffer(10)

# shared queue for grayscaling frames
conversionQueue = SharedBuffer(10)

# extract the frames
extractionThread = threading.Thread(target=extractFrames, args=(filename,extractionQueue, compExtractLock))

# convert frames to grayscale
conversionThread = threading.Thread(target=convertToGrayscale, args=(extractionQueue, conversionQueue, compExtractLock, compConvLock))

# display the frames
displayThread = threading.Thread(target=displayFrames, args=(conversionQueue, compConvLock))

print("Starting threads")
extractionThread.start()
displayThread.start()
conversionThread.start()

