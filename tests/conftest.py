import os
import sys

import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from api.YandexClient import YandexClient


@pytest.fixture(scope="session")
def client():
    return YandexClient()


@pytest.fixture
def test_folder(client):
    path = "/test_api_folder"
    client.create_folder(path)
    yield path
    client.delete_resource(path)


@pytest.fixture
def file_in_folder(client, test_folder, test_file_url):
    """
    Создаёт один файл внутри test_folder.
    Использует id(test_folder) для уникальности имени.
    """
    file_path = f"{test_folder}/test_file_{id(test_folder)}.txt"
    client.upload_file_by_url(path=file_path, url=test_file_url)
    return file_path

@pytest.fixture
def multiple_files_in_folder(client, test_folder, test_file_url):
    """
    Создаёт несколько файлов внутри test_folder.
    Возвращает список путей к файлам.
    """
    file_paths = []
    for i in range(3):
        file_path = f"{test_folder}/file_{i}.txt"
        client.upload_file_by_url(path=file_path, url=test_file_url)
        file_paths.append(file_path)
    return file_paths


@pytest.fixture
def trashable_folder(client):
    """Создаёт папку, но НЕ удаляет (для тестов удаления)."""
    path = "/test_trashable_folder"
    client.create_folder(path)
    return path




@pytest.fixture
def test_file_url():
    return "https://raw.githubusercontent.com/pytest-dev/pytest/main/README.rst"








def pytest_configure(config):
    config.addinivalue_line("markers", "smoke: быстрая проверка работоспособности")
    config.addinivalue_line("markers", "positive: положительные сценарии")
    config.addinivalue_line("markers", "negative: негативные сценарии")