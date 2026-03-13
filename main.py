import uvicorn

from service import create_app
from service.config import get_settings

app = create_app()

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        ssl_certfile=settings.ssl_cert,
        ssl_keyfile=settings.ssl_key,
    )
