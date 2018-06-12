DATE=$(date +"%Y-%m-%d_%H-%M")
#rotate, set automatic whitebalance and exposure, save with date-name.jpg at log folder
sudo raspistill --timeout 1  -rot 270 -n -awb auto --exposure auto -o /home/pi/citisense/logs/$DATE.jpg
sleep 1
sudo sync
sleep 1
#https://www.raspberrypi.org/documentation/raspbian/applications/camera.md
