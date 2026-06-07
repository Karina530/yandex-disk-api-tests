"""
Позитивные тесты

Метод: DELETE.
Техники тест-дизайна: Contract Testing, Chained Operations, Dependent Operations.
"""

import time
import pytest

# DELETE /v1/disk/resources

@pytest.mark.positive
class TestDeleteResource:
    """Happy Path для DELETE /v1/disk/resources"""

    def test_delete_existing_folder_returns_success(self, client, trashable_folder):
        """Удаление существующей папки: 200, 202 или 204"""
        response = client.delete_resource(trashable_folder)
        assert response.status_code in [200, 202, 204], (
            f"Статус удаления: {response.status_code}"
        )

    def test_deleted_folder_is_gone(self, client, trashable_folder):
        """Проверка цепочки: DELETE -> GET -> 404."""
        client.delete_resource(trashable_folder)
        time.sleep(1)

        response = client.get_resources(trashable_folder)
        assert response.status_code == 404, (
            f"Папка не удалена, статус: {response.status_code}"
        )

    def test_delete_non_empty_folder(self, client, test_folder, test_file_url):
        """Удаление папки с файлом внутри"""
        client.upload_file_by_url(
            path=f"{test_folder}/inside.txt", url=test_file_url
        )
        time.sleep(3)

        response = client.delete_resource(test_folder)
        assert response.status_code in [200, 202, 204], (
            f"Удаление непустой папки: статус {response.status_code}"
        )

        time.sleep(2)
        check = client.get_resources(test_folder)
        assert check.status_code == 404, f"Папка всё ещё существует"

    def test_permanently_true(self, client, trashable_folder):
        """Параметр permanently=true принимается"""
        response = client.delete_resource(trashable_folder, permanently="true")
        assert response.status_code in [200, 202, 204]

    def test_force_async_true(self, client, test_folder, test_file_url):
        """Асинхронное удаление непустой папки"""
        client.upload_file_by_url(
            path=f"{test_folder}/async_file.txt", url=test_file_url
        )
        time.sleep(3)

        response = client.delete_resource(test_folder, force_async="true")
        assert response.status_code in [200, 202], (
            f"Асинхронное удаление: статус {response.status_code}"
        )

        time.sleep(3)
        check = client.get_resources(test_folder)
        assert check.status_code == 404, "Папка не удалилась асинхронно"

    def test_fields_parameter_on_delete(self, client, trashable_folder):
        """Параметр fields при удалении принимается"""
        response = client.delete_resource(trashable_folder, fields="name,path")
        assert response.status_code in [200, 202, 204]

    def test_delete_single_file(self, client, test_folder, file_in_folder):
        """Удаление отдельного файла (не папки)"""
        time.sleep(3)

        response = client.delete_resource(file_in_folder)
        assert response.status_code in [200, 202, 204], (
            f"Удаление файла: статус {response.status_code}"
        )

        time.sleep(1)
        check = client.get_resources(file_in_folder)
        assert check.status_code == 404, "Файл всё ещё существует"

        

    