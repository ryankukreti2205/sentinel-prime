from ultralytics import YOLO

# 1. Point to the 'last.pt' file in your latest run folder
# CHECK YOUR FOLDER: It might be 'sentinel_victory_run' or just 'train' depending on what you named it.
model = YOLO('/Users/ryankukreti/Library/CloudStorage/OneDrive-ShriVileParleKelavaniMandal/SEM VI/Projects/Sentinal Cloud/runs/detect/sentinel_final_v3/weights/last.pt')

# 2. Resume
model.train(resume=True)