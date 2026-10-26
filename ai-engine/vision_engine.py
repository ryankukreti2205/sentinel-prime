import cv2
from ultralytics import YOLO
import requests # The messenger
import time

# 1. Load the model
custom_model_path = '/Users/ryankukreti/Library/CloudStorage/OneDrive-ShriVileParleKelavaniMandal/SEM VI/Projects/Sentinal Cloud/ai-engine/runs/detect/sentinel_emergency_v1/weights/best.pt'
model = YOLO(custom_model_path)
# 2. Configuration for the Bridge
API_URL = "http://127.0.0.1:5050/api/logs"
last_log_time = 0
LOG_DELAY = 3  # Only log once every 3 seconds to save cloud space

cap = cv2.VideoCapture(0)

print("AI Engine Bridge active... Press 'q' to quit.")

while cap.isOpened():
    success, frame = cap.read()
    if success:
        results = model(frame, verbose=False)
        
        # 3. Logic to send data to Node.js
        current_time = time.time()
        
        # Check if any objects were detected
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get class name (e.g., 'person', 'cell phone')
                cls = int(box.cls[0])
                name = model.names[cls]
                conf = float(box.conf[0])

                # 4. If we haven't logged recently, send to Backend
                if current_time - last_log_time > LOG_DELAY and conf > 0.5:
                    data = {
                        "object": name,
                        "confidence": round(conf, 2)
                    }
                    try:
                        response = requests.post(API_URL, json=data)
                        print(f"📡 Cloud Log: {name} ({data['confidence']}) -> {response.status_code}")
                        last_log_time = current_time
                    except Exception as e:
                        print(f"❌ Connection to Backend failed: {e}")

        annotated_frame = results[0].plot()
        cv2.imshow("SentinelCloud AI Engine", annotated_frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    else:
        break

cap.release()
cv2.destroyAllWindows()