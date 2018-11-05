# OS-producer-consumer
Example code for a possible producer consumer code
These examples require opencv to run

# Files
## Stand alone examples
* extractFrames.py      - extracts frames from clip.mp4 and saves them to jpg files
* converJpgToBmp.py     - opens frames saved in jpg files and saves them in bmp files
* convertToGrayScale.py - opens frames saved as png files and saves them as grayscal jpg files
* displayFrames.py      - opens frames saved as png files and displays them sequentially at 24 fps

## multithreaded examples
* multithread.py        - a basic multithreaded example that loads frames from a file and displays them
* multithread2.py       - a more advanced example that implements a shared buffer classes implementing producer/consumer to extract frames, 
* convert them to grayscale, and then display them
