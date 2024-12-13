
import cv2
import pickle
import cvzone
import numpy as np
from flask import Flask, render_template, Response
from flask import Flask, render_template
import sqlite3
from flask import Flask, render_template, jsonify

app = Flask(__name__)

cap = cv2.VideoCapture('carPark.mp4')

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48





import sqlite3
from datetime import datetime

def insert_parking_data(free_spaces):
    conn = sqlite3.connect('parking_details.db')
    cursor = conn.cursor()

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
    INSERT INTO parking_details (timestamp, free_spaces)
    VALUES (?, ?)
    ''', (timestamp, free_spaces))

    conn.commit()
    conn.close()

def checkParkingSpace(img,imgPro):
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 200, 0))

    insert_parking_data(spaceCounter)








def generate_frames():
    while True:
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, img = cap.read()
        if not success:
            break
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                             cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

        checkParkingSpace(img, imgDilate)  

        ret, buffer = cv2.imencode('.jpg', img)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')




def get_parking_data():
    conn = sqlite3.connect('parking_details.db')
    cursor = conn.cursor()

    cursor.execute('''
                   SELECT timestamp, free_spaces FROM parking_details ORDER BY timestamp DESC LIMIT 5
                   ''')
    data = cursor.fetchall()
    
    conn.close()
    return data


@app.route('/')
def index():
    data = get_parking_data()

    print("Data passed to template: ", data)

    return render_template('indexx.html', data=data)

@app.route('/get-parking-data', methods=['GET'])
def get_parking_data_json():
    data = get_parking_data()

    return jsonify(data)

@app.route('/map')
def map_view():
    return render_template('map.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(debug=True)
