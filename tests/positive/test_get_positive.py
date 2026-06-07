"""
Позитивные тесты

Метод: GET.
Техники тест-дизайна: Contract Testing, классы эквивалентности,
граничные значения, Chained Operations.
"""

import time
import pytest



# GET /v1/disk


@pytest.mark.positive
class TestGetDiskInfo:
    """Happy Path для GET /v1/disk"""

    def test_status_200_and_required_keys(self, client):
        """Обязательные поля ответа"""
        response = client.get_disk_info()
        assert response.status_code == 200

        required = [
            "total_space", "used_space", "trash_size",
            "system_folders", "unlimited_autoupload_enabled"
        ]
        data = response.json()
        for field in required:
            assert field in data, f"Поле '{field}' отсутствует в ответе"

    def test_total_space_positive(self, client):
        """Граничные значения: total_space > 0."""
        total = client.get_disk_info().json()["total_space"]
        assert isinstance(total, int), f"total_space не int, а {type(total)}"
        assert total > 0, f"total_space = {total}, ожидалось > 0"

    def test_fields_parameter_filters_response(self, client):
        """Параметр fields возвращает только запрошенные поля"""
        requested = ["total_space", "used_space", "trash_size"]
        response = client.get_disk_info(fields=",".join(requested))
        assert response.status_code == 200

        data = response.json()
        for field in requested:
            assert field in data, f"Поле '{field}' отсутствует в ответе с fields"



# GET /v1/disk/resources


@pytest.mark.positive
class TestGetResources:
    """Happy Path для GET /v1/disk/resources"""

    def test_root_has_embedded_items(self, client):
        """Корень диска содержит _embedded.items."""
        response = client.get_resources("/")
        assert response.status_code == 200

        data = response.json()
        assert "_embedded" in data, "Ответ не содержит _embedded"
        assert "items" in data["_embedded"], "Ответ не содержит items"

    def test_created_folder_is_visible(self, client, test_folder):
        """Проверка цепочки операций: PUT -> GET."""
        response = client.get_resources(test_folder)
        assert response.status_code == 200
        assert response.json()["type"] == "dir", "Созданный объект не является папкой"

    def test_limit_restricts_count(self, client):
        """Граничные значения: limit=1 -> не более 1 элемента"""
        response = client.get_resources("/", limit=1)
        assert response.status_code == 200

        items = response.json()["_embedded"]["items"]
        assert len(items) <= 1, f"limit=1, но получено {len(items)} элементов"
    def test_sort_by_name_ascending(self, client, test_folder):
        """Параметр sort=name: проверяем сортировку по возрастанию"""
        time.sleep(5)

        response = client.get_resources(test_folder, sort="name")
        assert response.status_code == 200

        items = response.json()["_embedded"]["items"]
        names = [item["name"] for item in items]
        assert names == sorted(names), (
            f"Сортировка нарушена. Получено: {names}, ожидалось: {sorted(names)}"
        )
    def test_sort_by_created(self, client, test_folder):
        """Параметр sort=created: запрос проходит успешно"""
        time.sleep(5)

        response = client.get_resources(test_folder, sort="created")
        assert response.status_code == 200

    

    


    

    def test_fields_limits_response(self, client, test_folder):
        """Параметр fields: в ответе только запрошенные поля"""
        response = client.get_resources(test_folder, fields="name,type")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data, f"Поле 'name' отсутствует. Ответ: {data}"
        assert "type" in data, f"Поле 'type' отсутствует. Ответ: {data}"

    def test_all_files_visible_in_folder(self, client, test_folder, multiple_files_in_folder):
        """Все загруженные файлы видны через GET /resources"""
        time.sleep(5)

        response = client.get_resources(test_folder)
        assert response.status_code == 200

        items = response.json()["_embedded"]["items"]
        names = [item["name"] for item in items]

        expected = ["file_0.txt", "file_1.txt", "file_2.txt"]
        for name in expected:
            assert name in names, f"Файл '{name}' не найден. Файлы в папке: {names}"

        assert len(items) == 3, f"Ожидалось 3 файла, получено {len(items)}: {names}"

    
        

# GET /v1/disk/resources/files


@pytest.mark.positive
class TestGetFlatResources:
    """Happy Path для GET /v1/disk/resources/files"""

    def test_returns_items_list(self, client):
        """Базовый запрос возвращает список items."""
        response = client.get_flat_resources()
        assert response.status_code == 200
        assert "items" in response.json(), "Ответ не содержит 'items'"

    def test_limit_parameter(self, client):
        """Граничные значения: limit=3"""
        response = client.get_flat_resources(limit=3)
        assert response.status_code == 200
        assert len(response.json()["items"]) <= 3

    

    def test_media_type_image_filter(self, client):
        """
        Класс эквивалентности: media_type=image
        Все элементы должны быть изображениями
        """
        response = client.get_flat_resources(media_type="image")
        assert response.status_code == 200

        for item in response.json()["items"]:
            mime = item.get("mime_type", "")
            is_image = (
                item.get("media_type") == "image"
                or mime.startswith("image/")
            )
            assert is_image, f"'{item['name']}' не является изображением"

    def test_media_type_video_filter(self, client):
        """Фильтр media_type=video принимается API"""
        response = client.get_flat_resources(media_type="video")
        assert response.status_code == 200

    def test_media_type_audio_filter(self, client):
        """Фильтр media_type=audio принимается API"""
        response = client.get_flat_resources(media_type="audio")
        assert response.status_code == 200

    def test_sort_by_name(self, client):
        """Сортировка по имени: проверяем порядок"""
        response = client.get_flat_resources(sort="name")
        assert response.status_code == 200

        items = response.json()["items"]
        names = [item["name"] for item in items]
        assert names == sorted(names), (
            f"Сортировка нарушена: {names} != {sorted(names)}"
        )

    def test_fields_parameter(self, client):
        """Параметр fields ограничивает набор полей"""
        response = client.get_flat_resources(limit=1, fields="name,type,size")
        assert response.status_code == 200

        items = response.json()["items"]
        if items:
            item = items[0]
            assert "name" in item, "Поле 'name' отсутствует"
            assert "type" in item, "Поле 'type' отсутствует"
            assert "size" in item, "Поле 'size' отсутствует"



# GET /v1/disk/resources/upload


@pytest.mark.positive
class TestGetUploadLink:
    """Happy Path для GET /v1/disk/resources/upload"""

    def test_returns_href(self, client):
        """Ответ содержит ссылку для загрузки"""
        response = client.get_upload_link("/test_upload.txt")
        assert response.status_code == 200
        assert "href" in response.json(), "Ответ не содержит 'href'"

    def test_overwrite_true(self, client):
        """Параметр overwrite=true принимается"""
        response = client.get_upload_link("/test_overwrite.txt", overwrite="true")
        assert response.status_code == 200
        assert "href" in response.json()

    def test_overwrite_false(self, client):
        """Параметр overwrite=false принимается"""
        response = client.get_upload_link("/test_no_overwrite.txt", overwrite="false")
        assert response.status_code == 200
        assert "href" in response.json()

    def test_fields_parameter(self, client):
        """Параметр fields фильтрует ответ"""
        response = client.get_upload_link("/test_fields.txt", fields="href,method")
        assert response.status_code == 200

        data = response.json()
        assert "href" in data, "Поле 'href' отсутствует"
        assert "method" in data, "Поле 'method' отсутствует"



# GET /v1/disk/operations/{operation_id}


@pytest.mark.positive
class TestGetOperationStatus:
    """Happy Path для отслеживания статуса операции"""

    def test_tracks_copy_operation(self, client, test_folder):
        """
        Проверка цепочки: Copy -> operation_id -> статус операции.
        Учитываем, что статус может быть уже недоступен (404).
        """
        copy_path = f"{test_folder}_copy_for_status"
        client.delete_resource(copy_path)
        time.sleep(1)

        try:
            response = client.copy_resource(from_path=test_folder, path=copy_path)
            assert response.status_code in [200, 201, 202], (
                f"Копирование не удалось: {response.status_code}"
            )

            time.sleep(2)
            check = client.get_resources(copy_path)
            assert check.status_code == 200, "Копия не была создана"
            data = response.json()
            if "href" in data:
                href = data["href"]
                operation_id = href.rstrip("/").split("/")[-1]

                status_response = client.get_operation_status(operation_id)

                assert status_response.status_code in [200, 404], (
                    f"Неожиданный статус операции: {status_response.status_code}"
                )
        finally:
            client.delete_resource(copy_path)
    
    def test_offset_works_with_limit(self, client, test_folder, multiple_files_in_folder):
        """Параметр offset смещает выдачу"""
        time.sleep(10)

        page1 = client.get_resources(test_folder, limit=1, offset=0)
        page2 = client.get_resources(test_folder, limit=1, offset=1)

        items1 = page1.json()["_embedded"]["items"]
        items2 = page2.json()["_embedded"]["items"]

        if items1 and items2:
            assert items1[0]["name"] != items2[0]["name"], (
                f"offset не работает: оба запроса вернули '{items1[0]['name']}'"
            )
        else:
            pytest.skip("Недостаточно файлов для проверки offset")