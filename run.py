import os
import uvicorn
from src.main import app

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8888"))
    uvicorn.run(app, host=host, port=port)
