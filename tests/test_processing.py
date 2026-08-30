from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.processing import ProcessingHistory

PREDICTIONS = [
    {
        "class": "person",
        "confidence": 0.91,
        "bbox": [10.0, 20.0, 30.0, 40.0],
    }
]


def _create_mission(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
) -> dict:
    response = client.post("/missions/", json=mission_payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


def _process(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_id: int,
    confidence_threshold: float = 0.5,
):
    return client.post(
        f"/missions/{mission_id}/process",
        headers=auth_headers,
        files={"image": ("drone.jpg", b"fake-image-bytes", "image/jpeg")},
        data={"confidence_threshold": str(confidence_threshold)},
    )


def test_process_image_for_existing_mission(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    mission = _create_mission(client, auth_headers, mission_payload)

    with patch("app.routes.processing.ai_service") as mock_ai:
        mock_ai.model_version = "1.0.0"
        mock_ai.predict.return_value = PREDICTIONS

        response = _process(client, auth_headers, mission["id"], 0.6)

    assert response.status_code == 200
    body = response.json()
    assert body["mission_id"] == mission["id"]
    assert body["filename"] == "drone.jpg"
    assert body["predictions"] == PREDICTIONS
    mock_ai.predict.assert_called_once()
    assert mock_ai.predict.call_args.args[1] == 0.6


def test_process_nonexistent_mission_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
):
    with patch("app.routes.processing.ai_service") as mock_ai:
        mock_ai.predict.return_value = PREDICTIONS
        response = _process(client, auth_headers, 999)

    assert response.status_code == 404
    assert response.json()["detail"] == "Mission not found"


def test_process_returns_model_version_and_confidence_threshold(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    mission = _create_mission(client, auth_headers, mission_payload)

    with patch("app.routes.processing.ai_service") as mock_ai:
        mock_ai.model_version = "2.3.1"
        mock_ai.predict.return_value = PREDICTIONS
        response = _process(client, auth_headers, mission["id"], 0.8)

    assert response.status_code == 200
    body = response.json()
    assert body["model_version"] == "2.3.1"
    assert body["confidence_threshold"] == 0.8


def test_processing_history_is_created_after_success(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
    db_session: Session,
):
    mission = _create_mission(client, auth_headers, mission_payload)

    with patch("app.routes.processing.ai_service") as mock_ai:
        mock_ai.model_version = "1.0.0"
        mock_ai.predict.return_value = PREDICTIONS
        process_response = _process(client, auth_headers, mission["id"])

    assert process_response.status_code == 200

    db_session.expire_all()
    records = (
        db_session.query(ProcessingHistory)
        .filter(ProcessingHistory.mission_id == mission["id"])
        .all()
    )
    assert len(records) == 1
    assert records[0].status == "success"
    assert records[0].model_version == "1.0.0"

    history_response = client.get(
        f"/missions/{mission['id']}/processing-history",
        headers=auth_headers,
    )
    assert history_response.status_code == 200
    history = history_response.json()
    assert len(history) == 1
    assert history[0]["status"] == "success"
    assert history[0]["predictions"] == PREDICTIONS


def test_inference_error_is_recorded_in_history(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
    db_session: Session,
):
    mission = _create_mission(client, auth_headers, mission_payload)

    with patch("app.routes.processing.ai_service") as mock_ai:
        mock_ai.model_version = "1.0.0"
        mock_ai.predict.side_effect = RuntimeError("inference failed")
        response = _process(client, auth_headers, mission["id"])

    assert response.status_code == 500
    assert response.json()["detail"] == "Error during AI processing"

    db_session.expire_all()
    record = (
        db_session.query(ProcessingHistory)
        .filter(ProcessingHistory.mission_id == mission["id"])
        .one()
    )
    assert record.status == "error"
    assert record.error_message == "inference failed"
    assert record.inference_time is not None


def test_inference_time_is_recorded(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    mission = _create_mission(client, auth_headers, mission_payload)

    with patch("app.routes.processing.ai_service") as mock_ai:
        mock_ai.model_version = "1.0.0"
        mock_ai.predict.return_value = PREDICTIONS
        response = _process(client, auth_headers, mission["id"])

    assert response.status_code == 200
    inference_time = response.json()["inference_time"]
    assert isinstance(inference_time, float)
    assert inference_time >= 0


def test_model_version_is_recorded_in_history(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    mission = _create_mission(client, auth_headers, mission_payload)

    with patch("app.routes.processing.ai_service") as mock_ai:
        mock_ai.model_version = "9.9.9"
        mock_ai.predict.return_value = PREDICTIONS
        _process(client, auth_headers, mission["id"])

    history_response = client.get(
        f"/missions/{mission['id']}/processing-history",
        headers=auth_headers,
    )
    assert history_response.json()[0]["model_version"] == "9.9.9"
