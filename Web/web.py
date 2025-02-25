import time
import datetime
import cv2
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, Response
import os

app = Flask(__name__)

cred = credentials.Certificate(
    r"D:\Project\GiamSatKhoangCach_IOT\Firebase\giamsatkhoangcachiot-firebase-adminsdk-e6yo6-e7c20c31c6.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://giamsatkhoangcachiot-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Khởi tạo Realtime Database
database = db.reference()

# URL của DroidCam
droidcam_url = "http://192.168.1.3:4747/video"
camera = cv2.VideoCapture(droidcam_url)
if not camera.isOpened():
    print("Không thể kết nối với DroidCam!")
    exit()

# Đảm bảo thư mục lưu ảnh tồn tại
image_directory = 'D:/Project/GiamSatKhoangCach_IOT/Upload/Image'
if not os.path.exists(image_directory):
    os.makedirs(image_directory)

# Thay đổi đường dẫn của Haar Cascade
car_cascade = cv2.CascadeClassifier(r"D:\Project\Distance_Camera\Web\model\haarcascade_car.xml")

# Thông số camera
focal_length = 1000  # Tiêu cự của camera (đơn vị pixel)
real_width_of_car = 1.8  # Chiều rộng thực tế của xe (m)
distance_threshold = 30  # Ngưỡng khoảng cách cảnh báo (m)

@app.route('/')
def home():
    return render_template('index.html')

def generate_video():
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cars = car_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        min_distance = float('inf')
        closest_car = None

        for (x, y, w, h) in cars:
            distance = (real_width_of_car * focal_length) / w
            if distance < min_distance:
                min_distance = distance
                closest_car = (x, y, w, h)

        if closest_car is not None:
            x, y, w, h = closest_car
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"Distance: {min_distance:.2f} m", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            if min_distance < distance_threshold:
                cv2.putText(frame, "Warning: Too Close!", (x, y - 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            # In khoảng cách ra terminal
            print(f"Closest car distance: {min_distance:.2f} m")

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_time', methods=['POST'])
def save_time():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ret, frame = camera.read()
    if ret:
        filename = f"image_{int(time.time())}.jpg"
        image_path = os.path.join(image_directory, filename)
        cv2.imwrite(image_path, frame)
        data = {
            'timestamp': current_time,
            'image_path': image_path
        }
        database.child('GiamSatKhoangCach').push(data)
        return f'Time and image saved successfully! Image Path: {image_path}'
    return 'Failed to capture image.'

@app.route('/history')
def history():
    # Lấy dữ liệu từ Firebase
    history_data = database.child('GiamSatKhoangCach').get()
    
    saved_data = []
    if history_data:  # Kiểm tra nếu có dữ liệu
        # Truy cập trực tiếp vào dictionary và lấy dữ liệu
        for record_key, record_value in history_data.items():  # Duyệt qua các mục trong dictionary
            saved_data.append(record_value)  # Lấy giá trị của mỗi mục
    
    return render_template('history.html', saved_data=saved_data)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
