import cv2
import threading


class VideoStream:
    def __init__(self):
        self.frame = None
        self.frame_lock = threading.Lock()

    def write(self, frame):
        if frame is None:
            print('[VideoStream] No Frame')
            return
        with self.frame_lock:
            self.frame = frame[:]

    def read(self):
        with self.frame_lock:
            if self.frame is None:
                return self.frame
            return self.frame[:]


class VideoWriteStream(VideoStream):
    def __init__(self, filesrc, width, height, fps=20.0):
        super().__init__()
        self.out = cv2.VideoWriter(filesrc, cv2.VideoWriter_fourcc(*'DIVX'), fps, (width, height))

    def write(self, frame):
        if frame is None:
            print('[VideoStream] No Frame')
            return
        self.out.write(frame)
        with self.frame_lock:
            self.frame = frame

    def stop(self):
        self.out.release()


class WebcamVideoStream:
    def __init__(self, src, width, height):
        self.src = src
        self.width = width
        self.height = height
        self.frame_lock = threading.Lock()
        self.stop_fg = False
        self.writing = False

        self.stream = cv2.VideoCapture(self.src)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.thread = threading.Thread(target=self.update)
        self.ret, self.frame = self.stream.read()
        self.out = None

    def start(self):
        self.thread.start()

    def update(self):
        while True:
            ret, frame = self.stream.read()
            if frame is None:
                print('[WebcamVideoStream] No Frame')
                return
            with self.frame_lock:
                self.ret, self.frame = ret, frame
            if self.stop_fg is True:
                return

    def read(self):
        with self.frame_lock:
            if self.frame is None:
                return self.ret, self.frame
            return self.ret, self.frame[:]

    def stop(self):
        self.stop_fg = True
        self.thread.join()
        self.stop_fg = False
        if self.writing is True:
            self.out.release()
            self.writing = False

    def release(self):
        self.stop()

    def updatewrite(self):
        while True:
            ret, frame = self.stream.read()
            if frame is None:
                print('[WebcamVideoStream] No Frame')
                return
            self.out.write(frame)
            with self.frame_lock:
                self.ret, self.frame = ret, frame
            if self.stop_fg is True:
                return

    def writefile(self, filesrc, fps=20.0):
        self.out = cv2.VideoWriter(filesrc, cv2.VideoWriter_fourcc(*'DIVX'), fps, (self.width, self.height))
        self.thread = threading.Thread(target=self.updatewrite)
        self.writing = True
        self.start()


# grame = numpy.zeros((480, 640, 3), dtype=numpy.uint8)
import time
cap = WebcamVideoStream(0, 640, 480)
cap.writefile('1.avi')
fin = VideoWriteStream('2.avi', 640, 480)
t = time.time()
while time.time() - t < 2:
    tv = time.time()
    ret, frame = cap.read()
    final = cv2.flip(frame, 1)
    fin.write(final)
    time.sleep(0.01)
print('OUTOUTOUTOUT')
cap.release()