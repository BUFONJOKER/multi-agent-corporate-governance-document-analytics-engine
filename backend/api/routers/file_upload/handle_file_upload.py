import os
import shutil
from fastapi import UploadFile, File, HTTPException, APIRouter, status

upload_file_router = APIRouter(prefix="/upload")

UPLOAD_DIR = "./uploads"
# Define a 10MB limit (in bytes)
MAX_FILE_SIZE = 10 * 1024 * 1024
# Create the upload directory if it does not exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


@upload_file_router.post("/file")
async def handle_file_upload(
    file: UploadFile = File(
        ..., description="**Allowed types:** PDF, CSV, DOCX, XLSX.<br>**Max size:** 10MB."
    )
):
    # 1. Option to validate file type extension
    allowed_extensions = ["pdf", "csv", "docx", "xlsx"]
    file_ext = file.filename.split(".")[-1]

    if file_ext.lower() not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Extension not allowed")

    if file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds limit",
        )

    # 2. Define the absolute destination path
    destination_path = os.path.join(UPLOAD_DIR, file.filename)

    # 3. Stream content cleanly into a local target file
    with open(destination_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "status": "Successfully uploaded"}
