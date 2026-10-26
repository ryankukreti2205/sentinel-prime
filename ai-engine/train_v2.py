from ultralytics import YOLO

# --- CONFIG ---
# 1. START FRESH (Don't load old weights, we want a clean brain)
model = YOLO('yolov8s.pt') 

print("🚀 Starting Sentinel Ultimate Training...")
print("   Dataset: Sentinal_Final_Dataset (Merged CCTV + Dashcam)")

# 2. TRAIN
model.train(
    # POINT TO THE NEW DATASET WE JUST BUILT:
    data='/Users/ryankukreti/Documents/Sentinal_Final_Dataset/data.yaml',
    
    epochs=50,           # Increased slightly for the larger dataset
    imgsz=640,
    batch=16,
    lr0=0.01,
    device='mps',        # Mac GPU acceleration
    
    # --- HYPERPARAMETERS ---
    scale=0.8,           # Handle zoom/close-ups
    mosaic=1.0,          # Force it to learn context
    degrees=10.0,        # Handle tilted cameras
    fliplr=0.5,          # Flip left/right
    
    name='sentinel_final_v3'
)