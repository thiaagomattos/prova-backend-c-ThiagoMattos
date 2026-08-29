import os

from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

AI_MODEL_PATH = os.getenv("AI_MODEL_PATH", "yolo26n.pt")
AI_MODEL_VERSION = os.getenv("AI_MODEL_VERSION", "1.0.0")

class AIService:

    def __init__(self):
        model_path = AI_MODEL_PATH

        self.model_version = AI_MODEL_VERSION

        self.model = YOLO(model_path)

    def predict(
        self,
        image_path: str,
        confidence_threshold: float
    ):
        results = self.model(
            image_path,
            conf=confidence_threshold
        )

        predictions = []

        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                coordinates = box.xyxy[0].tolist()

                predictions.append({
                    "class": result.names[class_id],
                    "confidence": round(confidence, 4),
                    "bbox": [
                        round(coordinate, 2)
                        for coordinate in coordinates
                    ]
                })

        return predictions


ai_service = AIService()