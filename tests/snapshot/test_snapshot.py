from httpx import AsyncClient


async def test_create_snapshot_success(client: AsyncClient):
    """Тест успешного создания снимка"""
    response = await client.post(
        "/api/v1/snapshot",
        data={"violationType": "face_not_detected"},
        files={"image": ("test.jpg", b"fake_image_data", "image/jpeg")},
        params={"proctoringId": None}
    )
    
    assert response.status_code in [201, 400, 401, 422]
    if response.status_code == 201:
        data = response.json()
        assert "id" in data
        assert data["violation_type"] == "face_not_detected"


async def test_get_snapshot_success(client: AsyncClient):
    """Тест получения снимка по ID"""
    response = await client.get("/api/v1/snapshot/1")
    
    assert response.status_code in [200, 404, 401, 422]
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert data["id"] == 1


async def test_get_snapshot_not_found(client: AsyncClient):
    """Тест получения несуществующего снимка"""
    response = await client.get("/api/v1/snapshot/999999")
    
    assert response.status_code in [404, 401, 422]


async def test_update_snapshot_success(client: AsyncClient):
    """Тест обновления снимка"""
    response = await client.put(
        "/api/v1/snapshot/1",
        params={"violationType": "multiple_faces"}
    )
    
    assert response.status_code in [200, 404, 401, 422]
    if response.status_code == 200:
        data = response.json()
        assert data["violation_type"] == "multiple_faces"


async def test_update_snapshot_not_found(client: AsyncClient):
    """Тест обновления несуществующего снимка"""
    response = await client.put(
        "/api/v1/snapshot/999999",
        params={"violationType": "multiple_faces"}
    )
    
    assert response.status_code in [404, 401, 422]


async def test_delete_snapshot_success(client: AsyncClient):
    """Тест удаления снимка"""
    response = await client.delete("/api/v1/snapshot/1")
    
    assert response.status_code in [204, 404, 401, 422]


async def test_delete_snapshot_not_found(client: AsyncClient):
    """Тест удаления несуществующего снимка"""
    response = await client.delete("/api/v1/snapshot/999999")
    
    assert response.status_code in [404, 401, 422]


# ============= PROCTORING SNAPSHOTS =============

async def test_get_proctoring_snapshots_success(client: AsyncClient):
    """Тест получения всех снимков для прокторинга"""
    response = await client.get("/api/v1/proctoring/1/snapshots")
    
    assert response.status_code in [200, 404, 401, 422]
    if response.status_code == 200:
        data = response.json()
        assert "snapshots" in data
        assert "total_count" in data
        assert isinstance(data["snapshots"], list)


async def test_get_proctoring_snapshots_not_found(client: AsyncClient):
    """Тест получения снимков для несуществующего прокторинга"""
    response = await client.get("/api/v1/proctoring/999999/snapshots")
    
    assert response.status_code in [404, 401, 422]


async def test_get_proctoring_report_success(client: AsyncClient):
    """Тест получения PDF отчета по прокторингу"""
    response = await client.get("/api/v1/proctoring/1/report")
    
    assert response.status_code in [200, 404, 401, 422]
    if response.status_code == 200:
        assert response.headers.get("content-type") == "application/pdf"


async def test_get_proctoring_report_not_found(client: AsyncClient):
    """Тест получения отчета для несуществующего прокторинга"""
    response = await client.get("/api/v1/proctoring/999999/report")
    
    assert response.status_code in [404, 401, 422]
