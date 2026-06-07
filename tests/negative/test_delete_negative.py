
# ================================================================
# DELETE /v1/disk/resources — негативные
# ================================================================
"""
Негативные тесты (Error Path) для Яндекс.Диск API.

Метод: GET.
Техники тест-дизайна: Pairwise Testing, классы эквивалентности,
анализ граничных значений, проверка отсутствия обязательных параметров,
проверка дублирования, невалидные типы данных.
"""

import time
import pytest
@pytest.mark.negative
class TestDeleteResourceNegative:
    """
    DELETE /v1/disk/resources.
    Техники: классы эквивалентности (path),
    невалидные boolean-флаги.
    """

    def test_delete_nonexistent_returns_404(self, client):
        """
        Класс эквивалентности: несуществующий ресурс.
        Документация: 404 Not Found.
        """
        response = client.delete_resource("/nonexistent_resource_42_xyz")
        assert response.status_code == 404, (
            f"Несуществующий ресурс: статус {response.status_code}"
        )

    @pytest.mark.parametrize("path,expected,desc", [
        ("", 400, "пустой path"),
    ])
    def test_invalid_path_returns_400(self, client, path, expected, desc):
        """
        Отсутствие обязательного параметра path.
        """
        response = client.delete_resource(path)
        assert response.status_code == expected, (
            f"'{desc}': ожидался {expected}, получен {response.status_code}"
        )

    @pytest.mark.parametrize("param,value,desc", [
        ("permanently", "yes", "permanently='yes'"),
        ("force_async", "now", "force_async='now'"),
        ("permanently", "", "permanently=''"),
        ("force_async", "123", "force_async='123'"),
    ])
    def test_invalid_flag_values(self, client, trashable_folder, param, value, desc):
        """
        Классы эквивалентности: некорректные boolean-флаги.
        API может принять (200/202/204) или отклонить (400).
        """
        kwargs = {"path": trashable_folder, param: value}
        response = client.delete_resource(**kwargs)
        assert response.status_code in [200, 202, 204, 400], (
            f"'{desc}': статус {response.status_code}"
        )
        # Очистка если не удалилась
        time.sleep(1)
        if client.get_resources(trashable_folder).status_code == 200:
            client.delete_resource(trashable_folder)

    def test_delete_with_invalid_fields(self, client, trashable_folder):
        """Невалидное значение fields."""
        response = client.delete_resource(
            trashable_folder, fields="nonexistent_xyz"
        )
        assert response.status_code in [200, 202, 204, 400], (
            f"fields=nonexistent: статус {response.status_code}"
        )
        time.sleep(1)
        if client.get_resources(trashable_folder).status_code == 200:
            client.delete_resource(trashable_folder)