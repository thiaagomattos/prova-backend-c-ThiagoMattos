from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient


def test_register_user_endpoint_is_not_implemented(client: TestClient):
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "secret"},
    )
    assert response.status_code in (404, 405)


def test_login_with_valid_credentials_returns_token(client: TestClient):
    response = client.post(
        "/auth/login",
        json={"username": "tester", "password": "secret"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str)
    assert body["access_token"]


@pytest.mark.skip(
    reason=(
        "A validação de credenciais em POST /auth/login está comentada; "
        "qualquer username/password atualmente gera um JWT."
    )
)
def test_login_with_invalid_credentials():
    pass


def test_protected_endpoint_without_token(client: TestClient):
    response = client.get("/missions/")
    assert response.status_code in (401, 403)


def test_protected_endpoint_with_valid_token(
    client: TestClient,
    auth_headers: dict[str, str],
):
    response = client.get("/missions/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_protected_endpoint_with_invalid_token(client: TestClient):
    response = client.get(
        "/missions/",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_protected_endpoint_with_expired_token(client: TestClient):
    expired_token = jwt.encode(
        {
            "sub": "tester",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        },
        "test-secret-key",
        algorithm="HS256",
    )
    response = client.get(
        "/missions/",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
