import picamera
import time

camera = picamera.PiCamera()
camera.iso=100
camera.rotation = 180
camera.zoom= (0.5,0.5,0.25,0.25)
camera._check_camera_open()
time.sleep(0.5)
camera.preview_fullscreen = True
camera.start_preview()
time.sleep(5)
camera.close()