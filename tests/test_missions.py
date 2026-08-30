from fastapi.testclient import TestClient


def _create_mission(
    client: TestClient,
    auth_headers: dict[str, str],
    payload: dict,
):
    response = client.post("/missions/", json=payload, headers=auth_headers)
    assert response.status_code == 201
    return response.json()


def test_create_mission_with_valid_data(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    body = _create_mission(client, auth_headers, mission_payload)

    assert body["id"] >= 1
    assert body["name"] == mission_payload["name"]
    assert body["status"] == mission_payload["status"]
    assert body["drone_model"] == mission_payload["drone_model"]
    assert body["image_count"] == mission_payload["image_count"]
    assert body["area_hectares"] == mission_payload["area_hectares"]
    assert "created_at" in body


def test_list_missions(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    _create_mission(client, auth_headers, mission_payload)
    second = {**mission_payload, "name": "Mission Beta"}
    _create_mission(client, auth_headers, second)

    response = client.get("/missions/", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_existing_mission_by_id(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    created = _create_mission(client, auth_headers, mission_payload)

    response = client.get(f"/missions/{created['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["name"] == mission_payload["name"]


def test_get_nonexistent_mission_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.get("/missions/999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Mission not found"


def test_update_existing_mission(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    created = _create_mission(client, auth_headers, mission_payload)
    updated_payload = {
        **mission_payload,
        "name": "Mission Updated",
        "status": "completed",
        "image_count": 20,
    }

    response = client.put(
        f"/missions/{created['id']}",
        json=updated_payload,
        headers=auth_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Mission Updated"
    assert body["status"] == "completed"
    assert body["image_count"] == 20


def test_update_nonexistent_mission_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    response = client.put(
        "/missions/999",
        json=mission_payload,
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Mission not found"


def test_delete_existing_mission(
    client: TestClient,
    auth_headers: dict[str, str],
    mission_payload: dict,
):
    created = _create_mission(client, auth_headers, mission_payload)

    response = client.delete(f"/missions/{created['id']}", headers=auth_headers)

    assert response.status_code == 204

    follow_up = client.get(f"/missions/{created['id']}", headers=auth_headers)
    assert follow_up.status_code == 404


def test_delete_nonexistent_mission_returns_404(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.delete("/missions/999", headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Mission not found"


def test_create_mission_rejects_invalid_payload(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.post(
        "/missions/",
        json={
            "name": "ab",
            "status": "",
            "drone_model": "x",
            "image_count": -1,
            "area_hectares": 0,
        },
        headers=auth_headers,
    )

    assert response.status_code == 422
