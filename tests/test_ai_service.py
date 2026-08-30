from unittest.mock import MagicMock, patch

import pytest

from app.routes import processing as processing_routes
from app.services.ai_service import AIService
from app.services import ai_service as ai_service_module


def _mock_yolo_result(class_id: int, confidence: float, bbox: list[float], names: dict):
    box = MagicMock()
    box.cls = [class_id]
    box.conf = [confidence]
    xyxy = MagicMock()
    xyxy.tolist.return_value = bbox
    box.xyxy = [xyxy]

    result = MagicMock()
    result.boxes = [box]
    result.names = names
    return result


def test_predict_image_successfully():
    with patch("app.services.ai_service.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.return_value = [
            _mock_yolo_result(0, 0.91, [10.0, 20.0, 30.0, 40.0], {0: "person"})
        ]

        service = AIService()
        predictions = service.predict("image.jpg", 0.5)

    assert len(predictions) == 1
    mock_model.assert_called_once()


def test_predict_returns_expected_format():
    with patch("app.services.ai_service.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.return_value = [
            _mock_yolo_result(1, 0.87654, [1.111, 2.222, 3.333, 4.444], {1: "car"})
        ]

        service = AIService()
        predictions = service.predict("image.jpg", 0.4)

    assert predictions == [
        {
            "class": "car",
            "confidence": 0.8765,
            "bbox": [1.11, 2.22, 3.33, 4.44],
        }
    ]


def test_predict_passes_confidence_threshold_to_model():
    with patch("app.services.ai_service.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.return_value = []

        service = AIService()
        service.predict("image.jpg", 0.75)

    mock_model.assert_called_once_with("image.jpg", conf=0.75)


def test_predict_raises_when_inference_fails():
    with patch("app.services.ai_service.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.side_effect = RuntimeError("yolo failed")

        service = AIService()

        with pytest.raises(RuntimeError, match="yolo failed"):
            service.predict("image.jpg", 0.5)


def test_model_is_loaded_only_once_on_init_and_reused_on_predict():
    with patch("app.services.ai_service.YOLO") as mock_yolo:
        mock_model = MagicMock()
        mock_yolo.return_value = mock_model
        mock_model.return_value = []

        service = AIService()
        service.predict("a.jpg", 0.5)
        service.predict("b.jpg", 0.4)

        assert mock_yolo.call_count == 1
        assert mock_model.call_count == 2


def test_application_uses_single_aiservice_instance():
    assert processing_routes.ai_service is ai_service_module.ai_service
