"""
Позитивные тесты

Метод: PUT.
Техники тест-дизайна: классы эквивалентности, Happy Path, Chained Operations.
"""


import pytest




# PUT /v1/disk/resources


@pytest.mark.positive
class TestCreateFolder:
    """Happy Path для PUT /v1/disk/resources."""

    def test_create_new_folder_returns_success(self, client):
        """Создание новой папки: 200 или 201."""
        folder = "/test_put_positive_unique"
        client.delete_resource(folder)

        response = client.create_folder(folder)
        assert response.status_code in [200, 201], (
            f"Статус создания папки: {response.status_code}"
        )

        client.delete_resource(folder)

    def test_created_folder_exists_with_type_dir(self, client, test_folder):
        """Проверка цепочки: PUT → GET. Папка создана и имеет type='dir'."""
        response = client.get_resources(test_folder)
        assert response.status_code == 200
        assert response.json()["type"] == "dir", "Тип созданного ресурса не 'dir'"

    
    def test_get_folder_with_fields(self, client, test_folder):
        """GET с параметром fields для существующей папки."""
        response = client.get_resources(test_folder, fields="name,type,created")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data, f"Поле 'name' отсутствует. Ответ: {data}"
        assert "type" in data, f"Поле 'type' отсутствует. Ответ: {data}"