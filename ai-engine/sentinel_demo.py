from ultralytics import YOLO

# 1. Load your best model
# (Make sure this path points to your actual best.pt file)
model = YOLO('/Users/ryankukreti/Library/CloudStorage/OneDrive-ShriVileParleKelavaniMandal/SEM VI/Projects/Sentinal Cloud/runs/detect/sentinel_final_v3/weights/best.pt')

print("🚀 Starting Sentinel Live Feed...")
print("   Press 'q' in the video window to quit.")

# 2. Run the Live Tracker
results = model.track(
    source='/Users/ryankukreti/Library/CloudStorage/OneDrive-ShriVileParleKelavaniMandal/SEM VI/Projects/Sentinal Cloud/test_set/archive/Police Cars Fire Trucks And Ambulances Responding Compilation Part 12.mp4', 
    
    # --- TWEAKS ---
    conf=0.7,        # Only show confident detections (60%+)
    iou=0.5,         # Aggressively merge overlapping boxes
    persist=True,    # TRACKING: Remembers "Ambulance #1" between frames
    tracker="bytetrack.yaml", # The algorithm that handles occlusion
    
    # --- LIVE DISPLAY ---
    show=True,       # Opens a window on your screen
    device='mps'     # Mac GPU acceleration
)