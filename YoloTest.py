from ultralytics import YOLO
from pathlib import Path

model = YOLO("yolov8m.pt")  # or "yolov8n.pt" for faster
results = []

testFolder = Path("TestImg")
for img in testFolder.iterdir():
    results.append(model(img))

for i, result in enumerate(results):
    save_path = f"Results/result_{i+1}.jpg"
    result[0].save(save_path)
    print(f"Result {i+1} saved to {save_path}")