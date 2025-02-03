import pytest
from httpx import AsyncClient


async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/registration",
        json={
            "nickname": "test_user_1",
            "email": "user_1@example.com",
            "phoneNumber": "79990001122",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 201


async def test_register_with_used_nickname(client: AsyncClient):
    response = await client.post(
        "/api/v1/registration",
        json={
            "nickname": "used_nickname",
            "email": "user_2@example.com",
            "phoneNumber": "78901234567",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 409


async def test_register_with_used_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/registration",
        json={
            "nickname": "test_user_2",
            "email": "used_email@mail.com",
            "phoneNumber": "78901234567",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 409


async def test_register_with_used_phone(client: AsyncClient):
    response = await client.post(
        "/api/v1/registration",
        json={
            "nickname": "test_user_2",
            "email": "user_2@mail.com",
            "phoneNumber": "78005553535",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    "invalid_password", ("1!aA", "password1!", "PASSWORD1!", "Password1", "Password!")
)
async def test_register_with_invalid_password(client: AsyncClient, invalid_password):
    response = await client.post(
        "/api/v1/registration",
        json={
            "nickname": "test_user_2",
            "email": "user_2@mail.com",
            "phoneNumber": "71234567890",
            "password": invalid_password,
        },
    )
    assert response.status_code == 422
