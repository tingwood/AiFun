from picamera import PiCamera, Color
from time import sleep

camera=PiCamera()

#camera.rotatio=180

#Default is the monitor's resolution
#still image(max 2592*1944), video (max 1920*1080)
#min resolution 64*64
#camera.resolution=(2592,1944)

#when set max resolution, framerate should be 15
#camera.framerate = 15
#camera.brightness=70
#camera.contrast=20

#valid size are 6-160, default 32
camera.annotate_text_size=30
#camera.annotate_background=Color('black')
camera.annotate_text='annotation'

#alter the transparency(0) nontrans(255)
#camera.start_preview(alpha=255)
camera.start_preview()

# camera.IMAGE-EFFECTS
camera.image_effect='gpen'
# camera.AWB_MODES
camera.awb_mode='auto'
# camera.EXPOSURE_MODES
camera.exposure_mode='auto'

#sleep for at least 2 seconds, sensor auto set its light levels
sleep(5)

#camera.capture('./image.jpg')
#camera.capture('./image%s.jpg' % i)

#camera.start_recording('./video.h264')
#sleep(10)
#camera.stop_recording()

camera.stop_preview()




