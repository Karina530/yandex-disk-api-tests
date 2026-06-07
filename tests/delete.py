import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from api.YandexClient import YandexClient


def clear_everything():
    client = YandexClient()


    print("ПОЛНАЯ ОЧИСТКА ДИСКА")

    response = client.get_resources("/")
    data = response.json()

    if "_embedded" not in data or not data["_embedded"]["items"]:
        print("Диск уже пустой")
        return

    items = data["_embedded"]["items"]
    print(f"\nНайдено элементов: {len(items)}")
    for item in items:
        print(f"  📁 {item['name']} — {item['type']}")

    confirm = input(f"\nУдалить ВСЁ ({len(items)} элементов)? Введи 'yes' для подтверждения: ")

    if confirm != "yes":
        print("Отменено")
        return

    deleted = 0
    failed = 0

    for item in items:
        path = "/" + item["name"]
        try:
            
            response = client.delete_resource(path, force_async="true", permanently="true")
            if response.status_code in [200, 202, 204]:
                print(f" {path}")
                deleted += 1
            else:
                print(f" {path} — статус {response.status_code}")
                failed += 1
        except Exception as e:
            print(f" {path} — ошибка: {e}")
            failed += 1

    print(f"\nРезультат: удалено {deleted}, ошибок {failed}")


if __name__ == "__main__":
    clear_everything()