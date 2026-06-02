from fastapi import FastAPI
from api.routers.file_upload.handle_file_upload import upload_file_router
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI(debug=True)

allowed_origins = os.getenv(
    "CORS_ORIGINS",
    "http://localhost,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(upload_file_router)

if __name__ == "__main__":
    # CRITICAL FIX: Must default to "0.0.0.0" in container environments
    # to let Hugging Face pass incoming traffic through.
    host = os.getenv("HOST", "0.0.0.0")

    # Hugging Face will automatically inject PORT=7860 into your environment variables,
    # falling back to 8000 locally.
    port = int(os.getenv("PORT", "8000"))

    # Production Notice: Turn reload off in production for better performance
    is_debug = os.getenv("ENVIRONMENT", "development").lower() == "development"

    uvicorn.run("main:app", host=host, port=port, reload=is_debug)