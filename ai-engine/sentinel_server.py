from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import cv2
import os
import time
import requests
import threading
from ultralytics import YOLO

app = Flask(__name__)
CORS(app)  # Allow React to talk to Python

# --- CONFIGURATION ---
MODEL_PATH = '/Users/ryankukreti/Library/CloudStorage/OneDrive-ShriVileParleKelavaniMandal/SEM VI/Projects/Sentinal Cloud/runs/detect/sentinel_final_v3/weights/best.pt' # CHECK THIS PATH
UPLOAD_FOLDER = 'uploads'
NODE_BACKEND_URL = "http://localhost:5050/api/logs"

# Create uploads folder if not exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Global variables to control the stream
current_video_path = None
model = YOLO(MODEL_PATH)
streaming_active = False

def generate_frames():
    global current_video_path, streaming_active
    
    if not current_video_path:
        return

    cap = cv2.VideoCapture(current_video_path)
    
    # Logic Variables
    consecutive_frames = 0
    alert_sent_flag = False
    persistence_req = 15

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # 1. INFERENCE
        results = model.track(frame, persist=True, conf=0.6, verbose=False, tracker="bytetrack.yaml")
        
        # 2. LOGIC (The same logic we built before)
        ambulance_present = False
        if results[0].boxes.id is not None:
            cls_ids = results[0].boxes.cls.cpu().numpy()
            if 0 in cls_ids:
                ambulance_present = True

        if ambulance_present:
            consecutive_frames += 1
            if consecutive_frames > persistence_req:
                consecutive_frames = persistence_req
                # IOT TRIGGER
                if not alert_sent_flag:
                    threading.Thread(target=send_log_to_node).start()
                    alert_sent_flag = True
        else:
            consecutive_frames = 0
            alert_sent_flag = False

        # 3. DRAW UI ON FRAME
        annotated_frame = results[0].plot()
        
        # Draw the "verification bar" we made earlier
        h, w, _ = annotated_frame.shape
        bar_w = 200
        fill_ratio = consecutive_frames / persistence_req
        fill_width = int(bar_w * fill_ratio)
        color = (0, 255, 0) if fill_ratio >= 1.0 else (0, 255, 255)
        
        cv2.rectangle(annotated_frame, (w-220, 30), (w-20, 45), (50,50,50), -1)
        cv2.rectangle(annotated_frame, (w-220, 30), (w-220+fill_width, 45), color, -1)
        cv2.putText(annotated_frame, "SCANNING" if fill_ratio < 1 else "ALERT SENT", (w-220, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # 4. ENCODE FRAME AS JPEG
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        frame = buffer.tobytes()

        # Yield frame for browser streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

def send_log_to_node():
    """Talks to your Node.js backend"""
    try:
        requests.post(NODE_BACKEND_URL, json={
            "object": "Emergency Vehicle",
            "confidence": 99.9
        })
        print("✅ Alert sent to Node Backend")
    except:
        pass

@app.route('/upload', methods=['POST'])
def upload_video():
    global current_video_path
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    current_video_path = filepath
    
    return jsonify({"message": "File uploaded successfully", "path": filepath}), 200

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    # Running on Port 5001 to avoid conflict with Node (5000)
    print("🚀 Sentinel AI Server running on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)