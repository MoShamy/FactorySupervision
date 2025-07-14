from ultralytics import YOLO
import os

# === CONFIGURATION ===
yaml_path = 'dataset/data.yaml'               # Path to your dataset YAML
video_dir = 'testVid/'               # Folder with input test videos
output_dir = 'fine_tuned_output_videos/'            # Output folder for annotated videos
pretrained_model = 'yolov8m.pt'          # Model variant: yolov8n/s/m/l/x.pt
epochs = 5                              # Training epochs


# === TRAINING ===
print(" Starting YOLOv8 training...")
model = YOLO(pretrained_model)
model.train(data=yaml_path, epochs=epochs)
print(" Training complete.\n")

# === LOAD BEST MODEL ===
trained_model = YOLO('runs/detect/train2/weights/best.pt')

# === PREP OUTPUT FOLDER ===
os.makedirs(output_dir, exist_ok=True)

# === TEST ON VIDEOS ===
print("🎬 Running inference on test videos...\n")
for file in video_dir:
    if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
        video_path = os.path.join(video_dir, file)
        name_prefix = os.path.splitext(file)[0]

        print(f"🔍 Processing: {file}")
        trained_model.predict(
            source=video_path,
            save=True,
            save_txt=False,
            save_conf=True,
            project=output_dir,
            name=f"annotated_{name_prefix}"
        )

print("\n✅ All videos processed. Check the 'output_videos' folder.")
