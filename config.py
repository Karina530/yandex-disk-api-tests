class Config:
    BASE_URL = "https://cloud-api.yandex.net/v1/disk"
    TOKEN = "your_token_here"
    
    HEADERS = {
        "Authorization": f"OAuth {TOKEN}",
        "Content-Type": "application/json"
    }