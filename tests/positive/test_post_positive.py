"""
Позитивные тесты

Методы: POST.
Техники тест-дизайна: Contract Testing, классы эквивалентности,
граничные значения, проверка цепочки операций.
"""

import time
import uuid
import pytest


# POST /v1/disk/resources/upload


@pytest.mark.positive
class TestUploadFileByUrl:
    """Happy Path для POST /v1/disk/resources/upload"""

    def test_upload_returns_accepted(self, client, test_folder, test_file_url):
        time.sleep(5)
        """Загрузка возвращает 201 или 202."""
        response = client.upload_file_by_url(
            path=f"{test_folder}/test_{uuid.uuid4().hex}.txt", url=test_file_url
        )
        assert response.status_code in [201, 202], (
            f"Статус загрузки: {response.status_code}"
        )

    def test_uploaded_file_visible_in_folder(self, client, test_folder, test_file_url):
        """Проверка цепочки: Upload -> GET /resources -> файл виден."""

        check = client.get_resources(test_folder)
        if check.status_code != 200:
            client.create_folder(test_folder)
        
        client.upload_file_by_url(
            path=f"{test_folder}/visible.txt", url=test_file_url
        )
        time.sleep(8)

        response = client.get_resources(test_folder)
        assert response.status_code == 200, (
            f"Папка {test_folder} недоступна: {response.status_code}"
        )

        names = [item["name"] for item in response.json()["_embedded"]["items"]]
        assert "visible.txt" in names, (
            f"Файл 'visible.txt' не найден. Файлы: {names}"
        )

    
    def test_fields_parameter(self, client, test_folder, test_file_url):
        """Параметр fields при загрузке принимается."""
        check = client.get_resources(test_folder)
        if check.status_code != 200:
            client.create_folder(test_folder)
        response = client.upload_file_by_url(
            path=f"{test_folder}/fields_{int(time.time())}.txt",
            url=test_file_url,
            fields="name,size,created"
        )
        assert response.status_code in [201, 202]


# POST /v1/disk/resources/copy


@pytest.mark.positive
class TestCopyResource:
    """Happy Path для POST /v1/disk/resources/copy."""

    def test_copy_creates_duplicate(self, client, test_folder):
        """Копирование создаёт дубликат папки"""
        copy_path = f"{test_folder}_copy"
        client.delete_resource(copy_path)
        time.sleep(1)  

        try:
            response = client.copy_resource(from_path=test_folder, path=copy_path)
            assert response.status_code in [200, 201, 202], (
                f"Копирование: статус {response.status_code}"
            )

            
            time.sleep(3)

            assert client.get_resources(test_folder).status_code == 200, "Источник недоступен"
            assert client.get_resources(copy_path).status_code == 200, "Копия не создана"
        finally:
            client.delete_resource(copy_path)

    def test_copy_with_overwrite(self, client, test_folder):
        """Копирование с overwrite=true перезаписывает существующий ресурс."""
        copy_path = f"{test_folder}_overwrite"
        client.delete_resource(copy_path)

        client.copy_resource(from_path=test_folder, path=copy_path)
        time.sleep(2)

        response = client.copy_resource(
            from_path=test_folder, path=copy_path, overwrite="true"
        )
        assert response.status_code in [200, 201, 202], (
            f"Overwrite: статус {response.status_code}, ответ: {response.json()}"
        )

        client.delete_resource(copy_path)

    def test_copy_with_fields(self, client, test_folder):
        """Параметр fields при копировании принимается."""
        copy_path = f"{test_folder}_fields"
        client.delete_resource(copy_path)
        time.sleep(5)

        response = client.copy_resource(
            from_path=test_folder, path=copy_path, fields="name,type,created"
        )
        assert response.status_code in [200, 201, 202]

        client.delete_resource(copy_path)

    def test_copy_file(self, client, test_folder, file_in_folder):
        """Копирование отдельного файла."""
        time.sleep(3)

        copy_path = f"{test_folder}/copied_file.txt"
        client.delete_resource(copy_path)

        response = client.copy_resource(from_path=file_in_folder, path=copy_path)
        assert response.status_code in [200, 201, 202]

        assert client.get_resources(copy_path).status_code == 200, "Копия файла не создана"
