"""
Негативные тесты (Error Path) для Яндекс.Диск API.

Метод: POST.
Техники тест-дизайна: Pairwise Testing, классы эквивалентности,
анализ граничных значений, проверка отсутствия обязательных параметров,
проверка дублирования, невалидные типы данных.
"""

import time
import pytest

# POST /v1/disk/resources/upload — негативные


@pytest.mark.negative
class TestUploadFileByUrlNegative:
    """
    POST /v1/disk/resources/upload.
    Техника: Pairwise Testing для комбинаций path × url.
    """

    VALID_URL = "https://raw.githubusercontent.com/pytest-dev/pytest/main/README.rst"

    @pytest.mark.parametrize("path,url,expected,desc", [
        # Пустой URL
        ("/test.txt", "", 400, "пустой URL"),
        # Пустой path
        ("", VALID_URL, 400, "пустой path"),
        # Невалидный URL — нет протокола
        ("/test.txt", "not-a-url", 400, "строка вместо URL"),
        # Неподдерживаемый протокол
        ("/test.txt", "ftp://server/file.txt", 400, "FTP протокол"),
        # Оба параметра пустые
        ("", "", 400, "оба параметра пустые"),
    ])
    def test_invalid_path_url_combinations(self, client, path, url, expected, desc):
        """
        Pairwise Testing: покрываем основные негативные сочетания
        обязательных параметров path и url.
        """
        response = client.upload_file_by_url(path=path, url=url)
        if isinstance(expected, list):
            assert response.status_code in expected, (
                f"'{desc}': статус {response.status_code} не входит в {expected}"
            )
        else:
            assert response.status_code == expected, (
                f"'{desc}': ожидался {expected}, получен {response.status_code}"
            )

    @pytest.mark.parametrize("param,value,desc", [
        ("disable_redirects", "yes_please", "disable_redirects=строка"),
        ("fields", "color,flavor", "fields=несуществующие поля"),
    ])
    def test_invalid_optional_params(self, client, test_folder, param, value, desc):
        """
        Классы эквивалентности для необязательных параметров.
        """
        kwargs = {
            "path": f"{test_folder}/test.txt",
            "url": self.VALID_URL,
            param: value
        }
        response = client.upload_file_by_url(**kwargs)
        assert response.status_code in [201, 202, 400], (
            f"'{desc}': статус {response.status_code}"
        )
    def test_missing_required_param_url(self):
        """
        Проверка отсутствия обязательного параметра url.
        Ожидаем 400 Bad Request.
        """
        import requests
        from config import Config

        response = requests.post(
            f"{Config.BASE_URL}/resources/upload",
            headers={"Authorization": f"OAuth {Config.TOKEN}"},
            params={"path": "/test.txt"}
        )
        assert response.status_code == 400, (
            f"Без url: статус {response.status_code}"
        )
    
    def test_missing_required_param_path(self, client):
        """Отсутствие path -> 400."""
        import requests
        from config import Config

        response = requests.post(
            f"{Config.BASE_URL}/resources/upload",
            headers={"Authorization": f"OAuth {Config.TOKEN}"},
            params={"url": self.VALID_URL}
        )
        assert response.status_code == 400, (
            f"Без path: статус {response.status_code}"
        )


# POST /v1/disk/resources/copy — негативные


@pytest.mark.negative
class TestCopyResourceNegative:
    """
    POST /v1/disk/resources/copy.
    Техники: классы эквивалентности, проверка дублирования,
    отсутствие обязательных параметров.
    """

    def test_copy_nonexistent_source_returns_404(self, client):
        """
        Класс эквивалентности: несуществующий from_path.
        Документация: 404 Not Found.
        """
        response = client.copy_resource(
            from_path="/nonexistent_source_12345_xyz", path="/dest"
        )
        assert response.status_code == 404, (
            f"Несуществующий источник: статус {response.status_code}"
        )
    
    def test_copy_to_existing_without_overwrite_returns_409(self, client, test_folder):
        """
        Проверка дублирования: копирование в существующий путь без overwrite.
        Документация: 409 Conflict.
        """
        response = client.copy_resource(from_path=test_folder, path=test_folder)
        assert response.status_code == 409, (
            f"Копирование в себя: статус {response.status_code}"
        )
        

    @pytest.mark.parametrize("from_path,path,expected,desc", [
        ("", "/dest", 400, "пустой from_path"),
        ("/source", "", 400, "пустой path"),
        ("", "", 400, "оба параметра пустые"),
    ])
    def test_empty_required_params(self, client, from_path, path, expected, desc):
        """
        Классы эквивалентности: пустые значения обязательных параметров.
        Документация: 400 Bad Request.
        """
        response = client.copy_resource(from_path=from_path, path=path)
        assert response.status_code == expected, (
            f"'{desc}': ожидался {expected}, получен {response.status_code}"
        )
