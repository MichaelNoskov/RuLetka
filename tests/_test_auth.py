import pytest
from httpx import AsyncClient
from fastapi import status
from unittest.mock import AsyncMock, patch
# from api.app.utils import encode_password, check_password
# from common.core.config import settings
from datetime import datetime

# Assume your FastAPI app instance is imported as `app`
# and router is included in it:
# app.include_router(router, prefix="/auth")


@pytest.mark.asyncio
@patch("app.api.app.auth.router.send_message")
async def test_register_success(mock_send_message, async_client: AsyncClient):
    # Mock the send_message to simulate DB response with user info JSON
    mock_user_id = "123e4567-e89b-12d3-a456-426614174000"
    user_response = {
        'id': mock_user_id,
        'username': "testuser",
        'birthdate': "2000-01-01",
        'description': "Test user"
    }

    mock_send_message.return_value = user_response

    # Prepare registration data
    register_data = {
        "username": "testuser",
        "password": "testpass",
        "email": "test@example.com",
        "birthdate": "2000-01-01",
        "description": "Test user"
    }

    response = await async_client.post("/auth/register", json=register_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "testuser"
    assert "password" in data and data["password"] != "testpass"  # password should be encoded
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
@patch("app.api.app.auth.router.send_message", new_callable=AsyncMock)
async def test_register_user_already_exists(mock_send_message, async_client: AsyncClient):
    # Simulate send_message raising exception indicating user exists
    mock_send_message.side_effect = Exception("User exists")

    register_data = {
        "username": "existinguser",
        "password": "pass123",
        "email": "exist@example.com",
        "birthdate": "1990-05-15",
        "description": "Existing user"
    }

    response = await async_client.post("/auth/register", json=register_data)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Пользователь с таким именем уже существует"

@pytest.mark.asyncio
@patch("app.api.app.auth.router.send_message")
async def test_login_success(mock_send_message, async_client: AsyncClient):
    # Mock user data returned from DB
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    password_plain = "secretpass"
    user = {
        "username": "existinguser",
        "password": "pass123",
        "email": "exist@example.com",
        "birthdate": "1990-05-15",
        "description": "Existing user"
    }
    mock_send_message.return_value = user.model_dump_json()

    login_data = {
        "username": "loginuser",
        "password": password_plain,
    }

    response = await async_client.post(
        "/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "Успешный вход"}

@pytest.mark.asyncio
@patch("app.api.app.auth.router.send_message")
async def test_login_wrong_password(mock_send_message, async_client: AsyncClient):
    user_id = "123e4567-e89b-12d3-a456-426614174000"
    user = {
        "username": "existinguser",
        "password": "pass123",
        "email": "exist@example.com",
        "birthdate": "1990-05-15",
        "description": "Existing user"
    }
    mock_send_message.return_value = user.model_dump_json()

    login_data = {
        "username": "loginuser",
        "password": "wrongpass",
    }

    response = await async_client.post(
        "/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Некорректные учётные данные"

@pytest.mark.asyncio
@patch("app.api.app.auth.router.send_message")
async def test_login_user_not_found(mock_send_message, async_client: AsyncClient):
    # Simulate user not found by raising exception
    mock_send_message.side_effect = Exception("User not found")

    login_data = {
        "username": "nonexistent",
        "password": "any",
    }

    response = await async_client.post(
        "/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Некорректные учётные данные"

@pytest.mark.asyncio
async def test_register_invalid_data(async_client: AsyncClient):
    # Missing required fields or invalid birthdate format
    invalid_data = {
        "username": "user",
        "password": "pass",
        "email": "not-an-email",
        "birthdate": "invalid-date",
        "description": "desc"
    }
    response = await async_client.post("/auth/register", json=invalid_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@pytest.mark.asyncio
async def test_login_missing_fields(async_client: AsyncClient):
    # Missing password field in form data
    login_data = {
        "username": "user",
        # "password" missing
    }
    response = await async_client.post(
        "/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    # FastAPI OAuth2PasswordRequestForm requires both username and password
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
