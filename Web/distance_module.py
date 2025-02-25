import cv2
import datetime
import time
import os
from camera_module import camera
from firebase_module import save_to_firebase

car_cascade = cv2.CascadeClassifier(r"D:\Project\Distance_Camera\Web\model\haarcascade_car.xml")
# Tạo thư mục lưu ảnh nếu chưa có
image_directory = 'D:/Project/GiamSatKhoangCach_IOT/Upload/Image'
if not os.path.exists(image_directory):
    os.makedirs(image_directory)
# Các thông số tính khoảng cách
focal_length = 1000  
real_width_of_car = 1.8  
distance_threshold = 30  

def detect_cars(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cars = car_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

    min_distance = float('inf')
    closest_car = None

    for (x, y, w, h) in cars:
        distance = (real_width_of_car * focal_length) / w
        if distance < min_distance:
            min_distance = distance
            closest_car = (x, y, w, h)

    return closest_car, min_distance

def save_image():
    frame = camera.get_frame()
    if frame is not None:
        filename = f"image_{int(time.time())}.jpg"
        image_path = os.path.join(image_directory, filename)
        cv2.imwrite(image_path, frame)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_to_firebase(timestamp, image_path)
        return image_path
    return None
