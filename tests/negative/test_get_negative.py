"""
Негативные тесты (Error Path) для Яндекс.Диск API.

Метод: GET.
Техники тест-дизайна: Pairwise Testing, классы эквивалентности,
анализ граничных значений, проверка отсутствия обязательных параметров,
проверка дублирования, невалидные типы данных.
"""

import time
import pytest



# GET /v1/disk — негативные


@pytest.mark.negative
class TestGetDiskInfoNegative:
    """
    GET /v1/disk.
    Техника: классы эквивалентности для параметра fields.
    """

    @pytest.mark.parametrize("fields,desc", [
        ("nonexistent_field_xyz", "несуществующее поле"),
        ("", "пустая строка"),
        ("   ", "пробелы"),
        ("!@#$%", "спецсимволы"),
    ])
    def test_invalid_fields_values(self, client, fields, desc):
        """
        Классы эквивалентности: некорректные значения fields.
        API должно проигнорировать (200) или вернуть 400.
        """
        response = client.get_disk_info(fields=fields)
        assert response.status_code in [200, 400], (
            f"'{desc}': неожиданный статус {response.status_code}"
        )



# GET /v1/disk/resources — негативные


@pytest.mark.negative
class TestGetResourcesNegative:
    """
    GET /v1/disk/resources.
    Техники: классы эквивалентности (path),
    анализ граничных значений (limit, offset),
    невалидные типы данных (preview_size, sort).
    """

    #path: классы эквивалентности

    @pytest.mark.parametrize("path,expected,desc", [
        ("/nonexistent_resource_12345_xyz", 404, "несуществующий ресурс"),
        ("", 400, "пустая строка"),
    ])
    def test_path_returns_expected_error(self, client, path, expected, desc):
        """
        Классы эквивалентности: невалидный path.
        Пустая строка -> 400, несуществующий -> 404.
        """
        response = client.get_resources(path)
        assert response.status_code == expected, (
            f"'{desc}': ожидался {expected}, получен {response.status_code}"
        )
    @pytest.mark.parametrize("path,desc", [
        ("!@#$%^&*()<>?|", "спецсимволы"),
        ("   ", "только пробелы"),
        ("///", "тройной слеш"),
    ])
    def test_path_special_values(self, client, path, desc):
        """
        Дополнительные негативные варианты для параметра `path`:
        спецсимволы, только пробелы, тройной слеш.
        """
        response = client.get_resources(path)
        assert response.status_code in [200, 400, 404], (
            f"'{desc}': статус {response.status_code}"
        )

     # limit: граничные значения

    @pytest.mark.parametrize("limit,desc", [
        (-1, "отрицательное число"),
        (0, "ноль"),
        ("abc", "строка вместо числа"),
        (5.5, "число с плавающей точкой"),
        (100000, "сверхбольшое значение"),
        ("1; DROP TABLE files;", "SQL-инъекция"),
    ])


    def test_invalid_limit_values(self, client, limit, desc):
        """
        Анализ граничных значений для limit.
        - Отрицательное -> 400 или дефолт
        - Ноль -> 0 элементов
        - Строка -> 400
        - Float -> 400
        - Сверхбольшое -> обрезается или 400
        - SQL-инъекция -> 400
        """
        response = client.get_resources("/", limit=limit)
        assert response.status_code in [200, 400], (
            f"limit={desc}: неожиданный статус {response.status_code}"
        )

     #offset: граничные значения

    @pytest.mark.parametrize("offset,desc", [
        (-5, "отрицательное число"),
        ("xyz", "строка вместо числа"),
        (999999999, "очень большое число"),
    ])
    def test_invalid_offset_values(self, client, offset, desc):
        """
        Анализ граничных значений для offset.
        """
        response = client.get_resources("/", offset=offset)
        assert response.status_code in [200, 400, 500], (
            f"offset={desc}: статус {response.status_code}"
        )

    # ── sort: невалидные значения ──

    @pytest.mark.parametrize("sort,desc", [
        ("color", "несуществующее поле"),
        ("", "пустая строка"),
        ("123", "цифры"),
    ])
    def test_invalid_sort_values(self, client, sort, desc):
        """
        Классы эквивалентности для sort.
        API может проигнорировать (200) или вернуть 400.
        """
        response = client.get_resources("/", sort=sort)
        assert response.status_code in [200, 400], (
            f"sort='{desc}': статус {response.status_code}"
        )

    #preview_size: невалидный формат

    @pytest.mark.parametrize("preview_size,desc", [
        ("BIG", "строка вместо размеров"),
        ("-100x-100", "отрицательные значения"),
        ("0x0", "нулевой размер"),
        ("100", "только одно число"),
    ])
    def test_invalid_preview_size(self, client, preview_size, desc):
        """
        Классы эквивалентности для preview_size.
        """
        response = client.get_resources("/", preview_size=preview_size)
        assert response.status_code in [200, 400], (
            f"preview_size='{desc}': статус {response.status_code}"
        )

    #fields: невалидные значения

    @pytest.mark.parametrize("fields,desc", [
        ("nonexistent_field_xyz", "несуществующее поле"),
        ("", "пустая строка"),
    ])
    def test_invalid_fields_values(self, client, fields, desc):
        response = client.get_resources("/", fields=fields)
        assert response.status_code in [200, 400], (
            f"fields='{desc}': статус {response.status_code}"
        )
