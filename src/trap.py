import cv2
import datetime
import time

class Trap:
    last_frame = None
    timedelta = datetime.timedelta(seconds=1)
    contour_size_coeff = 0.001
    running = False

    def __init__(self, camera, dir_path):
        self.camera = camera
        self.dir_path = dir_path
        self.last_photo_time = datetime.datetime.now()

    def run(self, interval=0.1):
        self.running = True
        while self.running:
            start = datetime.datetime.now()
            self.loop_step()
            end = datetime.datetime.now()
            delay = interval - (end - start).total_seconds()
            
            if delay>0:
                time.sleep(interval)

    def loop_step(self):
        img = self.camera.get_preview_img()

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21,21), 0)

        if self.last_frame is None:
            self.last_frame = gray
            return

        diff_frame = cv2.absdiff(self.last_frame, gray)
        thresh = cv2.threshold(diff_frame, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours,_ = cv2.findContours(thresh.copy(),
            cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion = False
        self.last_frame = gray

        for c in contours:
            if cv2.contourArea(c) > self.contour_size_coeff * img.size:
                motion = True

        if motion and datetime.datetime.now() - self.last_photo_time > self.timedelta:
            print('motion detected')
            self.last_photo_time = datetime.datetime.now()
            self.camera.save_photo(self.dir_path)

    def close(self):
        self.camera.close()

