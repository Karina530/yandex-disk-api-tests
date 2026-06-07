import requests
from requests import Response
from config import Config

class YandexClient:
    def __init__(self):
        self.base_url = Config.BASE_URL
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"OAuth {Config.TOKEN}", "Accept": "application/json"}
        )

    
    
    # GET methods
    
    def get_disk_info(self, **kwargs) -> Response:
        """GET /v1/disk - получить информацию о диске"""
        return self.session.get(self.base_url, params=kwargs)
    
    def get_resources(self, path: str, **kwargs) -> Response:
        """GET /v1/disk/resources - получить информацию о ресурсах"""
        return self.session.get(f"{self.base_url}/resources", params={'path': path, **kwargs})
    
    def get_flat_resources(self, **kwargs) -> Response:
        """GET /v1/disk/resources/files - получить список файлов, упорядоченный по имени"""
        return self.session.get(f"{self.base_url}/resources/files", params=kwargs)

    def get_operation_status(self, operation_id: str, **kwargs) -> Response:
        """ GET /v1/disk/operations/{operation_id} - получить статус асинхронной операции"""
        return self.session.get(
            f"{self.base_url}/operations/{operation_id}",
            params=kwargs
        )
    def get_upload_link(self, path: str, **kwargs) -> Response:
        """GET /v1/disk/resources/upload - получить ссылку для прямой загрузки файла"""
        return self.session.get(
            f"{self.base_url}/resources/upload",
            params={'path': path, **kwargs}
        )



    # PUT methods

    def create_folder(self, path: str, **kwargs) -> Response:
        """PUT /v1/disk/resources - создать папку"""
        return self.session.put(
            f"{self.base_url}/resources",
            params={'path': path, **kwargs}
        )
    


    # POST methods

    def upload_file_by_url(self, path: str, url: str, **kwargs) -> Response:
        """ POST /v1/disk/resources/upload - загрузить файл в Диск по URL """
        return self.session.post(
            f"{self.base_url}/resources/upload",
            params={'path': path, 'url': url, **kwargs}
        )

    def copy_resource(self, from_path: str, path: str, **kwargs) -> Response:
        """POST /v1/disk/resources/copy - копировать файл/папку"""
        return self.session.post( 
            f"{self.base_url}/resources/copy", 
            params={
                "from": from_path,
                "path": path,
                **kwargs
            }
        )


    # DELETE methods

    def delete_resource(self, path: str, **kwargs) -> Response:
        """DELETE /v1/disk/resources - удалить файл/папку"""
        return self.session.delete(
            f"{self.base_url}/resources",
            params={'path': path, **kwargs}
        )
    
