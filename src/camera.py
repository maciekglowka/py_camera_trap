from abc import ABC, abstractmethod
import cv2
import datetime
import gphoto2 as gp
import io
import numpy as np
import os

class BaseCamera(ABC):
    device = None

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def get_preview_img(self):
        return None

    @abstractmethod
    def save_photo(self, dir_path):
        pass

    @abstractmethod
    def close(self):
        pass


class WebCam(BaseCamera):
    def setup(self):
        self.device = cv2.VideoCapture(0)

    def get_preview_img(self):
        ret_val, img = self.device.read()
        return img

    def save_photo(self, dir_path):
        img = self.get_preview_img()
        path = os.path.join(dir_path, 
            f'webcam_{datetime.datetime.now()}.jpg')
        cv2.imwrite(path, img)
        print(f'photo saved at {path}')

    def close(self):
        pass

class PTPCam(BaseCamera):
    def setup(self):
        self.device = gp.Camera()
        self.device.init()

    def get_preview_img(self):
        camera_file = gp.check_result(gp.gp_camera_capture_preview(self.device))
        file_data = gp.check_result(gp.gp_file_get_data_and_size(camera_file))
        img_stream = io.BytesIO(file_data)

        img = cv2.imdecode(np.frombuffer(img_stream.read(), np.uint8), 1)
        return img

    def close(self):
        self.device.exit()

    def save_photo(self, dir_path):
        #set taret to internal ram
        config = self.device.get_config()
        target_config = config.get_child_by_name('capturetarget')
        old_target = target_config.get_value()
        target_config.set_value('Internal RAM')
        self.device.set_config(config)

        #capture photo
        camera_file_path = self.device.capture(gp.GP_CAPTURE_IMAGE)  

        #get photo to local folder
        target_path = os.path.join(dir_path, camera_file_path.name)
        camera_file = self.device.file_get(
            camera_file_path.folder, camera_file_path.name, gp.GP_FILE_TYPE_NORMAL)
        camera_file.save(target_path)

        #remove photo from camera storage
        self.device.file_delete(camera_file_path.folder, camera_file_path.name)
        
        #reset configuration
        target_config.set_value(old_target)
        self.device.set_config(config)
        
