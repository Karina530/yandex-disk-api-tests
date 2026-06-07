class Config:
    BASE_URL = "https://cloud-api.yandex.net/v1/disk"
    TOKEN = "y0__wgBEMC75fYGGNuWAyCVx-3pFzCx6_nQCFeM-kftXKdiLpFb74lTC84s5s-V"
    
    HEADERS = {
        "Authorization": f"OAuth {TOKEN}",
        "Content-Type": "application/json"
    }