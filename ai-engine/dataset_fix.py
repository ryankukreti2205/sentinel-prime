import os
import shutil
import glob
import yaml
from tqdm import tqdm

# ==========================================
# ⚙️ CONFIGURATION (CHECK THESE PATHS!)
# ==========================================

CCTV_RAW_DIR ='/Users/ryankukreti/Documents/dataset-2/cctv'
DASHCAM_RAW_DIR = '/Users/ryankukreti/Documents/dataset-2/dashcam'
FINAL_OUTPUT_DIR = "/Users/ryankukreti/Documents/Sentinal_Final_Dataset"

# ==========================================
# 🧠 THE LOGIC
# ==========================================

def setup_directories():
    if os.path.exists(FINAL_OUTPUT_DIR):
        print("♻️  Removing old output folder...")
        shutil.rmtree(FINAL_OUTPUT_DIR)
    
    for split in ['train', 'val']:
        os.makedirs(os.path.join(FINAL_OUTPUT_DIR, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(FINAL_OUTPUT_DIR, split, 'labels'), exist_ok=True)
    print("✅ Clean folder structure created.")

def process_dataset(source_dir, source_type):
    print(f"\n🚀 Processing {source_type} from: {source_dir}")
    
    processed_count = 0
    
    # We check train, valid, val, test
    for split in ['train', 'valid', 'val', 'test']:
        # Map to final destination (Test goes to Train for more data)
        dest_split = 'val' if split in ['valid', 'val'] else 'train'
        
        lbl_source = os.path.join(source_dir, split, 'labels')
        
        if not os.path.exists(lbl_source): continue
        
        files = glob.glob(os.path.join(lbl_source, "*.txt"))
        print(f"   ↳ Scanning {split} ({len(files)} files)...")
        
        for lbl_file in tqdm(files):
            try:
                with open(lbl_file, 'r') as f:
                    lines = f.readlines()
            except: continue
            
            new_lines = []
            has_data = False
            
            for line in lines:
                parts = line.strip().split()
                if not parts: continue
                
                try:
                    cls_id = int(float(parts[0]))
                except ValueError: continue 

                keep_line = False
                
                # --- CCTV LOGIC (SCORCHED EARTH) ---
                if source_type == "CCTV":
                    # Keep EVERYTHING, force to 0
                    keep_line = True
                    
                # --- DASHCAM LOGIC (SMART FILTER) ---
                elif source_type == "DASHCAM":
                    # 1. If it's the expected Roboflow ID (4 or 5) -> KEEP
                    if cls_id in [4, 5]:
                        keep_line = True
                    # 2. FAILSAFE: If it's ALREADY 0 (Roboflow re-mapped it) -> KEEP
                    elif cls_id == 0:
                        keep_line = True
                    # 3. Garbage (1, 2, 3, 6, 15, etc) -> IGNORE
                
                if keep_line:
                    parts[0] = '0' # Force to Class 0
                    new_lines.append(" ".join(parts) + "\n")
                    has_data = True
            
            # --- SAVE FILE ---
            if has_data:
                # 1. Unique Filename
                prefix = "cctv_" if source_type == "CCTV" else "dash_"
                new_name = prefix + os.path.basename(lbl_file)
                dest_lbl_path = os.path.join(FINAL_OUTPUT_DIR, dest_split, 'labels', new_name)
                
                # 2. Write Label
                with open(dest_lbl_path, 'w') as f:
                    f.writelines(new_lines)
                
                # 3. Find & Copy Image
                image_found = False
                orig_base = os.path.splitext(lbl_file)[0]
                # Look in parallel 'images' folder
                expected_img_dir = os.path.dirname(lbl_file).replace('labels', 'images')
                base_filename = os.path.basename(orig_base)
                
                for ext in ['.jpg', '.jpeg', '.png', '.bmp']:
                    img_path = os.path.join(expected_img_dir, base_filename + ext)
                    if os.path.exists(img_path):
                        dest_img_path = os.path.join(FINAL_OUTPUT_DIR, dest_split, 'images', prefix + base_filename + ext)
                        shutil.copy2(img_path, dest_img_path)
                        image_found = True
                        break
                
                if image_found:
                    processed_count += 1
                else:
                    # If image missing, delete the label we just wrote
                    os.remove(dest_lbl_path)

    print(f"   ✅ Saved {processed_count} pairs for {source_type}.")

def create_yaml():
    yaml_content = {
        'path': os.path.abspath(FINAL_OUTPUT_DIR),
        'train': 'train/images',
        'val': 'val/images',
        'nc': 1,
        'names': ['Emergency_Vehicle']
    }
    with open(os.path.join(FINAL_OUTPUT_DIR, 'data.yaml'), 'w') as f:
        yaml.dump(yaml_content, f, sort_keys=False)

if __name__ == "__main__":
    setup_directories()
    
    # 1. PROCESS CCTV (Scorched Earth)
    process_dataset(CCTV_RAW_DIR, "CCTV") 
    
    # 2. PROCESS DASHCAM (Smart Filter)
    process_dataset(DASHCAM_RAW_DIR, "DASHCAM") 
    
    create_yaml()
    print(f"\n🎉 DONE! Final Dataset is ready at: {FINAL_OUTPUT_DIR}")