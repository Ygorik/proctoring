from httpx import AsyncClient


async def test_authorization_with_nickname(client: AsyncClient):
    response = await client.post(
        "/api/v1/authorization",
        json={
            "nickname": "used_nickname",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 200


async def test_authorization_with_email(client: AsyncClient):
    response = await client.post(
        "/api/v1/authorization",
        json={
            "email": "used_email@mail.com",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 200


async def test_authorization_with_phone_number(client: AsyncClient):
    response = await client.post(
        "/api/v1/authorization",
        json={
            "phoneNumber": "78005553535",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 200


async def test_authorization_without_all(client: AsyncClient):
    response = await client.post(
        "/api/v1/authorization",
        json={
            "password": "1234_Test",
        },
    )

    assert response.status_code == 422


async def test_authorization_with_all(client: AsyncClient):
    response = await client.post(
        "/api/v1/authorization",
        json={
            "nickname": "used_nickname",
            "email": "used_email@mail.com",
            "phoneNumber": "78005553535",
            "password": "1234_Test",
        },
    )

    assert response.status_code == 422


async def test_authorization_with_wrong_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/authorization",
        json={
            "nickname": "used_nickname",
            "password": "1234_Test!",
        },
    )

    assert response.status_code == 400


async def test_authorization_with_without_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/authorization",
        json={
            "nickname": "used_nickname",
        },
    )

    assert response.status_code == 422
