"""Tests for item CRUD endpoints."""

from fastapi.testclient import TestClient


class TestItemsAPI:
    def test_create_and_list_items(self) -> None:
        from src.main import create_app

        app = create_app()
        with TestClient(app) as client:
            create_response = client.post(
                "/api/v1/items",
                json={"name": "Widget", "description": "A test item"},
            )
            assert create_response.status_code == 201
            created = create_response.json()
            assert created["name"] == "Widget"
            assert created["description"] == "A test item"
            assert "id" in created

            list_response = client.get("/api/v1/items")
            assert list_response.status_code == 200
            items = list_response.json()
            assert len(items) == 1
            assert items[0]["id"] == created["id"]

    def test_get_item_by_id(self) -> None:
        from src.main import create_app

        app = create_app()
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/items",
                json={"name": "Gadget"},
            ).json()

            response = client.get(f"/api/v1/items/{created['id']}")
            assert response.status_code == 200
            assert response.json()["name"] == "Gadget"

    def test_get_item_not_found(self) -> None:
        from src.main import create_app

        app = create_app()
        with TestClient(app) as client:
            response = client.get("/api/v1/items/nonexistent-id")
            assert response.status_code == 404

    def test_update_item(self) -> None:
        from src.main import create_app

        app = create_app()
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/items",
                json={"name": "Old name"},
            ).json()

            response = client.put(
                f"/api/v1/items/{created['id']}",
                json={"name": "New name", "description": "Updated"},
            )
            assert response.status_code == 200
            body = response.json()
            assert body["name"] == "New name"
            assert body["description"] == "Updated"

    def test_delete_item(self) -> None:
        from src.main import create_app

        app = create_app()
        with TestClient(app) as client:
            created = client.post(
                "/api/v1/items",
                json={"name": "To delete"},
            ).json()

            delete_response = client.delete(f"/api/v1/items/{created['id']}")
            assert delete_response.status_code == 204

            get_response = client.get(f"/api/v1/items/{created['id']}")
            assert get_response.status_code == 200

            list_response = client.get("/api/v1/items")
            assert list_response.json() == []

    def test_delete_item_not_found(self) -> None:
        from src.main import create_app

        app = create_app()
        with TestClient(app) as client:
            response = client.delete("/api/v1/items/nonexistent-id")
            assert response.status_code == 404
