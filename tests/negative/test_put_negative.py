"""
Негативные тесты (Error Path) для Яндекс.Диск API.

Метод: PUT.
Техники тест-дизайна: Pairwise Testing, классы эквивалентности,
анализ граничных значений, проверка отсутствия обязательных параметров,
проверка дублирования, невалидные типы данных.
"""

import time
import pytest


# PUT /v1/disk/resources — негативные


@pytest.mark.negative
class TestCreateFolderNegative:
    """
    PUT /v1/disk/resources.
    Техники: классы эквивалентности (path),
    проверка дублирования (409 Conflict).
    """

    def test_create_existing_folder_returns_409(self, client, test_folder):
        """
        Проверка дублирования: создание уже существующей папки.
        Документация: 409 Conflict, DiskPathPointsToExistentDirectoryError.
        """
        response = client.create_folder(test_folder)
        assert response.status_code == 409, (
            f"Дубликат папки: статус {response.status_code}"
        )
        error = response.json().get("error", "")
        assert "DiskPathPointsToExistentDirectoryError" in error, (
            f"Неожиданная ошибка: {error}"
        )

    @pytest.mark.parametrize("path,expected,desc", [
        ("", 400, "пустая строка"),
        ("   ", [201, 404, 409], "только пробелы"),
        ("///", [404, 409], "тройной слеш"),
    ])
    def test_invalid_path_formats(self, client, path, expected, desc):
        """
        Классы эквивалентности: синтаксически некорректные пути.
        """
        response = client.create_folder(path)
        if isinstance(expected, list):
            assert response.status_code in expected, (
                f"'{desc}': статус {response.status_code} не входит в {expected}"
            )
        else:
            assert response.status_code == expected, (
                f"'{desc}': ожидался {expected}, получен {response.status_code}"
            )

    

    def test_create_folder_with_invalid_fields(self, client):
        """Невалидное значение fields."""
        folder = "/test_invalid_fields_put"
        client.delete_resource(folder)
        time.sleep(1)

        response = client.create_folder(folder, fields="color,shape")
        assert response.status_code in [200, 201, 400], (
            f"fields=color,shape: статус {response.status_code}"
        )

        client.delete_resource(folder)
