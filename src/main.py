import os
import pathlib
from trap import Trap
from camera import WebCam, PTPCam


def main():
    #cam = WebCam()
    cam = PTPCam()
    cam.setup()

    dir = pathlib.Path(__file__).resolve().parents[1]
    dir = os.path.join(dir, 'img')

    trap = Trap(cam, dir)

    print("starting loop")
    try:
        trap.run()
    except KeyboardInterrupt:
        pass

    trap.close()
    print("loop closed")


if __name__ == "__main__":
   main()
