# import cv2
# import math
# import time
# import threading
# import numpy as np
# import mediapipe as mp
# import urllib.request

# from flask import Flask, Response, jsonify, send_from_directory
# from flask_cors import CORS

# # ─────────────────────────────────────────────────────────────
# # Flask Setup
# # ─────────────────────────────────────────────────────────────
# app = Flask(__name__, template_folder='.')
# CORS(app)

# # ─────────────────────────────────────────────────────────────
# # MediaPipe Setup (FAST MODE)
# # ─────────────────────────────────────────────────────────────
# mp_pose = mp.solutions.pose
# mp_drawing = mp.solutions.drawing_utils

# pose_video = mp_pose.Pose(
#     static_image_mode=False,
#     model_complexity=0,          # Faster than 1
#     min_detection_confidence=0.5,
#     min_tracking_confidence=0.5
# )

# # ─────────────────────────────────────────────────────────────
# # Shared Data
# # ─────────────────────────────────────────────────────────────
# latest_data = {
#     "pose": "Unknown Pose",
#     "confidence": 0,
#     "angles": {
#         "le": 0, "re": 0,
#         "ls": 0, "rs": 0,
#         "lk": 0, "rk": 0
#     },
#     "fps": 0,
#     "source": "None"
# }

# latest_frame_jpg = None
# camera_running = False

# data_lock = threading.Lock()
# frame_lock = threading.Lock()

# # ─────────────────────────────────────────────────────────────
# # ESP32 CONFIG
# # ─────────────────────────────────────────────────────────────
# ESP32_IP = "http://10.96.178.102"
# ESP32_URL = f"{ESP32_IP}/capture"   # Snapshot mode

# # ─────────────────────────────────────────────────────────────
# # Utility Functions
# # ─────────────────────────────────────────────────────────────
# def calculateAngle(p1, p2, p3):
#     x1, y1, _ = p1
#     x2, y2, _ = p2
#     x3, y3, _ = p3

#     angle = math.degrees(
#         math.atan2(y3 - y2, x3 - x2) -
#         math.atan2(y1 - y2, x1 - x2)
#     )

#     if angle < 0:
#         angle += 360

#     return angle


# def detectPose(image):
#     imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
#     results = pose_video.process(imageRGB)

#     output = image.copy()
#     h, w, _ = image.shape
#     landmarks = []

#     if results.pose_landmarks:
#         mp_drawing.draw_landmarks(
#             output,
#             results.pose_landmarks,
#             mp_pose.POSE_CONNECTIONS
#         )

#         for lm in results.pose_landmarks.landmark:
#             landmarks.append((
#                 int(lm.x * w),
#                 int(lm.y * h),
#                 lm.z * w
#             ))

#     return output, landmarks


# def classifyPose(landmarks):
#     if not landmarks or len(landmarks) < 33:
#         return "Unknown Pose", 0, {}

#     try:
#         PL = mp_pose.PoseLandmark

#         le = calculateAngle(
#             landmarks[PL.LEFT_SHOULDER.value],
#             landmarks[PL.LEFT_ELBOW.value],
#             landmarks[PL.LEFT_WRIST.value]
#         )

#         re = calculateAngle(
#             landmarks[PL.RIGHT_SHOULDER.value],
#             landmarks[PL.RIGHT_ELBOW.value],
#             landmarks[PL.RIGHT_WRIST.value]
#         )

#         ls = calculateAngle(
#             landmarks[PL.LEFT_ELBOW.value],
#             landmarks[PL.LEFT_SHOULDER.value],
#             landmarks[PL.LEFT_HIP.value]
#         )

#         rs = calculateAngle(
#             landmarks[PL.RIGHT_HIP.value],
#             landmarks[PL.RIGHT_SHOULDER.value],
#             landmarks[PL.RIGHT_ELBOW.value]
#         )

#         lk = calculateAngle(
#             landmarks[PL.LEFT_HIP.value],
#             landmarks[PL.LEFT_KNEE.value],
#             landmarks[PL.LEFT_ANKLE.value]
#         )

#         rk = calculateAngle(
#             landmarks[PL.RIGHT_HIP.value],
#             landmarks[PL.RIGHT_KNEE.value],
#             landmarks[PL.RIGHT_ANKLE.value]
#         )

#         angles = {
#             "le": round(le),
#             "re": round(re),
#             "ls": round(ls),
#             "rs": round(rs),
#             "lk": round(lk),
#             "rk": round(rk)
#         }

#         label = "Unknown Pose"
#         confidence = 10

#         # T Pose
#         if le > 160 and re > 160 and 75 < ls < 110 and 75 < rs < 110:
#             if lk > 160 and rk > 160:
#                 label = "T Pose"
#                 confidence = 98

#         # Warrior II
#         elif (
#             le > 160 and re > 160 and
#             70 < ls < 115 and
#             70 < rs < 115
#         ):
#             if (
#                 (lk > 160 and 95 < rk < 135) or
#                 (rk > 160 and 95 < lk < 135)
#             ):
#                 label = "Warrior II Pose"
#                 confidence = 96

#         # Tree Pose
#         elif (lk > 160 and 25 < rk < 50) or (rk > 160 and 25 < lk < 50):
#             label = "Tree Pose"
#             confidence = 92

#         return label, confidence, angles

#     except:
#         return "Unknown Pose", 0, {}


# # ─────────────────────────────────────────────────────────────
# # ESP32 Worker (OPTIMIZED)
# # ─────────────────────────────────────────────────────────────
# def esp32_worker():
#     global latest_frame_jpg

#     print("[INFO] ESP32 worker started")

#     t_prev = time.time()

#     while True:
#         try:
#             img_resp = urllib.request.urlopen(ESP32_URL, timeout=2)
#             img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)

#             frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

#             if frame is None:
#                 continue

#             # SPEED BOOST
#             frame = cv2.resize(frame, (320, 240))

#             output, landmarks = detectPose(frame)
#             label, conf, angles = classifyPose(landmarks)

#             # FPS
#             t_now = time.time()
#             fps = int(1 / max(t_now - t_prev, 0.001))
#             t_prev = t_now

#             # Text
#             color = (0, 255, 0) if label != "Unknown Pose" else (0, 0, 255)

#             cv2.putText(
#                 output,
#                 f"{label} {conf}%",
#                 (10, 30),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.7,
#                 color,
#                 2
#             )

#             cv2.putText(
#                 output,
#                 f"{fps} FPS",
#                 (10, 55),
#                 cv2.FONT_HERSHEY_SIMPLEX,
#                 0.6,
#                 (255, 255, 0),
#                 2
#             )

#             _, buffer = cv2.imencode(
#                 '.jpg',
#                 output,
#                 [cv2.IMWRITE_JPEG_QUALITY, 65]
#             )

#             with frame_lock:
#                 latest_frame_jpg = buffer.tobytes()

#             with data_lock:
#                 latest_data.update({
#                     "pose": label,
#                     "confidence": conf,
#                     "angles": angles,
#                     "fps": fps,
#                     "source": "ESP32-CAM"
#                 })

#         except Exception as e:
#             print("ESP32 Error:", e)
#             time.sleep(1)


# # ─────────────────────────────────────────────────────────────
# # Laptop Webcam
# # ─────────────────────────────────────────────────────────────
# def generate_frames():
#     global camera_running

#     cap = cv2.VideoCapture(0)

#     t_prev = time.time()

#     while camera_running:
#         success, frame = cap.read()

#         if not success:
#             break

#         frame = cv2.flip(frame, 1)
#         frame = cv2.resize(frame, (640, 480))

#         output, landmarks = detectPose(frame)
#         label, conf, angles = classifyPose(landmarks)

#         t_now = time.time()
#         fps = int(1 / max(t_now - t_prev, 0.001))
#         t_prev = t_now

#         cv2.putText(
#             output,
#             f"{label} {conf}%",
#             (10, 30),
#             cv2.FONT_HERSHEY_SIMPLEX,
#             0.7,
#             (0, 255, 0),
#             2
#         )

#         with data_lock:
#             latest_data.update({
#                 "pose": label,
#                 "confidence": conf,
#                 "angles": angles,
#                 "fps": fps,
#                 "source": "Webcam"
#             })

#         _, buffer = cv2.imencode('.jpg', output)

#         yield (
#             b'--frame\r\n'
#             b'Content-Type: image/jpeg\r\n\r\n' +
#             buffer.tobytes() +
#             b'\r\n'
#         )

#     cap.release()


# # ─────────────────────────────────────────────────────────────
# # Routes
# # ─────────────────────────────────────────────────────────────
# @app.route('/')
# def home():
#     return send_from_directory('.', 'index.html')


# @app.route('/video_feed')
# def video_feed():
#     return Response(
#         generate_frames(),
#         mimetype='multipart/x-mixed-replace; boundary=frame'
#     )


# @app.route('/latest_frame')
# def latest_frame():
#     with frame_lock:
#         jpg = latest_frame_jpg

#     if jpg is None:
#         return Response(status=204)

#     return Response(jpg, mimetype='image/jpeg')


# @app.route('/pose_data')
# def pose_data():
#     with data_lock:
#         return jsonify(latest_data)


# @app.route('/start_camera', methods=['POST'])
# def start_camera():
#     global camera_running
#     camera_running = True
#     return jsonify({"status": "started"})


# @app.route('/stop_camera', methods=['POST'])
# def stop_camera():
#     global camera_running
#     camera_running = False
#     return jsonify({"status": "stopped"})


# @app.route('/<path:path>')
# def static_files(path):
#     return send_from_directory('.', path)


# # ─────────────────────────────────────────────────────────────
# # Main
# # ─────────────────────────────────────────────────────────────
# if __name__ == '__main__':
#     threading.Thread(target=esp32_worker, daemon=True).start()

#     app.run(
#         host='0.0.0.0',
#         port=5000,
#         debug=False,
#         threaded=True
#     )


import cv2
import math
import time
import threading
import numpy as np
import mediapipe as mp
import urllib.request

from flask import Flask, Response, jsonify, send_from_directory
from flask_cors import CORS

# ─────────────────────────────────────────────────────────────
# Flask Setup
# ─────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder='.')
CORS(app)

# ─────────────────────────────────────────────────────────────
# MediaPipe Setup
# ─────────────────────────────────────────────────────────────
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

pose_video = mp_pose.Pose(
    static_image_mode=False,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# ─────────────────────────────────────────────────────────────
# Shared Data
# ─────────────────────────────────────────────────────────────
latest_data = {
    "pose": "Unknown Pose",
    "confidence": 0,
    "angles": {"le": 0, "re": 0, "ls": 0, "rs": 0, "lk": 0, "rk": 0},
    "fps": 0,
    "source": "None"
}

latest_frame_jpg = None
camera_running = False

data_lock = threading.Lock()
frame_lock = threading.Lock()

# ─────────────────────────────────────────────────────────────
# ESP32 CONFIG
# ─────────────────────────────────────────────────────────────
ESP32_IP = "http://10.96.178.102"
ESP32_STREAM_URL = f"{ESP32_IP}:81/stream"   # MJPEG stream

# ─────────────────────────────────────────────────────────────
# Utility Functions
# ─────────────────────────────────────────────────────────────
def calculateAngle(p1, p2, p3):
    x1, y1, _ = p1
    x2, y2, _ = p2
    x3, y3, _ = p3
    angle = math.degrees(
        math.atan2(y3 - y2, x3 - x2) -
        math.atan2(y1 - y2, x1 - x2)
    )
    if angle < 0:
        angle += 360
    return angle


def detectPose(image):
    imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose_video.process(imageRGB)
    output = image.copy()
    h, w, _ = image.shape
    landmarks = []
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(output, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        for lm in results.pose_landmarks.landmark:
            landmarks.append((int(lm.x * w), int(lm.y * h), lm.z * w))
    return output, landmarks


def classifyPose(landmarks):
    if not landmarks or len(landmarks) < 33:
        return "Unknown Pose", 0, {}
    try:
        PL = mp_pose.PoseLandmark

        le = calculateAngle(landmarks[PL.LEFT_SHOULDER.value],  landmarks[PL.LEFT_ELBOW.value],   landmarks[PL.LEFT_WRIST.value])
        re = calculateAngle(landmarks[PL.RIGHT_SHOULDER.value], landmarks[PL.RIGHT_ELBOW.value],  landmarks[PL.RIGHT_WRIST.value])
        ls = calculateAngle(landmarks[PL.LEFT_ELBOW.value],     landmarks[PL.LEFT_SHOULDER.value], landmarks[PL.LEFT_HIP.value])
        rs = calculateAngle(landmarks[PL.RIGHT_HIP.value],      landmarks[PL.RIGHT_SHOULDER.value],landmarks[PL.RIGHT_ELBOW.value])
        lk = calculateAngle(landmarks[PL.LEFT_HIP.value],       landmarks[PL.LEFT_KNEE.value],    landmarks[PL.LEFT_ANKLE.value])
        rk = calculateAngle(landmarks[PL.RIGHT_HIP.value],      landmarks[PL.RIGHT_KNEE.value],   landmarks[PL.RIGHT_ANKLE.value])

        angles = {
            "le": round(le), "re": round(re),
            "ls": round(ls), "rs": round(rs),
            "lk": round(lk), "rk": round(rk)
        }

        label = "Unknown Pose"
        confidence = 10

        # T Pose
        if le > 160 and re > 160 and 75 < ls < 110 and 75 < rs < 110:
            if lk > 160 and rk > 160:
                label = "T Pose"
                confidence = 98

        # Warrior II
        elif le > 160 and re > 160 and 70 < ls < 115 and 70 < rs < 115:
            if (lk > 160 and 95 < rk < 135) or (rk > 160 and 95 < lk < 135):
                label = "Warrior II Pose"
                confidence = 96

        # Tree Pose
        elif (lk > 160 and 25 < rk < 50) or (rk > 160 and 25 < lk < 50):
            label = "Tree Pose"
            confidence = 92

        # Mountain Pose
        elif 10 < ls < 60 and 10 < rs < 60 and le > 160 and re > 160 and lk > 160 and rk > 160:
            label = "Mountain Pose"
            confidence = 90

        # Chair Pose
        elif 140 < ls < 180 and 140 < rs < 180 and le > 160 and re > 160 and 80 < lk < 130 and 80 < rk < 130:
            label = "Chair Pose"
            confidence = 93

        # Hand Up Pose
        elif (ls > 140 or ls < 30) and (rs > 140 or rs < 30) and le > 160 and re > 160 and lk > 160 and rk > 160:
            label = "Hand Up Pose"
            confidence = 88

        return label, confidence, angles
    except:
        return "Unknown Pose", 0, {}


# ─────────────────────────────────────────────────────────────
# ESP32 MJPEG Stream Worker  ← THE KEY FIX
#
# cv2.VideoCapture() silently fails on ESP32-CAM MJPEG streams
# because OpenCV's backend can't reliably parse the multipart
# boundary format the ESP32-CAM firmware uses.
#
# Solution: read the raw stream with urllib, manually scan for
# JPEG start (FF D8) and end (FF D9) markers, then decode each
# complete JPEG frame with cv2.imdecode().
# ─────────────────────────────────────────────────────────────
def esp32_worker():
    global latest_frame_jpg

    print("[INFO] ESP32 MJPEG stream worker started")

    JPEG_START = b'\xff\xd8'
    JPEG_END   = b'\xff\xd9'
    CHUNK_SIZE = 4096          # bytes per read
    RECONNECT_DELAY = 2        # seconds between reconnect attempts

    t_prev = time.time()
    buffer = b''

    while True:
        stream = None
        try:
            print(f"[INFO] Connecting to {ESP32_STREAM_URL} ...")
            req = urllib.request.Request(
                ESP32_STREAM_URL,
                headers={"User-Agent": "Mozilla/5.0"}  # some firmware needs this
            )
            stream = urllib.request.urlopen(req, timeout=10)
            print("[INFO] Connected to ESP32 stream")
            buffer = b''

            while True:
                chunk = stream.read(CHUNK_SIZE)
                if not chunk:
                    print("[WARN] Stream ended, reconnecting...")
                    break

                buffer += chunk

                # Extract every complete JPEG in the buffer
                while True:
                    start = buffer.find(JPEG_START)
                    if start == -1:
                        buffer = b''   # no JPEG start found, discard
                        break

                    end = buffer.find(JPEG_END, start + 2)
                    if end == -1:
                        # Incomplete JPEG — keep buffer from start onwards
                        buffer = buffer[start:]
                        break

                    # We have a complete JPEG: [start : end+2]
                    jpg_bytes = buffer[start : end + 2]
                    buffer    = buffer[end + 2:]   # advance past this frame

                    # Decode
                    img_array = np.frombuffer(jpg_bytes, dtype=np.uint8)
                    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                    if frame is None:
                        continue

                    # Resize for speed
                    frame = cv2.resize(frame, (320, 240))

                    output, landmarks = detectPose(frame)
                    label, conf, angles = classifyPose(landmarks)

                    t_now = time.time()
                    fps   = int(1 / max(t_now - t_prev, 0.001))
                    t_prev = t_now

                    color = (0, 255, 0) if label != "Unknown Pose" else (0, 0, 255)
                    cv2.putText(output, f"{label} {conf}%", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                    cv2.putText(output, f"{fps} FPS", (10, 55),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                    _, enc = cv2.imencode('.jpg', output,
                                         [cv2.IMWRITE_JPEG_QUALITY, 70])

                    with frame_lock:
                        latest_frame_jpg = enc.tobytes()

                    with data_lock:
                        latest_data.update({
                            "pose": label,
                            "confidence": conf,
                            "angles": angles,
                            "fps": fps,
                            "source": "ESP32 Stream"
                        })

        except Exception as e:
            print(f"[ERROR] ESP32 stream error: {e}")
        finally:
            if stream:
                try:
                    stream.close()
                except:
                    pass
            print(f"[INFO] Reconnecting in {RECONNECT_DELAY}s...")
            time.sleep(RECONNECT_DELAY)


# ─────────────────────────────────────────────────────────────
# Laptop Webcam
# ─────────────────────────────────────────────────────────────
def generate_frames():
    global camera_running

    cap = cv2.VideoCapture(0)
    t_prev = time.time()

    while camera_running:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (640, 480))

        output, landmarks = detectPose(frame)
        label, conf, angles = classifyPose(landmarks)

        t_now = time.time()
        fps   = int(1 / max(t_now - t_prev, 0.001))
        t_prev = t_now

        cv2.putText(output, f"{label} {conf}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        with data_lock:
            latest_data.update({
                "pose": label,
                "confidence": conf,
                "angles": angles,
                "fps": fps,
                "source": "Webcam"
            })

        _, buffer = cv2.imencode('.jpg', output)
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
               + buffer.tobytes() + b'\r\n')

    cap.release()


# ─────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/latest_frame')
def latest_frame():
    with frame_lock:
        jpg = latest_frame_jpg
    if jpg is None:
        return Response(status=204)
    return Response(jpg, mimetype='image/jpeg')

@app.route('/pose_data')
def pose_data():
    with data_lock:
        return jsonify(latest_data)

@app.route('/start_camera', methods=['POST'])
def start_camera():
    global camera_running
    camera_running = True
    return jsonify({"status": "started"})

@app.route('/stop_camera', methods=['POST'])
def stop_camera():
    global camera_running
    camera_running = False
    return jsonify({"status": "stopped"})

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    threading.Thread(target=esp32_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)